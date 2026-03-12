# File Renaming Tools

This directory aggregates focused utilities for renaming files—especially academic PDFs and hashed archives. These scripts complement, but do not replace, the more feature-rich packages in `/home/coolhand/projects/packages/`.

## Tools

### `rename_academic_pdfs.py`
- **Purpose:** Generate human-readable filenames for academic PDFs using metadata, DOI lookups, and xAI enrichment.
- **Features:**
  - Multi-strategy metadata extraction (PDF metadata, DOI, LLM summary support).
  - Integrates with the Unpaywall API for DOI resolution.
  - Produces filenames such as `AuthorLastName_YYYY_TopicKeywords.pdf`.
  - Supports dry-run and undo flows for safer batch work.
- **Usage:**
  ```bash
  python rename_academic_pdfs.py /path/to/pdfs --dry-run
  python rename_academic_pdfs.py /path/to/pdfs --apply
  ```

### `namecrawler/`
- **Purpose:** Simple hash-based renaming utility that produces SHA256-based filenames.
- **Package entry point:** `python -m namecrawler` or `namecrawler <files...>` once installed.
- **Usage:**
  ```bash
  poetry install  # or pip install -e .
  namecrawler myfile.docx another.pdf
  ```

## Relationship to Other Renaming Solutions

| Tool / Package | Location | Scope | Notes |
|----------------|----------|-------|-------|
| `herd` | `/home/coolhand/projects/packages/working/herd` | Comprehensive document management (renaming + ingestion) | Includes GUI + CLI |
| `reference-renamer` | `/home/coolhand/projects/packages/working/reference-renamer` | Academic reference enrichment and citation utilities | Pip installable |
| `cleanupx` (archived Sep 2024) | `/home/coolhand/projects/packages/archived/cleanupx-renamers-sep2024` | Historical text cleanup pipeline | Superseded by `/packages/incomplete/cleanupx` |
| `rename_academic_pdfs.py` | This directory | Scriptable academic PDF renaming | Ideal for quick batch jobs |
| `namecrawler` | This directory | Hash-based renaming | Keeps filenames opaque + traceable |

## When to Use Which
- Use **`rename_academic_pdfs.py`** when you need descriptive, human-readable filenames for scholarly materials.
- Use **`namecrawler`** when you need deterministic, hash-based filenames or want to anonymize file names without losing traceability.
- Use **`herd`** when you require a full document workflow (metadata enrichment, ingestion, GUI).
- Use **`reference-renamer`** for citation-focused enrichment and cross-referencing.

## Notes
- These scripts assume Python 3.8+.
- API keys (xAI, Unpaywall, etc.) should be provided via environment variables or `.env` files when required.
- Add new tools to this README with a clear description, usage example, and relationship notes.

