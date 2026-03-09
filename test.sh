#!/usr/bin/env bash
# ============================================================================
# test.sh — Smoke tests for aivia lib/
# Usage: bash test.sh
# ============================================================================

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PASS=0
FAIL=0

test_module() {
    local name="$1"
    shift
    if bash -c "$*" >/dev/null 2>&1; then
        printf "  [\033[32m✓\033[0m] %s\n" "$name"
        PASS=$((PASS + 1))
    else
        printf "  [\033[31m✗\033[0m] %s\n" "$name"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "aivia — smoke tests"
echo "━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  lib/ modules:"

test_module "core.sh loads" \
    'source lib/core.sh && [ -n "$AIVIA_LIB_DIR" ] && [ -n "$CONTENT_WIDTH" ]'

test_module "core.sh sleep_ms" \
    'source lib/core.sh && sleep_ms 1'

test_module "core.sh random_int" \
    'source lib/core.sh && r=$(random_int 1 10) && [ "$r" -ge 1 ] && [ "$r" -le 10 ]'

test_module "core.sh source_lib" \
    'source lib/core.sh && source_lib style'

test_module "core.sh source_theme" \
    'source lib/core.sh && source_lib style && source_theme entity'

test_module "core.sh double-source guard" \
    'source lib/core.sh && source lib/core.sh'

test_module "style.sh loads" \
    'source lib/core.sh && source_lib style && [ -n "$RESET" ] && [ -n "$BOLD" ]'

test_module "style.sh color_256" \
    'source lib/core.sh && source_lib style && c=$(color_256 255 0 0) && [ "$c" -ge 16 ]'

test_module "style.sh supports_256_color" \
    'source lib/core.sh && source_lib style && supports_256_color'

test_module "terminal.sh loads" \
    'source lib/core.sh && source_lib style terminal && type -t hide_cursor >/dev/null'

test_module "terminal.sh center_col" \
    'source lib/core.sh && source_lib style terminal && c=$(center_col "test") && [ "$c" -gt 0 ]'

test_module "text.sh loads" \
    'source lib/core.sh && source_lib style terminal text && type -t type_text >/dev/null'

test_module "text.sh wrap_text" \
    'source lib/core.sh && source_lib style terminal text && lines=$(wrap_text "aaa bbb ccc" 8 | wc -l) && [ "$lines" -ge 2 ]'

test_module "text.sh truncate_text" \
    'source lib/core.sh && source_lib style terminal text && t=$(truncate_text "hello world" 8) && [ "${#t}" -le 8 ]'

test_module "text.sh center_text" \
    'source lib/core.sh && source_lib style terminal text && center_text "hi" >/dev/null'

test_module "divider.sh loads" \
    'source lib/core.sh && source_lib style terminal divider && type -t divider >/dev/null'

test_module "divider.sh thin" \
    'source lib/core.sh && source_lib style terminal divider && divider thin >/dev/null'

test_module "divider.sh divider_text" \
    'source lib/core.sh && source_lib style terminal divider && divider_text "test" >/dev/null'

test_module "box.sh loads" \
    'source lib/core.sh && source_lib style terminal box && type -t draw_box >/dev/null'

test_module "box.sh draw_box" \
    'source lib/core.sh && source_lib style terminal box && draw_box 10 5 single >/dev/null'

test_module "box.sh draw_box_text" \
    'source lib/core.sh && source_lib style terminal box && draw_box_text "hi" rounded >/dev/null'

test_module "box.sh draw_header" \
    'source lib/core.sh && source_lib style terminal box && draw_header "test" heavy >/dev/null'

test_module "progress.sh loads" \
    'source lib/core.sh && source_lib style progress && type -t progress_bar >/dev/null'

test_module "progress.sh progress_bar" \
    'source lib/core.sh && source_lib style progress && progress_bar 5 10 >/dev/null'

test_module "progress.sh checklist_item" \
    'source lib/core.sh && source_lib style progress && checklist_item "test" done >/dev/null'

test_module "progress.sh install_line" \
    'source lib/core.sh && source_lib style progress && install_line "pkg@1.0" >/dev/null'

test_module "animation.sh loads" \
    'source lib/core.sh && source_lib style terminal animation && type -t sweep_down >/dev/null'

test_module "animation.sh flash_screen fn exists" \
    'source lib/core.sh && source_lib style terminal animation && type -t flash_screen >/dev/null'

test_module "ascii.sh loads" \
    'source lib/core.sh && source_lib style terminal ascii && type -t render_art >/dev/null'

test_module "ascii.sh render_art" \
    'source lib/core.sh && source_lib style terminal ascii && render_art "test art" >/dev/null'

echo ""
echo "  theme/:"

test_module "entity.sh loads" \
    'source lib/core.sh && source_lib style && source_theme entity && [ -n "$ENTITY_FG" ]'

test_module "entity.sh random_frame_char" \
    'source lib/core.sh && source_lib style && source_theme entity && c=$(random_frame_char) && [ -n "$c" ]'

test_module "entity.sh entity_divider" \
    'source lib/core.sh && source_lib style && source_theme entity && entity_divider 10 >/dev/null'

echo ""
echo "  scripts/:"

test_module "manifest.sh help" \
    'bash scripts/manifest.sh help >/dev/null'

test_module "voice.sh clear" \
    'bash scripts/voice.sh "test" clear >/dev/null'

echo ""
echo "━━━━━━━━━━━━━━━━━━━"
echo "  Results: ${PASS} passed, ${FAIL} failed"
echo ""

[ "$FAIL" -eq 0 ] && exit 0 || exit 1
