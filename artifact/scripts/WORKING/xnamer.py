#!/usr/bin/env python3
"""
renamer.py - AI-Powered Media File Renaming with Undo

Uses xAI's Grok-2 Vision to intelligently rename images and videos based on their content.
Generates filenames with 5 words or less, separated by underscores.
Includes undo functionality to restore original filenames.

Usage:
    python renamer.py --dir ./media              # Rename media files in directory
    python renamer.py --file image.jpg           # Rename single image
    python renamer.py --file video.mp4           # Rename single video
    python renamer.py --undo                     # Undo last rename operation
    python renamer.py --undo --all               # Undo all renames

Author: Lucas "Luke" Steuber
"""

import os
import sys
import json
import base64
import argparse
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

try:
    from openai import OpenAI
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
    from rich.table import Table
    from PIL import Image
    import cv2
    import tempfile
except ImportError as e:
    print(f"Missing required package: {e}")
    print("\nInstall required packages with:")
    print("pip install openai rich pillow opencv-python")
    sys.exit(1)

# --- Configuration ---
XAI_API_KEY = "REDACTED_XAI_KEY"
XAI_BASE_URL = "https://api.x.ai/v1"
XAI_MODEL = "grok-2-vision-1212"

# Supported file extensions (images and videos)
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.heic', '.mp4'}

# Log file for undo functionality
RENAME_LOG_FILE = Path.home() / ".image_rename_ai_log.json"

# Initialize rich console
console = Console()

# Initialize OpenAI client for xAI
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url=XAI_BASE_URL,
)


# --- Helper Functions ---

def find_duplicates(files: List[Path]) -> List[Path]:
    """
    Find duplicate files based on size and naming patterns.
    Returns list of files to remove (keeping the first instance).
    """
    duplicates_to_remove = []
    
    # Group by size
    size_groups = defaultdict(list)
    for file_path in files:
        try:
            size = file_path.stat().st_size
            size_groups[size].append(file_path)
        except OSError:
            continue
    
    # Check for exact size matches
    for size, file_list in size_groups.items():
        if len(file_list) > 1:
            # Sort by modification time, keep the oldest
            file_list.sort(key=lambda f: f.stat().st_mtime)
            duplicates_to_remove.extend(file_list[1:])
    
    # Check for numbered duplicates pattern (e.g., file (1).jpg, file (2).jpg)
    duplicate_pattern = re.compile(r'^(.+?)\s*\(\d+\)(\.\w+)$')
    pattern_groups = defaultdict(list)
    
    for file_path in files:
        match = duplicate_pattern.match(file_path.name)
        if match:
            base_name = match.group(1) + match.group(2)
            pattern_groups[base_name].append(file_path)
        else:
            # Check if this is the original file
            potential_base = file_path.name
            pattern_groups[potential_base].append(file_path)
    
    # Find numbered duplicates and mark them for removal
    for base_name, file_list in pattern_groups.items():
        if len(file_list) > 1:
            # Separate original from numbered copies
            original = None
            numbered_copies = []
            
            for file_path in file_list:
                if duplicate_pattern.match(file_path.name):
                    numbered_copies.append(file_path)
                else:
                    if original is None:
                        original = file_path
                    else:
                        # Multiple originals, keep the oldest
                        if file_path.stat().st_mtime < original.stat().st_mtime:
                            numbered_copies.append(original)
                            original = file_path
                        else:
                            numbered_copies.append(file_path)
            
            # Add numbered copies to removal list
            for copy in numbered_copies:
                if copy not in duplicates_to_remove:
                    duplicates_to_remove.append(copy)
    
    return duplicates_to_remove


def deduplicate_files(files: List[Path], dry_run: bool = False) -> List[Path]:
    """
    Remove duplicate files from the list.
    Returns list of remaining files after deduplication.
    """
    if not files:
        return files
    
    console.print("[cyan]Checking for duplicates...[/cyan]")
    
    duplicates = find_duplicates(files)
    
    if not duplicates:
        console.print("[green]No duplicates found[/green]")
        return files
    
    console.print(f"[yellow]Found {len(duplicates)} duplicate file(s):[/yellow]")
    for dup in duplicates:
        console.print(f"  - {dup.name}")
    
    if not dry_run:
        from rich.prompt import Confirm
        if not Confirm.ask("\nRemove these duplicates?"):
            console.print("[yellow]Skipping deduplication[/yellow]")
            return files
    
    if dry_run:
        console.print("[yellow][DRY RUN] Duplicates not actually removed[/yellow]")
        remaining_files = [f for f in files if f not in duplicates]
    else:
        remaining_files = []
        removed_count = 0
        
        for file_path in files:
            if file_path in duplicates:
                try:
                    file_path.unlink()
                    console.print(f"[red]✓ Removed:[/red] {file_path.name}")
                    removed_count += 1
                except Exception as e:
                    console.print(f"[bold red]Error removing {file_path.name}: {e}[/bold red]")
                    remaining_files.append(file_path)  # Keep if removal failed
            else:
                remaining_files.append(file_path)
        
        console.print(f"[green]Removed {removed_count} duplicate file(s)[/green]")
    
    return remaining_files

