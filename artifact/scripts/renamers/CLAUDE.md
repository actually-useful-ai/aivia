# CLAUDE.md
<!-- Navigation: ~/projects/renamers/CLAUDE.md -->
<!-- Parent: ~/projects/CLAUDE.md -->
<!-- Map: ~/CLAUDE_MAP.md -->

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Two file renaming utilities with distinct strategies:

- **namecrawler/** - PyPI package (`pip install namecrawler`). SHA256 hash-based file renaming for privacy and deduplication. Zero external dependencies (stdlib only).
- **rename_academic_pdfs.py** - Standalone script. Renames academic PDFs using a three-tier metadata extraction fallback: PDF metadata (PyMuPDF) → DOI + Unpaywall API → xAI Grok-2 text analysis.

These are lightweight, focused tools. For full document workflows, see `herd` and `reference-renamer` in `/home/coolhand/projects/packages/working/`.

## Build & Test

### namecrawler

```bash
cd namecrawler
pip install -e .

# Run tests
pytest                               # all tests (7 tests)
pytest tests/test_namecrawler.py -v  # verbose single file
pytest -k test_rename_file           # single test by name

# CLI usage
namecrawler file1.pdf file2.jpg
```

### rename_academic_pdfs.py

```bash
# Dependencies: pymupdf openai rich requests
# Requires XAI_API_KEY env var (or uses hardcoded fallback)

python rename_academic_pdfs.py --dir "path/to/pdfs"            # dry run (default)
python rename_academic_pdfs.py --dir "path/to/pdfs" --execute  # actually rename
python rename_academic_pdfs.py --undo                          # undo last batch
python rename_academic_pdfs.py --stats                         # show statistics
```

No test suite for the PDF renamer - test with `--dir` (dry-run mode is default and safe).

## Architecture

### namecrawler

Standard Python package layout with `src/` structure:

```
namecrawler/src/namecrawler/cli.py  → entire implementation (~40 lines)
```

Entry point: `namecrawler.cli:main`. Two public functions: `sha256sum(path) -> str` and `rename_file(path) -> Path`. Tests in `namecrawler/tests/test_namecrawler.py` use `tmp_path` fixtures.

pytest config in `namecrawler/pytest.ini` sets `--strict-markers --tb=short` defaults.

### rename_academic_pdfs.py

Single-file script (~1030 lines). Key flow:

1. `extract_metadata_multi_strategy()` tries three strategies in order:
   - `extract_pdf_metadata()` - reads embedded PDF metadata via PyMuPDF
   - `extract_doi_from_pdf()` → `query_unpaywall()` - finds DOI in text, queries free Unpaywall API
   - Falls back to `generate_filename_with_ai()` - sends text excerpt to xAI Grok-2
2. `metadata_to_filename()` converts metadata to format: `authorlastname_YYYY_keyword_keyword_keyword`
3. All operations logged to `/home/coolhand/servers/clinical/data/pdf_rename_log.json` for undo support
4. Unpaywall responses cached at `/home/coolhand/servers/clinical/data/unpaywall_cache.json`

The xAI client uses the OpenAI SDK pointed at `https://api.x.ai/v1`. Retry logic is manual (loop with `time.sleep`), not backoff-based.

## Environment Variables

| Variable | Used By | Purpose |
|----------|---------|---------|
| `XAI_API_KEY` | rename_academic_pdfs.py | xAI API access for fallback strategy |

## Author

All projects by **Luke Steuber**. Never credit "Claude" or "AI" as author.
