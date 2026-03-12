"""Command-line interface for namecrawler.

Renames files based on the SHA256 hash of their contents.
This is an example tool for demonstration purposes.
"""
import argparse
from pathlib import Path
import hashlib


def sha256sum(path: Path) -> str:
    """Return the SHA256 hash of a file."""
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def rename_file(path: Path) -> Path:
    """Rename a file using its SHA256 hash."""
    new_name = sha256sum(path) + path.suffix
    new_path = path.with_name(new_name)
    path.rename(new_path)
    return new_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path, help='Files to rename')
    args = parser.parse_args(argv)

    for file in args.files:
        if file.is_file():
            new_path = rename_file(file)
            print(f"Renamed {file} -> {new_path}")
        else:
            print(f"Skipping {file}, not a file")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