def load_rename_log() -> Dict:
    """Load the rename log for undo functionality."""
    if RENAME_LOG_FILE.exists():
        with open(RENAME_LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"renames": [], "last_operation": None}


def save_rename_log(log_data: Dict) -> None:
    """Save the rename log to file."""
    log_data["last_updated"] = datetime.now().isoformat()
    with open(RENAME_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)


def extract_video_frame(video_path: Path, frame_position: float = 0.3) -> Optional[Path]:
    """
    Extract a frame from video file at the specified position (0.0 to 1.0).
    Returns path to temporary image file or None on error.
    """
    try:
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            console.print(f"[bold red]Failed to open video: {video_path.name}[/bold red]")
            return None
        
        # Get total frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            console.print(f"[bold red]Unable to determine video length: {video_path.name}[/bold red]")
            cap.release()
            return None
        
        # Calculate frame to extract (30% into the video by default)
        target_frame = int(total_frames * frame_position)
        
        # Seek to target frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        
        # Read the frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            console.print(f"[bold red]Failed to extract frame from video: {video_path.name}[/bold red]")
            return None
        
        # Save frame to temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            temp_path = Path(tmp_file.name)
            cv2.imwrite(str(temp_path), frame)
            
        return temp_path
        
    except Exception as e:
        console.print(f"[bold red]Error extracting frame from {video_path.name}: {e}[/bold red]")
        return None


def get_image_base64(image_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """
    Read and encode image to base64.
    For videos, extracts a frame first.
    Returns (base64_string, mime_type) or (None, None) on error.
    """
    try:
        # Check if it's a video file
        if image_path.suffix.lower() == '.mp4':
            # Extract a frame from the video
            frame_path = extract_video_frame(image_path)
            if not frame_path:
                return None, None
            
            try:
                # Read the extracted frame
                with open(frame_path, 'rb') as img_file:
                    img_data = img_file.read()
                
                encoded = base64.b64encode(img_data).decode('utf-8')
                mime_type = 'jpeg'  # Frame is saved as JPEG
                
                return encoded, mime_type
            finally:
                # Clean up temporary file
                if frame_path.exists():
                    frame_path.unlink()
        else:
            # Handle regular images
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
            
            encoded = base64.b64encode(img_data).decode('utf-8')
            
            # Determine MIME type
            ext = image_path.suffix.lower()
            mime_map = {
                '.jpg': 'jpeg', '.jpeg': 'jpeg',
                '.png': 'png', '.gif': 'gif',
                '.webp': 'webp', '.bmp': 'bmp'
            }
            mime_type = mime_map.get(ext, 'jpeg')
            
            return encoded, mime_type
            
    except Exception as e:
        console.print(f"[bold red]Error encoding file {image_path.name}: {e}[/bold red]")
        return None, None


def generate_filename(image_path: Path) -> Optional[str]:
    """
    Use Grok-2 Vision to generate a descriptive filename (5 words or less).
    Returns filename without extension, or None on error.
    """
    media_type = "video" if image_path.suffix.lower() == '.mp4' else "image"
    console.print(f"[cyan]Analyzing {media_type}:[/cyan] {image_path.name}")
    
    # Encode image (for videos, this extracts a frame)
    base64_img, mime_type = get_image_base64(image_path)
    if not base64_img:
        return None
    
    # Always use image MIME type since we're sending frames from videos
    media_url = f"data:image/{mime_type};base64,{base64_img}"
    
    # Prepare prompt
    prompt = (
        "Analyze this image and generate a descriptive filename using 5 words or less. "
        "Use only lowercase letters, numbers, and underscores between words. "
        "Be concise and descriptive. Return ONLY the filename, nothing else. "
        "Example format: blue_sky_mountains_sunset or cat_sitting_window"
    )
    
    try:
        # Call xAI API
        response = client.chat.completions.create(
            model=XAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": media_url, "detail": "high"}},
                        {"type": "text", "text": prompt}
                    ]
                }
            ],
            temperature=0.3,
            max_tokens=50,
        )
        
        filename = response.choices[0].message.content.strip()
        
        # Clean filename (remove quotes, spaces, etc.)
        filename = filename.lower()
        filename = filename.strip('"\'`.')
        filename = filename.replace(' ', '_')
        filename = filename.replace('-', '_')
        
        # Remove any non-alphanumeric except underscores
        filename = ''.join(c for c in filename if c.isalnum() or c == '_')
        
        # Remove multiple underscores
        while '__' in filename:
            filename = filename.replace('__', '_')
        
        filename = filename.strip('_')
        
        console.print(f"[green]Generated filename:[/green] {filename}")
        return filename
        
    except Exception as e:
        console.print(f"[bold red]Error generating filename: {e}[/bold red]")
        return None


