#!/usr/bin/env python3
"""
rename_academic_pdfs.py - Intelligent Academic PDF Renaming Script

Uses multi-strategy metadata extraction to intelligently rename academic PDFs:
1. PDF metadata extraction (PyMuPDF/pypdf)
2. DOI extraction + Unpaywall API lookup (free, no key needed)
3. AI analysis using xAI grok-4-fast-non-reasoning (fallback)

Generates standardized filenames: AuthorLastName_YYYY_Keyword_Keyword.pdf

Usage:
    python rename_academic_pdfs.py --dir "inbox/Academic References" --dry-run
    python rename_academic_pdfs.py --dir "inbox/Academic References" --execute
    python rename_academic_pdfs.py --undo
    python rename_academic_pdfs.py --stats

Examples:
    # Preview renames without making changes (default)
    python rename_academic_pdfs.py --dir "inbox/Academic References"

    # Execute renames
    python rename_academic_pdfs.py --dir "inbox/Academic References" --execute

    # Show statistics on metadata extraction success rates
    python rename_academic_pdfs.py --dir "inbox/Academic References" --stats

    # Undo last batch of renames
    python rename_academic_pdfs.py --undo

    # Process with custom batch size
    python rename_academic_pdfs.py --dir "inbox/Academic References" --batch-size 50 --execute

Author: AI-Enhanced Clinical Reference System
"""

import os
import sys
import json
import re
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import Counter

try:
    import fitz  # PyMuPDF
    from openai import OpenAI
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
    from rich.table import Table
    from rich.prompt import Confirm
    import requests
except ImportError as e:
    print(f"Missing required package: {e}")
    print("\nInstall required packages with:")
    print("pip install pymupdf openai rich requests")
    sys.exit(1)

# --- Configuration ---
XAI_API_KEY = os.getenv("XAI_API_KEY", "REDACTED_XAI_KEY")
XAI_BASE_URL = "https://api.x.ai/v1"
XAI_MODEL = "grok-2-1212"  # Using grok-2 for better academic text analysis

# Paths
RENAME_LOG_FILE = Path("/home/coolhand/servers/clinical/data/pdf_rename_log.json")
UNPAYWALL_CACHE_FILE = Path("/home/coolhand/servers/clinical/data/unpaywall_cache.json")

# API Configuration
UNPAYWALL_API_BASE = "https://api.unpaywall.org/v2"
UNPAYWALL_EMAIL = "clinical@eamer.dev"  # Required by Unpaywall API

# Processing Configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
TEXT_EXTRACT_CHARS = 1000  # Characters to extract for AI analysis
DOI_PAGES_TO_CHECK = 2  # Check first N pages for DOI

# Initialize rich console
console = Console()

# Initialize OpenAI client for xAI
try:
    client = OpenAI(
        api_key=XAI_API_KEY,
        base_url=XAI_BASE_URL,
    )
except Exception as e:
    console.print(f"[bold red]Warning: Failed to initialize xAI client: {e}[/bold red]")
    client = None


# --- Helper Functions ---

def load_rename_log() -> Dict:
    """Load the rename log for undo functionality."""
    if RENAME_LOG_FILE.exists():
        try:
            with open(RENAME_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            console.print("[yellow]Warning: Corrupt rename log, creating new one[/yellow]")
            return {"renames": [], "last_operation": None, "stats": {}}
    return {"renames": [], "last_operation": None, "stats": {}}


def save_rename_log(log_data: Dict) -> None:
    """Save the rename log to file."""
    log_data["last_updated"] = datetime.now().isoformat()
    RENAME_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RENAME_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)


