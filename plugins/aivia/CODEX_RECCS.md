# CODEX_RECCS

Recommendations for enriching [`files/detect.sh`](/home/coolhand/projects/aivia/plugins/aivia/files/detect.sh) while preserving the current privacy boundary and narrative intent.

## Scope

The current script is a reasonable install-time environment snapshot for personalization, but it has a few implementation risks and leaves useful terminal-context data on the table.

This document captures:

- current weaknesses
- recommended enrichments
- a concrete implementation plan
- a prompt to resume work from this file

## Current Weaknesses

### 1. Unsafe shell-to-Python interpolation

At [`files/detect.sh:105`](/home/coolhand/projects/aivia/plugins/aivia/files/detect.sh#L105), shell variables are injected directly into embedded Python source. Values containing quotes, backslashes, or newlines can break parsing or produce malformed JSON state.

Recommendation:

- pass data to Python through environment variables, stdin, or a temporary JSON blob
- avoid interpolating arbitrary shell strings directly into Python code

### 2. Noisy process detection

At [`files/detect.sh:59`](/home/coolhand/projects/aivia/plugins/aivia/files/detect.sh#L59), the script converts process names into a single comma-separated string and then does substring matching with `grep`.

Problems:

- false positives for short names like `arc` or `code`
- inconsistent matching because `ps -eo comm` can truncate names
- duplicate or variant labels such as `steam` and `Steam`

Recommendation:

- collect process names as normalized tokens
- map aliases to canonical names
- perform exact or anchored matching where possible

### 3. Full replacement of `environment`

At [`files/detect.sh:111`](/home/coolhand/projects/aivia/plugins/aivia/files/detect.sh#L111), the script overwrites `state["environment"]` entirely.

Problems:

- future fields cannot be preserved automatically
- schema evolution is brittle
- metadata like capture version/timestamps cannot persist cleanly

Recommendation:

- merge into the existing object
- add a schema version field

### 4. Silent failure during install

At [`files/install.sh:257`](/home/coolhand/projects/aivia/plugins/aivia/files/install.sh#L257), detection runs in the background and install only watches for process exit. If detection fails, install still prints `done`.

Recommendation:

- wait on the process and check exit status
- optionally log a warning or write a detection status field into state

## Recommended Enrichments

These additions stay within the stated privacy model: process names, terminal/env data, hostname, and local system metadata only. No file inspection, browsing history, network access, or elevated permissions.

### Terminal capability detection

High value because the planning docs already call for fallback-aware rendering in `manifest.sh`.

Add fields such as:

- `tty`: whether stdout is a TTY
- `tmux`: whether running inside tmux
- `screen_session`: whether running inside GNU screen
- `ssh`: whether session appears to be remote via `SSH_CONNECTION` or related env vars
- `color_count`: from `tput colors`
- `truecolor`: heuristic from `COLORTERM=truecolor|24bit`
- `unicode_safe`: heuristic from locale like `UTF-8`

Use cases:

- tone down effects on low-color terminals
- avoid layout assumptions in small or non-interactive terminals
- choose ASCII-only fallback if Unicode support looks weak

### Capture metadata

Add:

- `captured_at` in UTC ISO 8601
- `timezone`
- `weekday`
- `is_weekend`

Use cases:

- cleaner narrative references than only `hour`
- better state introspection during debugging

### Platform detail

Add:

- `arch` from `uname -m`
- `kernel` from `uname -r`
- distro `id` and `version_id` from `/etc/os-release` where available

Use cases:

- future terminal/render quirks by platform
- debugging odd install behavior across macOS/Linux variants

### Derived activity summary

The current arrays are useful, but narrative code will benefit more from an interpretation layer.

Add:

- `primary_activity`: one of `coding`, `gaming`, `browsing`, `music`, `mixed`, `idle`
- `activity_signals`: counts by category

Use cases:

- easier narrative branching
- less duplication elsewhere when deciding what to reference

### Canonicalized app names

Normalize detected apps into canonical labels.

Examples:

- `code`, `code-insiders` -> `VS Code`
- `cursor` -> `Cursor`
- `spotify` -> `Spotify`
- `firefox` -> `Firefox`

Benefits:

- cleaner personalization text
- less downstream casing/alias cleanup

### Schema versioning

Add:

- `schema_version`
- optional `detection_status`

Benefits:

- safer future migrations
- easier debugging if older installs exist

## Proposed `environment` Shape

```json
{
  "environment": {
    "schema_version": 2,
    "detection_status": "ok",
    "captured_at": "2026-03-12T18:42:00Z",
    "username": "coolhand",
    "hostname": "workstation",
    "os": "Linux",
    "os_release": "Ubuntu 24.04 LTS",
    "arch": "x86_64",
    "kernel": "6.8.0",
    "distro_id": "ubuntu",
    "distro_version_id": "24.04",
    "terminal": "vscode",
    "term_type": "xterm-256color",
    "shell": "bash",
    "timezone": "America/Chicago",
    "hour": 18,
    "weekday": "Thursday",
    "time_context": "evening",
    "is_weekend": false,
    "screen_cols": 140,
    "screen_rows": 42,
    "tty": true,
    "tmux": false,
    "screen_session": false,
    "ssh": false,
    "color_count": 256,
    "truecolor": true,
    "unicode_safe": true,
    "locale": "en_US.UTF-8",
    "detected_games": ["Steam"],
    "detected_editors": ["VS Code", "Cursor"],
    "detected_music": ["Spotify"],
    "detected_browsers": ["Firefox"],
    "activity_signals": {
      "games": 1,
      "editors": 2,
      "music": 1,
      "browsers": 1
    },
    "primary_activity": "coding"
  }
}
```

## Implementation Plan

### Phase 1. Make the current script safe

1. Refactor the embedded Python block to read values from environment variables instead of inline shell interpolation.
2. Ensure `STATE_FILE` existence is validated before reading.
3. Replace full `environment` replacement with merge behavior.
4. Add `schema_version` and `captured_at`.

Acceptance criteria:

- usernames/locales with quotes do not break the script
- existing unknown `environment` keys survive reruns

### Phase 2. Improve process classification

1. Gather process names into a normalized list rather than one comma-separated string.
2. Introduce alias maps for editors, browsers, music, and games.
3. Canonicalize labels and dedupe output arrays.
4. Derive `activity_signals` and `primary_activity`.

Acceptance criteria:

- output arrays contain canonical human-readable names
- obvious false positives from short substrings are reduced

### Phase 3. Add terminal capability detection

1. Detect `tty`, `tmux`, `screen_session`, and `ssh`.
2. Detect `color_count`, `truecolor`, and `unicode_safe`.
3. Preserve current `screen_cols` and `screen_rows`, but guard them for non-interactive environments.

Acceptance criteria:

- script returns sensible defaults in headless/non-TTY installs
- data is sufficient to drive fallback logic in `manifest.sh`

### Phase 4. Add platform/time metadata

1. Capture `arch`, `kernel`, `timezone`, `weekday`, and `is_weekend`.
2. Optionally parse distro `ID` and `VERSION_ID` from `/etc/os-release`.

Acceptance criteria:

- fields are present on Linux and degrade gracefully on macOS

### Phase 5. Improve install integration

1. Update [`files/install.sh`](/home/coolhand/projects/aivia/plugins/aivia/files/install.sh#L257) to `wait` on the detection subprocess.
2. If detection fails, print a subdued warning or write `detection_status: "failed"` into state.
3. Keep the user-facing install flow quiet unless debugging is needed.

Acceptance criteria:

- install no longer reports success if detection crashes immediately

### Phase 6. Wire rendering fallbacks

After `detect.sh` is enriched, use the new fields in:

- [`files/manifest.sh`](/home/coolhand/projects/aivia/plugins/aivia/files/manifest.sh)
- [`files/voice.sh`](/home/coolhand/projects/aivia/plugins/aivia/files/voice.sh)

Suggested follow-up behavior:

- degrade from 256-color palettes when `color_count` is low
- avoid heavy Unicode frames when `unicode_safe` is false
- reduce layout assumptions for very narrow terminals

## Suggested Implementation Notes

- Keep the privacy note in `detect.sh` explicit and accurate.
- Prefer deterministic canonical names over raw process labels.
- Keep all new fields optional-by-default in downstream readers.
- Do not probe beyond install-time data collection unless the design changes intentionally.

## Ready-to-Use Continue Prompt

Use this in a future Codex session to resume directly from this document:

```text
Read /home/coolhand/projects/aivia/plugins/aivia/CODEX_RECCS.md and implement the detect.sh improvements described there.

Constraints:
- preserve the current privacy boundary
- keep changes compatible with existing state.json consumers
- start with Phase 1 and Phase 2 from the implementation plan
- also update install.sh so detection failure is not silently reported as success
- run any reasonable local verification you can

When finished, summarize:
1. what changed
2. any schema additions
3. any remaining follow-up work for manifest.sh/voice.sh
```

## Short Version

If only one pass is going to happen, the highest-value subset is:

1. safe Python handoff
2. canonicalized process detection
3. terminal capability detection
4. schema versioning
5. install-time failure handling