def rename_image(image_path: Path, dry_run: bool = False) -> Optional[Dict]:
    """
    Rename a single image file.
    Returns rename operation dict or None on failure.
    """
    if not image_path.exists():
        console.print(f"[bold red]File not found:[/bold red] {image_path}")
        return None
    
    if image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        console.print(f"[yellow]Skipping unsupported file:[/yellow] {image_path.name}")
        return None
    
    # Generate new filename
    new_name = generate_filename(image_path)
    if not new_name:
        return None
    
    # Add extension
    new_name = new_name + image_path.suffix.lower()
    new_path = image_path.parent / new_name
    
    # Handle duplicates
    counter = 1
    base_name = new_name
    while new_path.exists() and new_path != image_path:
        name_without_ext = Path(base_name).stem
        new_name = f"{name_without_ext}_{counter}{image_path.suffix.lower()}"
        new_path = image_path.parent / new_name
        counter += 1
    
    # Skip if names are the same
    if new_path == image_path:
        console.print(f"[yellow]Filename unchanged:[/yellow] {image_path.name}")
        return None
    
    console.print(f"[cyan]Renaming:[/cyan]")
    console.print(f"  From: {image_path.name}")
    console.print(f"  To:   {new_name}")
    
    if dry_run:
        console.print("[yellow][DRY RUN] File not actually renamed[/yellow]")
        return {
            "original_path": str(image_path.absolute()),
            "new_path": str(new_path.absolute()),
            "timestamp": datetime.now().isoformat(),
            "dry_run": True
        }
    
    try:
        # Perform rename
        image_path.rename(new_path)
        console.print(f"[bold green]✓ Successfully renamed![/bold green]\n")
        
        return {
            "original_path": str(image_path.absolute()),
            "new_path": str(new_path.absolute()),
            "timestamp": datetime.now().isoformat(),
            "dry_run": False
        }
    except Exception as e:
        console.print(f"[bold red]Error renaming file: {e}[/bold red]\n")
        return None


def process_directory(directory: Path, recursive: bool = False, dry_run: bool = False) -> List[Dict]:
    """
    Process all images in a directory.
    Returns list of rename operations.
    """
    if not directory.exists() or not directory.is_dir():
        console.print(f"[bold red]Directory not found:[/bold red] {directory}")
        return []
    
    # Find media files
    pattern = "**/*" if recursive else "*"
    all_files = list(directory.glob(pattern))
    media_files = [f for f in all_files if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS]
    
    # Deduplicate before processing
    if media_files:
        media_files = deduplicate_files(media_files, dry_run=dry_run)
    
    if not media_files:
        console.print("[yellow]No supported files found in directory[/yellow]")
        return []
    
    console.print(Panel(
        f"[bold cyan]Found {len(media_files)} file(s) to process[/bold cyan]",
        expand=False
    ))
    
    # Process each image
    operations = []
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Processing files...", total=len(media_files))
        
        for image_file in media_files:
            operation = rename_image(image_file, dry_run=dry_run)
            if operation:
                operations.append(operation)
            progress.update(task, advance=1)
    
    return operations


