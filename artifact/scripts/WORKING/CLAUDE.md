# CLAUDE.md
<!-- Navigation: ~/projects/WORKING/CLAUDE.md -->
<!-- Parent: ~/projects/CLAUDE.md -->
<!-- Map: ~/CLAUDE_MAP.md -->

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Standalone, single-purpose Python scripts following Unix philosophy: do one thing well, be composable via stdin/stdout/JSON. No shared state between scripts.

## Running Scripts

```bash
python script_name.py --help        # Every script supports --help
python arxiv_search.py "topic"      # Typical usage: positional args
python xai_tools.py chat "prompt"   # Subcommand pattern (xai_tools only)
python company-research.py          # Interactive prompt (no args)
```

V2 scripts need the shared library:
```bash
export PYTHONPATH=/home/coolhand/shared:$PYTHONPATH
python perplexity_multi_v2.py "query"
```

## Architecture

**14 main scripts** + **11 clinical tools** in `to_test/`.

All scripts are independent — no imports between them. Dependencies are per-script:

| Script | Key Deps | API Key Env Var |
|--------|----------|-----------------|
| `xai_tools.py` | openai, PIL (optional), colorama (optional) | `XAI_API_KEY` |
| `xnamer.py` | openai, rich, PIL, cv2 | `XAI_API_KEY` |
| `arxiv_search.py` | arxiv | none |
| `perplexity-multi.py` | requests | `PERPLEXITY_API_KEY` |
| `company-research.py` | requests, concurrent.futures | `PERPLEXITY_API_KEY` |
| `ping_*.py` | requests/openai | respective provider key |
| `gtts_cli.py` | gtts | none |
| `time_calc.py` | pytz | none |
| `file_info.py` | stdlib only | none |

API keys: `/home/coolhand/documentation/API_KEYS.md`

### Notable Scripts

- **`company-research.py`** (169KB) — 25-agent hierarchical research system with 5 pods, pod managers, and final synthesis. Uses `concurrent.futures` for parallel execution against Perplexity API. Interactive prompts for company name.
- **`xai_tools.py`** (70KB) — Swiss army knife: chat, alt-text generation, arxiv search via xAI/Grok. Uses OpenAI client pointed at xAI endpoint.
- **`xnamer.py`** — Vision-powered file renamer using Grok-2 Vision. Extracts video frames with cv2, has undo via JSON rename log.

### V2 Scripts

Thin wrappers around `/home/coolhand/shared/utils/` modules. Original versions work without the shared library and are the safer choice.

### `to_test/` Clinical Tools

11 scripts for auditing clinical reference documentation at `/servers/clinical/`. All take a `project_root` path and operate on a `conditions/` subdirectory within it. Class-based pattern (e.g., `ClinicalQualityAuditor`).

## Patterns To Follow

- Shebang: `#!/usr/bin/env python3`
- Use `argparse` for CLI args
- Optional deps: try/except import with graceful fallback (see `xai_tools.py` for pattern)
- Output: stdout for data, stderr for progress/errors
- Exit codes: 0 success, 1 failure