def load_unpaywall_cache() -> Dict:
    """Load cached Unpaywall API responses."""
    if UNPAYWALL_CACHE_FILE.exists():
        try:
            with open(UNPAYWALL_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_unpaywall_cache(cache: Dict) -> None:
    """Save Unpaywall API cache."""
    UNPAYWALL_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(UNPAYWALL_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def clean_filename(text: str, max_words: int = 5) -> str:
    """
    Clean and format text for use in filename.

    Args:
        text: Text to clean
        max_words: Maximum number of words to keep

    Returns:
        Cleaned filename-safe string
    """
    # Convert to lowercase
    text = text.lower()

    # Remove special characters, keep only alphanumeric and spaces
    text = re.sub(r'[^a-z0-9\s\-]', '', text)

    # Replace multiple spaces/hyphens with single space
    text = re.sub(r'[\s\-]+', ' ', text)

    # Split into words and limit
    words = text.strip().split()[:max_words]

    # Join with underscores
    return '_'.join(words)


def extract_year(text: str) -> Optional[str]:
    """
    Extract 4-digit year from text.
    Prefers years between 1990-2030 (reasonable range for academic papers).

    Args:
        text: Text to search for year

    Returns:
        Year as string or None
    """
    # Look for 4-digit years
    years = re.findall(r'\b(19\d{2}|20[0-3]\d)\b', text)

    if years:
        # Return the first year in reasonable range
        for year in years:
            year_int = int(year)
            if 1990 <= year_int <= 2030:
                return year
        # If no year in preferred range, return first found
        return years[0]

    return None


def extract_doi(text: str) -> Optional[str]:
    """
    Extract DOI (Digital Object Identifier) from text.

    Args:
        text: Text to search for DOI

    Returns:
        DOI string or None
    """
    # Common DOI patterns
    doi_patterns = [
        r'doi:\s*([10]\.\d{4,}/[^\s]+)',
        r'DOI:\s*([10]\.\d{4,}/[^\s]+)',
        r'https?://doi\.org/([10]\.\d{4,}/[^\s]+)',
        r'https?://dx\.doi\.org/([10]\.\d{4,}/[^\s]+)',
    ]

    for pattern in doi_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            doi = match.group(1)
            # Clean up common trailing characters
            doi = re.sub(r'[,;.\s]+$', '', doi)
            return doi

    return None


def query_unpaywall(doi: str, cache: Dict) -> Optional[Dict]:
    """
    Query Unpaywall API for metadata by DOI.

    Args:
        doi: Digital Object Identifier
        cache: Cache dictionary to avoid re-querying

    Returns:
        Metadata dict or None
    """
    # Check cache first
    if doi in cache:
        return cache[doi]

    try:
        url = f"{UNPAYWALL_API_BASE}/{doi}"
        params = {"email": UNPAYWALL_EMAIL}

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            metadata = {
                'title': data.get('title'),
                'year': data.get('year'),
                'authors': data.get('z_authors', []),
                'source': 'unpaywall'
            }

            # Cache the result
            cache[doi] = metadata
            save_unpaywall_cache(cache)

            return metadata
        else:
            # Cache negative result to avoid re-querying
            cache[doi] = None
            save_unpaywall_cache(cache)
            return None

    except Exception as e:
        console.print(f"[yellow]Unpaywall API error: {e}[/yellow]")
        return None


def extract_pdf_metadata(pdf_path: Path) -> Optional[Dict]:
    """
    Extract metadata from PDF file using PyMuPDF.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Metadata dict with keys: title, author, year, source
    """
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata

        if not metadata:
            return None

        # Extract relevant fields
        title = metadata.get('title', '').strip()
        author = metadata.get('author', '').strip()
        subject = metadata.get('subject', '').strip()

        # Try to extract year from various fields
        year = None
        for field in [metadata.get('creationDate', ''), metadata.get('modDate', ''), subject]:
            if field:
                year = extract_year(field)
                if year:
                    break

        # Only return if we have at least title or author
        if title or author:
            return {
                'title': title,
                'author': author,
                'year': year,
                'source': 'pdf_metadata'
            }

        return None

    except Exception as e:
        console.print(f"[yellow]Error extracting PDF metadata from {pdf_path.name}: {e}[/yellow]")
        return None


def extract_text_from_pdf(pdf_path: Path, max_chars: int = TEXT_EXTRACT_CHARS,
                          max_pages: int = 2) -> Optional[str]:
    """
    Extract text from first few pages of PDF.

    Args:
        pdf_path: Path to PDF file
        max_chars: Maximum characters to extract
        max_pages: Maximum pages to read

    Returns:
        Extracted text or None
    """
    try:
        doc = fitz.open(pdf_path)
        text_parts = []

        for page_num in range(min(max_pages, len(doc))):
            page = doc[page_num]
            text_parts.append(page.get_text())

            # Stop if we have enough text
            if len(''.join(text_parts)) >= max_chars:
                break

        text = ''.join(text_parts)[:max_chars]

        return text.strip() if text.strip() else None

    except Exception as e:
        console.print(f"[yellow]Error extracting text from {pdf_path.name}: {e}[/yellow]")
        return None


def extract_doi_from_pdf(pdf_path: Path, max_pages: int = DOI_PAGES_TO_CHECK) -> Optional[str]:
    """
    Extract DOI from PDF text.

    Args:
        pdf_path: Path to PDF file
        max_pages: Maximum pages to check

    Returns:
        DOI string or None
    """
    try:
        doc = fitz.open(pdf_path)

        for page_num in range(min(max_pages, len(doc))):
            page = doc[page_num]
            text = page.get_text()

            doi = extract_doi(text)
            if doi:
                return doi

        return None

    except Exception as e:
        console.print(f"[yellow]Error extracting DOI from {pdf_path.name}: {e}[/yellow]")
        return None


def generate_filename_with_ai(text: str, original_filename: str) -> Optional[str]:
    """
    Use xAI to generate standardized filename from text excerpt.

    Args:
        text: Text excerpt from PDF
        original_filename: Original filename for context

    Returns:
        Filename (without extension) or None
    """
    if not client:
        return None

    prompt = f"""Analyze this academic paper excerpt and generate a standardized filename.

Original filename: {original_filename}

Text excerpt:
{text[:1000]}

Generate a filename in this EXACT format: AuthorLastName_YYYY_Keyword_Keyword_Keyword

Rules:
- Use the first author's last name (lowercase)
- Include the publication year (YYYY)
- Add 3-5 descriptive keywords from the title/topic (lowercase, underscores)
- Use ONLY lowercase letters, numbers, and underscores
- Return ONLY the filename without .pdf extension
- Maximum 5 words after the year

Examples:
hunter_2014_rett_syndrome_communication
smith_2020_aac_intervention_outcomes
jones_2018_cerebral_palsy_motor

Return ONLY the filename, nothing else."""

    try:
        for attempt in range(MAX_RETRIES):
            try:
                response = client.chat.completions.create(
                    model=XAI_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=100,
                )

                filename = response.choices[0].message.content.strip()

                # Clean the response
                filename = filename.lower()
                filename = filename.strip('"\'`.')
                filename = re.sub(r'\.pdf$', '', filename)  # Remove .pdf if present
                filename = re.sub(r'[^a-z0-9_]', '', filename)  # Keep only valid chars

                # Remove multiple underscores
                while '__' in filename:
                    filename = filename.replace('__', '_')

                filename = filename.strip('_')

                # Validate format (author_year_keywords)
                parts = filename.split('_')
                if len(parts) >= 3:  # At least author_year_keyword
                    # Check if second part looks like a year
                    if re.match(r'^(19|20)\d{2}$', parts[1]):
                        return filename

                # If format doesn't match, return cleaned version anyway
                return filename if filename else None

            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    console.print(f"[yellow]AI API retry {attempt + 1}/{MAX_RETRIES}: {e}[/yellow]")
                    time.sleep(RETRY_DELAY)
                else:
                    raise

        return None

    except Exception as e:
        console.print(f"[bold red]Error generating filename with AI: {e}[/bold red]")
        return None


def extract_metadata_multi_strategy(pdf_path: Path, unpaywall_cache: Dict) -> Tuple[Optional[Dict], str]:
    """
    Extract metadata using multiple strategies in order of preference.

    Strategy order:
    1. PDF metadata extraction
    2. DOI extraction + Unpaywall API
    3. AI analysis of text excerpt

    Args:
        pdf_path: Path to PDF file
        unpaywall_cache: Cache for Unpaywall API results

    Returns:
        Tuple of (metadata dict, strategy name)
    """
    # Strategy 1: PDF Metadata
    metadata = extract_pdf_metadata(pdf_path)
    if metadata and metadata.get('title'):
        return metadata, 'pdf_metadata'

    # Strategy 2: DOI + Unpaywall
    doi = extract_doi_from_pdf(pdf_path)
    if doi:
        unpaywall_data = query_unpaywall(doi, unpaywall_cache)
        if unpaywall_data:
            return unpaywall_data, 'unpaywall'

    # Strategy 3: AI Analysis
    text = extract_text_from_pdf(pdf_path)
    if text:
        # Try to extract year from text if AI doesn't provide it
        year_from_text = extract_year(text)

        return {
            'text': text,
            'year': year_from_text,
            'source': 'ai_analysis'
        }, 'ai_analysis'

    return None, 'failed'


def metadata_to_filename(metadata: Dict, original_filename: str) -> Optional[str]:
    """
    Convert metadata to standardized filename.

    Args:
        metadata: Metadata dictionary
        original_filename: Original filename for fallback

    Returns:
        Filename (without extension) or None
    """
    if metadata['source'] == 'ai_analysis':
        # Use AI to generate filename from text
        return generate_filename_with_ai(metadata.get('text', ''), original_filename)

    # Extract components
    author_last = None
    year = metadata.get('year')
    title = metadata.get('title', '')

    # Extract author last name
    author = metadata.get('author', '')
    if author:
        # Try to get last name
        parts = author.split()
        if parts:
            author_last = parts[-1]
    elif metadata.get('authors'):
        # From Unpaywall format
        authors = metadata['authors']
        if authors and len(authors) > 0:
            first_author = authors[0]
            if isinstance(first_author, dict):
                author_last = first_author.get('family', first_author.get('given', ''))
            else:
                author_last = str(first_author).split()[-1] if first_author else None

    # Build filename components
    parts = []

    if author_last:
        parts.append(clean_filename(author_last, max_words=1))

    if year:
        parts.append(str(year))

    if title:
        # Extract keywords from title (3-5 words)
        title_keywords = clean_filename(title, max_words=5)
        if title_keywords:
            parts.append(title_keywords)

    # Need at least author or title
    if len(parts) >= 2:
        return '_'.join(parts)

    return None


def generate_unique_filename(base_path: Path, base_name: str, extension: str) -> Path:
    """
    Generate unique filename by adding numeric suffix if needed.

    Args:
        base_path: Directory for the file
        base_name: Base filename without extension
        extension: File extension (including dot)

    Returns:
        Unique file path
    """
    new_path = base_path / f"{base_name}{extension}"
    counter = 2

    while new_path.exists():
        new_path = base_path / f"{base_name}_{counter}{extension}"
        counter += 1

    return new_path


def rename_pdf(pdf_path: Path, unpaywall_cache: Dict, dry_run: bool = True) -> Optional[Dict]:
    """
    Rename a single PDF file using multi-strategy metadata extraction.

    Args:
        pdf_path: Path to PDF file
        unpaywall_cache: Unpaywall API cache
        dry_run: If True, don't actually rename files

    Returns:
        Rename operation dict or None
    """
    if not pdf_path.exists():
        console.print(f"[bold red]File not found:[/bold red] {pdf_path}")
        return None

    if pdf_path.suffix.lower() != '.pdf':
        console.print(f"[yellow]Skipping non-PDF file:[/yellow] {pdf_path.name}")
        return None

    console.print(f"\n[cyan]Processing:[/cyan] {pdf_path.name}")

    # Extract metadata
    metadata, strategy = extract_metadata_multi_strategy(pdf_path, unpaywall_cache)

    if not metadata:
        console.print(f"[red]✗ Failed to extract metadata[/red]")
        return {
            'original_path': str(pdf_path.absolute()),
            'new_path': None,
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy,
            'status': 'failed',
            'dry_run': dry_run
        }

    console.print(f"[green]Strategy:[/green] {strategy}")

    # Generate filename
    new_name = metadata_to_filename(metadata, pdf_path.stem)

    if not new_name:
        console.print(f"[red]✗ Failed to generate filename[/red]")
        return {
            'original_path': str(pdf_path.absolute()),
            'new_path': None,
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy,
            'status': 'failed',
            'dry_run': dry_run
        }

    # Generate unique path
    new_path = generate_unique_filename(pdf_path.parent, new_name, pdf_path.suffix.lower())

    # Check if names are the same
    if new_path == pdf_path:
        console.print(f"[yellow]Filename unchanged[/yellow]")
        return None

    console.print(f"[green]New name:[/green] {new_path.name}")

    if dry_run:
        console.print(f"[yellow][DRY RUN] File not actually renamed[/yellow]")
        return {
            'original_path': str(pdf_path.absolute()),
            'new_path': str(new_path.absolute()),
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy,
            'status': 'success',
            'dry_run': True
        }

    # Perform rename
    try:
        pdf_path.rename(new_path)
        console.print(f"[bold green]✓ Successfully renamed![/bold green]")

        return {
            'original_path': str(pdf_path.absolute()),
            'new_path': str(new_path.absolute()),
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy,
            'status': 'success',
            'dry_run': False
        }
    except Exception as e:
        console.print(f"[bold red]✗ Error renaming file: {e}[/bold red]")
        return {
            'original_path': str(pdf_path.absolute()),
            'new_path': None,
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy,
            'status': 'error',
            'error': str(e),
            'dry_run': dry_run
        }


def process_directory(directory: Path, batch_size: int = 100, dry_run: bool = True, skip_confirm: bool = False) -> List[Dict]:
    """
    Process all PDFs in a directory.

    Args:
        directory: Directory containing PDFs
        batch_size: Number of files to process in one batch
        dry_run: If True, don't actually rename files
        skip_confirm: If True, skip confirmation prompts

    Returns:
        List of rename operations
    """
    if not directory.exists() or not directory.is_dir():
        console.print(f"[bold red]Directory not found:[/bold red] {directory}")
        return []

    # Find PDF files
    pdf_files = sorted([f for f in directory.glob("*.pdf") if f.is_file()])

    if not pdf_files:
        console.print("[yellow]No PDF files found in directory[/yellow]")
        return []

    console.print(f"\n[bold cyan]Found {len(pdf_files)} PDF files[/bold cyan]")

    # Load Unpaywall cache
    unpaywall_cache = load_unpaywall_cache()

    # Estimate AI cost if needed
    if not dry_run and not skip_confirm:
        # Rough estimate: assume 30% will need AI (after metadata and DOI fail)
        estimated_ai_calls = int(len(pdf_files) * 0.3)
        if estimated_ai_calls > 0:
            console.print(f"\n[yellow]Estimated AI API calls: ~{estimated_ai_calls}[/yellow]")
            console.print(f"[dim]Grok-2: ~$0.002 per call (estimate)[/dim]")
            try:
                if not Confirm.ask("\nContinue with processing?"):
                    return []
            except EOFError:
                # Non-interactive mode, continue
                console.print("[yellow]Non-interactive mode detected, continuing...[/yellow]")
                pass

    # Process files
    operations = []
    stats = Counter()

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Processing PDFs...", total=len(pdf_files))

        for pdf_file in pdf_files:
            operation = rename_pdf(pdf_file, unpaywall_cache, dry_run=dry_run)

            if operation:
                operations.append(operation)
                stats[operation.get('strategy', 'unknown')] += 1

                if operation.get('status') == 'success':
                    stats['success'] += 1
                else:
                    stats['failed'] += 1

            progress.update(task, advance=1)

            # Small delay to be respectful to APIs
            time.sleep(0.1)

    # Save updated Unpaywall cache
    save_unpaywall_cache(unpaywall_cache)

    # Display statistics
    console.print("\n[bold cyan]Processing Statistics:[/bold cyan]")
    console.print(f"  Total processed: {len(operations)}")
    console.print(f"  Successful: {stats['success']}")
    console.print(f"  Failed: {stats['failed']}")
    console.print(f"\n[bold cyan]Metadata Strategies:[/bold cyan]")
    console.print(f"  PDF Metadata: {stats['pdf_metadata']}")
    console.print(f"  Unpaywall API: {stats['unpaywall']}")
    console.print(f"  AI Analysis: {stats['ai_analysis']}")
    console.print(f"  Failed: {stats['failed']}")

    return operations


def show_statistics(log_data: Dict) -> None:
    """
    Display statistics about past rename operations.

    Args:
        log_data: Rename log data
    """
    if not log_data.get('renames'):
        console.print("[yellow]No rename operations in log[/yellow]")
        return

    renames = log_data['renames']
    stats = Counter()

    for op in renames:
        stats[op.get('strategy', 'unknown')] += 1
        if op.get('status') == 'success':
            stats['success'] += 1
        else:
            stats['failed'] += 1

    # Create statistics table
    table = Table(title="Rename Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="green", justify="right")

    table.add_row("Total Operations", str(len(renames)))
    table.add_row("Successful", str(stats['success']))
    table.add_row("Failed", str(stats['failed']))
    table.add_row("", "")
    table.add_row("PDF Metadata", str(stats['pdf_metadata']))
    table.add_row("Unpaywall API", str(stats['unpaywall']))
    table.add_row("AI Analysis", str(stats['ai_analysis']))

    console.print("\n")
    console.print(table)


def undo_renames() -> None:
    """
    Undo the last batch of rename operations.
    """
    log_data = load_rename_log()

    if not log_data.get('renames'):
        console.print("[yellow]No renames to undo[/yellow]")
        return

    if not log_data.get('last_operation'):
        console.print("[yellow]No last operation found[/yellow]")
        return

    # Get all renames from the last operation
    last_op_time = log_data['last_operation']
    renames_to_undo = [
        r for r in reversed(log_data['renames'])
        if r.get('operation_id') == last_op_time and r.get('status') == 'success'
    ]

    if not renames_to_undo:
        console.print("[yellow]No successful renames found for last operation[/yellow]")
        return

    console.print(f"\n[cyan]Found {len(renames_to_undo)} renames to undo[/cyan]")

    try:
        if not Confirm.ask("Proceed with undo?"):
            console.print("[yellow]Undo cancelled[/yellow]")
            return
    except EOFError:
        # Non-interactive mode, continue
        console.print("[yellow]Non-interactive mode detected, proceeding...[/yellow]")
        pass

    # Perform undo
    success_count = 0
    fail_count = 0

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Undoing renames...", total=len(renames_to_undo))

        for rename_op in renames_to_undo:
            if rename_op.get('dry_run'):
                progress.update(task, advance=1)
                continue

            original_path = Path(rename_op['original_path'])
            new_path_str = rename_op.get('new_path')

            if not new_path_str:
                fail_count += 1
                progress.update(task, advance=1)
                continue

            new_path = Path(new_path_str)

            if new_path.exists():
                try:
                    new_path.rename(original_path)
                    console.print(f"[green]✓ Restored:[/green] {original_path.name}")
                    success_count += 1

                    # Remove from log
                    log_data['renames'].remove(rename_op)
                except Exception as e:
                    console.print(f"[red]✗ Failed to restore {original_path.name}: {e}[/red]")
                    fail_count += 1
            else:
                console.print(f"[yellow]! File not found:[/yellow] {new_path.name}")
                fail_count += 1

            progress.update(task, advance=1)

    # Update log
    log_data['last_operation'] = None
    save_rename_log(log_data)

    console.print(f"\n[bold]Undo complete:[/bold] {success_count} restored, {fail_count} failed")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Intelligent Academic PDF Renaming with Multi-Strategy Metadata Extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --dir "inbox/Academic References" --dry-run
                                    Preview renames without making changes (default)

  %(prog)s --dir "inbox/Academic References" --execute
                                    Execute renames on all PDFs

  %(prog)s --stats                  Show metadata extraction statistics

  %(prog)s --undo                   Undo last batch of renames

  %(prog)s --dir "inbox/Academic References" --batch-size 50 --execute
                                    Process in smaller batches

Metadata Extraction Strategies:
  1. PDF Metadata: Extracts embedded metadata from PDF
  2. Unpaywall API: Finds DOI and queries free academic database
  3. AI Analysis: Uses xAI Grok-2 to analyze text excerpt

Generated Filename Format:
  AuthorLastName_YYYY_Keyword_Keyword_Keyword.pdf

  Examples:
    hunter_2014_rett_syndrome_communication.pdf
    smith_2020_aac_intervention_outcomes.pdf
        """
    )

    # Main operations
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dir", "-d", type=str, help="Directory containing PDFs to rename")
    group.add_argument("--undo", "-u", action="store_true", help="Undo last batch of renames")
    group.add_argument("--stats", "-s", action="store_true", help="Show statistics")

    # Options
    parser.add_argument("--execute", "-e", action="store_true",
                       help="Actually rename files (default is dry-run)")
    parser.add_argument("--batch-size", "-b", type=int, default=100,
                       help="Process files in batches (default: 100)")
    parser.add_argument("--yes", "-y", action="store_true",
                       help="Skip confirmation prompts")

    args = parser.parse_args()

    # Display header
    console.print(Panel.fit(
        "[bold cyan]Academic PDF Renamer[/bold cyan]\n"
        "Multi-Strategy Metadata Extraction\n"
        "[dim]PDF Metadata → Unpaywall API → xAI Analysis[/dim]",
        border_style="cyan"
    ))

    # Handle undo
    if args.undo:
        undo_renames()
        return

    # Handle stats
    if args.stats:
        log_data = load_rename_log()
        show_statistics(log_data)
        return

    # Process directory
    dry_run = not args.execute

    if dry_run:
        console.print("\n[yellow]DRY RUN MODE[/yellow] - No files will be renamed")
        console.print("[dim]Use --execute to actually rename files[/dim]\n")

    directory = Path(args.dir).expanduser().absolute()

    # Load log
    log_data = load_rename_log()
    operation_id = datetime.now().isoformat()

    # Process files
    operations = process_directory(directory, batch_size=args.batch_size, dry_run=dry_run, skip_confirm=args.yes)

    # Save to log
    if operations:
        for op in operations:
            op["operation_id"] = operation_id
            log_data["renames"].append(op)

        log_data["last_operation"] = operation_id
        save_rename_log(log_data)

        # Display summary table
        table = Table(title="Rename Summary")
        table.add_column("Original", style="cyan", max_width=40)
        table.add_column("New Name", style="green", max_width=40)
        table.add_column("Strategy", style="yellow", max_width=15)

        # Show only successful renames
        successful_ops = [op for op in operations if op.get('status') == 'success']

        for op in successful_ops[:50]:  # Limit display to first 50
            orig_name = Path(op["original_path"]).name
            new_path = op.get("new_path")
            new_name = Path(new_path).name if new_path else "FAILED"
            strategy = op.get("strategy", "unknown")

            table.add_row(orig_name, new_name, strategy)

        if len(successful_ops) > 50:
            table.add_row("...", f"... and {len(successful_ops) - 50} more", "...")

        console.print("\n")
        console.print(table)

        if not dry_run:
            console.print(f"\n[green]✓ Renamed {len(successful_ops)} file(s) successfully[/green]")
            console.print(f"[dim]To undo: python {Path(__file__).name} --undo[/dim]")
        else:
            console.print(f"\n[yellow]Dry run complete - {len(successful_ops)} files would be renamed[/yellow]")
            console.print(f"[dim]Use --execute to perform actual renames[/dim]")
    else:
        console.print("\n[yellow]No files were processed[/yellow]")


if __name__ == "__main__":
    main()