def undo_renames(undo_all: bool = False) -> None:
    """
    Undo rename operations from the log.
    If undo_all is False, only undo the last operation.
    If undo_all is True, undo all operations.
    """
    log_data = load_rename_log()
    
    if not log_data["renames"]:
        console.print("[yellow]No renames to undo[/yellow]")
        return
    
    if undo_all:
        renames_to_undo = list(reversed(log_data["renames"]))
        console.print(f"[cyan]Undoing all {len(renames_to_undo)} rename operations...[/cyan]")
    else:
        if not log_data["last_operation"]:
            console.print("[yellow]No last operation found[/yellow]")
            return
        
        # Get all renames from the last operation
        last_op_time = log_data["last_operation"]
        renames_to_undo = [
            r for r in reversed(log_data["renames"])
            if r.get("operation_id") == last_op_time
        ]
        
        if not renames_to_undo:
            console.print("[yellow]No renames found for last operation[/yellow]")
            return
        
        console.print(f"[cyan]Undoing {len(renames_to_undo)} rename(s) from last operation...[/cyan]")
    
    # Perform undo
    success_count = 0
    fail_count = 0
    
    for rename_op in renames_to_undo:
        if rename_op.get("dry_run"):
            continue
        
        original_path = Path(rename_op["original_path"])
        new_path = Path(rename_op["new_path"])
        
        if new_path.exists():
            try:
                new_path.rename(original_path)
                console.print(f"[green]✓ Restored:[/green] {original_path.name}")
                success_count += 1
                
                # Remove from log
                log_data["renames"].remove(rename_op)
            except Exception as e:
                console.print(f"[red]✗ Failed to restore {original_path.name}: {e}[/red]")
                fail_count += 1
        else:
            console.print(f"[yellow]! File not found:[/yellow] {new_path}")
            fail_count += 1
    
    # Update log
    if undo_all:
        log_data["last_operation"] = None
    
    save_rename_log(log_data)
    
    console.print(f"\n[bold]Undo complete:[/bold] {success_count} restored, {fail_count} failed")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI-powered media file renaming using xAI Grok-2 Vision",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --dir ./media                 # Rename all media files in directory
  %(prog)s --dir ./media --recursive     # Include subdirectories
  %(prog)s --file photo.jpg              # Rename single image
  %(prog)s --file video.mp4              # Rename single video
  %(prog)s --dry-run --dir ./media       # Preview renames without changing files
  %(prog)s --undo                        # Undo last rename operation
  %(prog)s --undo --all                  # Undo all renames
        """
    )
    
    # Main operations
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", "-f", type=str, help="Process a single media file (image or video)")
    group.add_argument("--dir", "-d", type=str, help="Process all media files in directory")
    group.add_argument("--undo", "-u", action="store_true", help="Undo rename operations")
    
    # Options
    parser.add_argument("--recursive", "-r", action="store_true", help="Process subdirectories recursively")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Preview without renaming files")
    parser.add_argument("--all", "-a", action="store_true", help="With --undo, undo all operations")
    
    args = parser.parse_args()
    
    # Display header
    console.print(Panel.fit(
        "[bold cyan]AI Media Renamer[/bold cyan]\n"
        "Powered by xAI Grok-2 Vision",
        border_style="cyan"
    ))
    
    # Handle undo
    if args.undo:
        undo_renames(undo_all=args.all)
        return
    
    # Load log
    log_data = load_rename_log()
    operation_id = datetime.now().isoformat()
    
    # Process files
    operations = []
    
    if args.file:
        operation = rename_image(Path(args.file), dry_run=args.dry_run)
        if operation:
            operations.append(operation)
    
    elif args.dir:
        operations = process_directory(
            Path(args.dir),
            recursive=args.recursive,
            dry_run=args.dry_run
        )
    
    # Save to log
    if operations:
        for op in operations:
            op["operation_id"] = operation_id
            log_data["renames"].append(op)
        
        log_data["last_operation"] = operation_id
        save_rename_log(log_data)
        
        # Display summary
        table = Table(title="Rename Summary")
        table.add_column("Original", style="cyan")
        table.add_column("New Name", style="green")
        
        for op in operations:
            orig_name = Path(op["original_path"]).name
            new_name = Path(op["new_path"]).name
            table.add_row(orig_name, new_name)
        
        console.print("\n")
        console.print(table)
        
        if not args.dry_run:
            console.print(f"\n[green]✓ Renamed {len(operations)} file(s) successfully[/green]")
            console.print(f"[dim]To undo: python {Path(__file__).name} --undo[/dim]")
        else:
            console.print(f"\n[yellow]Dry run complete - no files were renamed[/yellow]")
    else:
        console.print("\n[yellow]No files were renamed[/yellow]")


if __name__ == "__main__":
    main()
