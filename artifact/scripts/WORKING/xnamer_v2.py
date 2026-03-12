#!/usr/bin/env python3
"""
xnamer - AI-Powered Media File Renaming (v2 - using shared/utils)

Thin CLI wrapper around shared/utils/vision.py for intelligent file renaming.

Usage:
    python xnamer_v2.py --dir ./media              # Rename media files in directory
    python xnamer_v2.py --file image.jpg           # Rename single image
    python xnamer_v2.py --file video.mp4           # Rename single video

Author: Luke Steuber
"""

import sys
import argparse
from pathlib import Path

# Add shared library to path
sys.path.insert(0, str(Path.home() / "shared"))

try:
    from utils import analyze_image, analyze_video, generate_filename_from_vision
    from rich.console import Console
    from rich.progress import Progress, TextColumn, BarColumn
except ImportError as e:
    print(f"Missing required package: {e}")
    print("\nInstall required packages with:")
    print("pip install rich")
    print("\nOr install vision dependencies:")
    print("pip install openai pillow opencv-python")
    sys.exit(1)

console = Console()

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.heic', '.mp4', '.mov', '.avi'}


def rename_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Rename a single file using AI vision.

    Args:
        file_path: Path to file
        dry_run: If True, don't actually rename

    Returns:
        True if successful
    """
    try:
        # Generate filename using shared utility
        new_filename = generate_filename_from_vision(file_path)

        if not new_filename:
            console.print(f"[red]Failed to generate filename for: {file_path.name}[/red]")
            return False

        # Construct new path
        new_path = file_path.parent / new_filename

        # Handle conflicts
        if new_path.exists() and new_path != file_path:
            stem = new_path.stem
            suffix = new_path.suffix
            counter = 1
            while new_path.exists():
                new_path = file_path.parent / f"{stem}_{counter}{suffix}"
                counter += 1

        console.print(f"[cyan]{file_path.name}[/cyan] → [green]{new_path.name}[/green]")

        if not dry_run:
            file_path.rename(new_path)

        return True

    except Exception as e:
        console.print(f"[red]Error processing {file_path.name}: {e}[/red]")
        return False


def rename_directory(dir_path: Path, dry_run: bool = False):
    """
    Rename all supported files in a directory.

    Args:
        dir_path: Directory to process
        dry_run: If True, don't actually rename
    """
    if not dir_path.is_dir():
        console.print(f"[red]Error: Not a directory: {dir_path}[/red]")
        return

    # Find supported files
    files = [f for f in dir_path.iterdir()
             if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS]

    if not files:
        console.print("[yellow]No supported media files found[/yellow]")
        return

    console.print(f"\n[bold]Found {len(files)} media files[/bold]")

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be renamed[/yellow]\n")

    # Process files with progress bar
    success_count = 0
    failure_count = 0

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("Renaming files...", total=len(files))

        for file_path in files:
            if rename_file(file_path, dry_run):
                success_count += 1
            else:
                failure_count += 1

            progress.update(task, advance=1)

    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  [green]Success: {success_count}[/green]")
    console.print(f"  [red]Failed: {failure_count}[/red]")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI-Powered Media File Renaming (using shared/utils)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rename all files in directory
  python xnamer_v2.py --dir ./photos

  # Rename single file
  python xnamer_v2.py --file image.jpg

  # Dry run (simulate)
  python xnamer_v2.py --dir ./photos --dry-run

Note: This is a thin wrapper around shared/utils/vision.py
        """
    )

    parser.add_argument("--dir", type=str, help="Directory containing media files")
    parser.add_argument("--file", type=str, help="Single file to rename")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without renaming")

    args = parser.parse_args()

    if not args.dir and not args.file:
        parser.print_help()
        return 1

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            console.print(f"[red]Error: File not found: {args.file}[/red]")
            return 1

        rename_file(file_path, args.dry_run)

    elif args.dir:
        dir_path = Path(args.dir)
        rename_directory(dir_path, args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
