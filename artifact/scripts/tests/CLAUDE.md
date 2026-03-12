# CLAUDE.md
<!-- Navigation: ~/projects/tests/CLAUDE.md -->
<!-- Parent: ~/projects/CLAUDE.md -->
<!-- Map: ~/CLAUDE_MAP.md -->

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Cross-project test suite for the development ecosystem. Individual projects also have their own test directories.

## Structure

```
tests/
├── conftest.py               # Shared fixtures (Beltalowda, Swarm, xAI Swarm)
├── unit/
│   └── test_core_functionality.py
└── integration/
    └── test_platform_integration.py
```

## Commands

```bash
cd /home/coolhand/projects/tests
pytest                           # All tests
pytest unit/                     # Unit only
pytest integration/              # Integration only
pytest -v                        # Verbose
```

## Notes

- `conftest.py` adds the project root to `sys.path` and provides mock fixtures for LLM providers
- Tests cover Beltalowda, Swarm, and xAI integration platforms
- Individual project tests live in their own directories (e.g., `wordblocks/tests/`, `social-scout/tests/`)
