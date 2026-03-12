# namecrawler

**SHA256 hash-based file renaming for privacy and deduplication**

Rename files using their SHA256 content hash, creating deterministic, collision-resistant, privacy-preserving filenames.

## Installation

```bash
pip install namecrawler
```

## Quick Start

```bash
# Rename single file
namecrawler document.pdf

# Rename multiple files
namecrawler *.jpg

# Rename files in a directory
namecrawler ~/Documents/*.pdf
```

## Features

- **Deterministic**: Same content = same filename (every time)
- **Collision-Resistant**: SHA256 makes accidental collisions virtually impossible
- **Privacy-Preserving**: Original filenames not exposed
- **Deduplication-Friendly**: Identical files get same hash (easy to find duplicates)
- **Format-Preserving**: Original file extensions maintained
- **Fast**: Efficient chunk-based hashing (8KB chunks)
- **Safe**: Only renames files that exist

## Use Cases

### 1. Privacy Protection
Hide sensitive information in original filenames:
```bash
# Before: SSN_123-45-6789_tax_return_2024.pdf
# After:  a3f89b2c1d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6.pdf
namecrawler sensitive_document.pdf
```

### 2. Deduplication
Find duplicate files easily:
```bash
namecrawler ~/Downloads/*.jpg
# Duplicate files will have the same hash name
# Just look for repeated filenames!
```

### 3. Content-Based Organization
Files with same content automatically grouped:
```bash
namecrawler backup_folder/*
# Version 1, 2, 3 of same file → all get same hash
```

### 4. Archival Storage
Create immutable, content-addressed archives:
```bash
namecrawler archive/*.* 
# Filenames never change if content doesn't change
```

## How It Works

1. **Reads file content** in 8KB chunks (memory efficient)
2. **Computes SHA256 hash** of the entire content
3. **Preserves file extension** from original filename
4. **Renames file** to `{hash}{extension}`

**Example:**
```bash
# Original file: "meeting_notes_2024.txt"
# Content hash: "a1b2c3d4e5f6..."
# New filename: "a1b2c3d4e5f6...txt"
```

## API Usage

Use as a Python library:

```python
from namecrawler.cli import sha256sum, rename_file
from pathlib import Path

# Get hash of a file
file_path = Path("document.pdf")
file_hash = sha256sum(file_path)
print(f"SHA256: {file_hash}")

# Rename using hash
new_path = rename_file(file_path)
print(f"Renamed to: {new_path}")
```

## Comparison with Other Tools

| Tool | Method | Reversible | Privacy | Speed |
|------|--------|------------|---------|-------|
| namecrawler | SHA256 hash | No | High | Fast |
| Manual rename | User input | Yes | ❌ Low | ❌ Slow |
| UUID tools | Random UUID | No | High | Fast |
| Timestamp tools | Current time | No | ❌ Low | Fast |

**Advantages over alternatives:**
- More meaningful than UUIDs (hash reveals if content changed)
- More private than timestamps (no metadata leakage)
- Deterministic (unlike random UUIDs)
- Built-in deduplication (same content = same hash)

## Requirements

- Python 3.8+
- No external dependencies (uses stdlib only)

## Limitations

- **Not reversible**: You cannot recover the original filename from the hash
- **Same content = same name**: Files with identical content get identical names
- **No metadata preservation**: Original filename lost (keep a mapping if needed)

## Advanced Usage

### Keep a rename log

```bash
# Create a simple mapping log
for file in *.pdf; do
  echo "$file -> $(namecrawler "$file")" >> rename_log.txt
done
```

### Undo by using a log

namecrawler doesn't include undo (by design - hashes are one-way), but you can create your own:

```python
import json
from pathlib import Path

# Before renaming, save a log
log = {}
for file in Path('.').glob('*.pdf'):
    from namecrawler.cli import sha256sum
    hash_name = sha256sum(file) + file.suffix
    log[hash_name] = str(file)

with open('rename_map.json', 'w') as f:
    json.dump(log, f, indent=2)

# Later, restore using the log
with open('rename_map.json') as f:
    log = json.load(f)
    for hash_name, original in log.items():
        Path(hash_name).rename(original)
```

## Security Note

SHA256 hashes are **cryptographically secure** but **not secret**. If someone has the original file, they can compute the same hash. Use namecrawler for:
- Privacy (hiding original filenames)
- Deduplication (finding identical files)
- Content-addressing (organizing by content)

**Don't use for:**
- Security (anyone with original can verify hash)
- Encryption (filenames are not encrypted)
- Authentication (hashes alone don't prove ownership)

## License

MIT License - see LICENSE file

## Author

**Luke Steuber**

- Website: [lukesteuber.com](https://lukesteuber.com)
- GitHub: [@lukeslp](https://github.com/lukeslp)
- Bluesky: [@lukesteuber.com](https://bsky.app/profile/lukesteuber.com)

---

**Fun fact**: The name "namecrawler" reflects how the tool "crawls" through file content to generate a name, rather than using metadata or user input.
