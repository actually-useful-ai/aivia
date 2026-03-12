# CLAUDE.md
<!-- Navigation: ~/projects/scripts/CLAUDE.md -->
<!-- Parent: ~/projects/CLAUDE.md -->
<!-- Map: ~/CLAUDE_MAP.md -->

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Automation scripts and utilities organized by category. Most are Python, some Bash.

## Directory Structure

```
scripts/
├── api-tools/          # API testing utilities
├── packages/           # Package management scripts
├── schema/             # Schema/data-spec tools
├── snippets/           # Code snippets and templates
├── tools/              # General utilities
├── needs_testing/      # Unverified scripts
└── publish_package.sh  # PyPI publishing script
```

## Usage

```bash
cd /home/coolhand/projects/scripts/<category>
python script_name.py [arguments]

# Publish to PyPI
./publish_package.sh package_name
```

## Notes

- Scripts may have varying levels of testing -- check `needs_testing/` for unverified ones
- Prefer `/home/coolhand/shared/` for reusable implementations
- Single-purpose composable scripts live in `../WORKING/` instead
