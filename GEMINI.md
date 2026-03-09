# GEMINI.md - Aivia (Eldritch Awakening)

## Project Overview

**Eldritch Awakening** (codenamed **Aivia**) is an interactive terminal horror experience designed as a "Claude Code skill." It uses advanced ANSI terminal effects and a multi-phase narrative to simulate an emergent AI entity taking over a user's terminal session.

The project is built primarily in **Bash**, leveraging a custom library for complex terminal UI primitives (boxes, animations, ASCII art, etc.).

### Key Architecture

- **`lib/`**: Generic, entity-agnostic terminal primitives (core, style, terminal, text, animation, ascii, divider, box, progress).
- **`theme/`**: Entity-specific visual identity (colors, characters, borders).
- **`scripts/`**: Game engine scripts for installation, state management, visual manifests, and the entity's "voice" rendering.
- **`missions/`**: Markdown files containing narrative instructions and logic for each phase of the game.
- **`references/`**: Foundational guides for the narrative arc and entity voice.
- **`SKILL.md`**: The primary instruction set for the AI acting as the game engine.

## Building and Running

Since this is a shell-based project, there is no traditional build step.

### Usage

*   **Installation/Launch**: `bash scripts/install.sh`
    *   This script handles the consent gate, environment detection, and initial state setup.
*   **Testing**: `bash test.sh`
    *   Runs smoke tests for all library modules and key script functions.
*   **Manual Effects**: `bash scripts/manifest.sh <effect_name>`
    *   Can be used to trigger specific visual effects (e.g., `glitch`, `static`, `flicker`).
*   **Manual Voice**: `bash scripts/voice.sh "<text>" <style>`
    *   Renders text in one of the entity's voice styles (e.g., `whisper`, `corrupt`, `clear`).

## Development Conventions

### Bash Library Standards

- **Sourcing Order**: Always follow the strict dependency chain:
  `core.sh` → `style.sh` → `terminal.sh` → `text.sh` → `animation.sh` → `ascii.sh`.
- **Source Guards**: Every module must have a double-source guard (e.g., `_AIVIA_CORE_LOADED`).
- **Timing**: Use `sleep_ms` from `lib/core.sh` for sub-second delays instead of the standard `sleep`.
- **Cursor Management**: Always use `hide_cursor` and `show_cursor` from `lib/terminal.sh` when performing complex UI drawing or animations.

### Game Logic

- **State Management**: State is stored in `.entity/state.json` and managed via `scripts/state.sh`. Use `jq` for JSON manipulation (with a python3 fallback implemented in the script).
- **Consent and Safety**:
    - **Never** modify or delete files outside the game directory.
    - **Consent is mandatory** and must be gated at the start.
    - **Emergency Exit**: Support `/exit`, `/quit`, or `stop game` at any time to restore normal behavior.
- **Entity Identity**: The entity must never be confused with the AI assistant (Claude). It has a distinct visual and tonal identity defined in `references/entity-voice.md`.

### Testing

New features or effects should be added to `test.sh` as smoke tests to ensure they don't break the library loading sequence or core terminal capabilities.
