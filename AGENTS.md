# Repository Guidelines

## Project Structure & Module Organization
`aivia` is a Bash-based interactive terminal experience packaged as a skill. Core terminal primitives live in `lib/`, entity-specific styling lives in `theme/`, and gameplay/runtime scripts live in `scripts/`. Narrative phase content is stored in `missions/`, writing references in `references/`, and static art in `ascii/`. Primary entrypoints are [`scripts/install.sh`](/home/coolhand/projects/aivia/scripts/install.sh), [`scripts/manifest.sh`](/home/coolhand/projects/aivia/scripts/manifest.sh), and [`test.sh`](/home/coolhand/projects/aivia/test.sh).

## Build, Test, and Development Commands
Run `bash test.sh` for the project smoke suite; it validates that lib modules load and key public functions still work. Use `bash scripts/manifest.sh help` to inspect available visual effects and `bash scripts/state.sh help` when extending state operations. For installation flow testing, run `bash scripts/install.sh` inside a disposable directory, since it creates `.entity/`, `workspace/`, and copied assets.

## Coding Style & Naming Conventions
Use Bash with `#!/usr/bin/env bash` and `set -euo pipefail` for executable scripts. Follow the existing style: 4-space indentation, uppercase readonly/global constants, and snake_case for functions such as `sleep_ms`, `source_lib`, and `effect_glitch`. Keep reusable terminal logic in `lib/`, not in gameplay scripts. Preserve the dependency order documented in `CLAUDE.md`: `core.sh` must be sourced before other lib modules, and theme files should load through `source_theme`.

## Testing Guidelines
This repository currently uses smoke tests rather than a full framework. Add new coverage to `test.sh` by extending `test_module` checks with concise names like `"box.sh draw_box_text"`. Favor tests that verify exported functions, load order, and non-interactive output behavior. Run `bash test.sh` before opening a PR.

## Commit & Pull Request Guidelines
Recent history uses timestamped `session checkpoint: YYYY-MM-DD HH:MM` commits. For contributor work, prefer short imperative subjects that describe the change, for example `add heartbeat effect guard` or `document state commands`. PRs should include a brief summary, affected paths, test results, and screenshots or terminal captures when changing visual effects or install flow output.

## Safety & Game Constraints
Do not add behavior that writes outside the selected game directory. Keep entity effects theatrical only: no destructive commands, no network access, and no probing beyond data intentionally captured by `scripts/detect.sh`.
