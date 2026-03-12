# WORKING - Composable Single-Task Scripts

This directory contains standalone, single-purpose scripts designed to be easily composed together in workflows.

## Philosophy

Each script should:
- **Do one thing well** - Single, clear purpose
- **Be composable** - Easy to pipe or chain with other tools
- **Have clear I/O** - Well-defined inputs and outputs
- **Be self-documenting** - Include help text and examples
- **Handle errors gracefully** - Clean error messages

## Current Scripts (25 total)

### API Testing & Connectivity (3 scripts) 
All production-ready, no dependencies issues:
- `ping_xai.py` - Test XAI/Grok API connectivity
- `ping_openai.py` - Test OpenAI API connectivity
- `ping_mistral.py` - Test Mistral AI API connectivity

### Search & Research (3 scripts) 
- `arxiv_search.py` - ✅ Working (Nov 18, 2025: arxiv installed)
- `perplexity-multi.py` - ✅ Working (Perplexity AI search)
- `company-research.py` - ✅ Working (25-agent research, interactive)

### Utilities (4 scripts) 
Production-ready:
- `file_info.py` - Detailed file/directory information (no dependencies)
- `time_calc.py` - Time zone calculator (uses pytz)
- `gtts_cli.py` - Google Text-to-Speech CLI
- `xai_tools.py` - ⚠️ XAI utilities (chat, alt-text, arxiv) - arxiv optional

### LLM-Powered Tools (2 scripts)
- `xnamer.py` - ✅ Working (Nov 18, 2025: opencv-python installed)
- `xai_tools.py` - ✅ Working (chat, alt-text, arxiv features)

### V2 Scripts (Shared Library) ⚠️
Scripts using `/home/coolhand/shared/utils/` (code reduction):
- `xnamer_v2.py` - ⚠️ Needs utils module setup (72% reduction)
- `time_calc_v2.py` - ⚠️ Needs utils module setup (12% reduction)
- `perplexity_multi_v2.py` - ⚠️ Needs utils module setup (42% reduction)

**Status:** Shared library exists but module import path needs configuration  
**Note:** Original versions work fine, v2 versions are optimizations

### Clinical Tools (`to_test/` - 11 scripts) ✅

**Status:** All scripts fixed (Nov 18, 2025)

#### All Working (11 scripts)
- `audit_conditions.py` - Quality audit
- `bulk_convert_conditions.py` - MD to HTML conversion
- `convert_resources.py` - Resource HTML generation
- `quality_dashboard.py` - Dashboard (functions are intentional stubs for future)
- `analyze_content_gaps.py` - ✅ Path fixed
- `citation_validator.py` - ✅ Path fixed
- `comprehensive_quality_audit.py` - ✅ Path fixed
- `content_gap_analyzer.py` - ✅ Path fixed
- `generate_action_plan.py` - ✅ Path fixed
- `generate_markdown_report.py` - ✅ Path fixed
- `citation_audit.py` - ✅ Path & regex fixed

**All scripts now use correct path:** `/servers/clinical/`

## Usage Patterns

### Basic Usage
```bash
# Single script
./arxiv_search.py "quantum computing"

# Check API connectivity
./ping_xai.py

# File information
./file_info.py /path/to/file
```

### Composition Examples
```bash
# Chain scripts together
./arxiv_search.py "machine learning" | ./file_info.py -

# Use in workflows
for paper in $(./arxiv_search.py "machine learning" --ids-only); do
    ./process_paper.py "$paper"
done
```

### With WORKING Scripts

Many scripts can work together:
- Search tools can feed into analysis tools
- API ping tools verify connectivity before processing
- File tools can validate inputs/outputs

## Adding New Scripts

When adding a script to WORKING:

1. **Make it executable**: `chmod +x script.py`
2. **Add shebang**: `#!/usr/bin/env python3`
3. **Include docstring**: Clear description at top
4. **Add --help**: Use argparse or similar
5. **Test independently**: Should work standalone
6. **Document here**: Add to this README

## Related Directories

- `/projects/scripts/` - Larger script collections and packages
- `/projects/swarm/` - Complex multi-agent orchestration
- `/projects/beltalowda/` - Multi-agent task platform

## Script Standards

### CLI Interface
```python
#!/usr/bin/env python3
"""
Script Name - Brief description

Purpose: What this script does
Input: What it expects
Output: What it produces
"""

import argparse

def main():
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument('input', help="Input description")
    # ... more args
    args = parser.parse_args()
    
    # Do the thing
    result = process(args.input)
    
    # Output result
    print(result)

if __name__ == "__main__":
    main()
```

### Error Handling
```python
import sys

try:
    result = risky_operation()
except SpecificError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

### Input/Output
- **stdin/stdout** for pipeline compatibility
- **JSON output** for structured data
- **Exit codes** for success/failure signaling
- **Progress to stderr** to preserve stdout

## Test Results Summary

**Last Tested:** November 18, 2025

**Main Scripts (14):**
- Working: 9 (64%)
- ❌ Needs deps: 5 (36%)

**to_test Scripts (11):**
- Working: 4 (36%)
- ❌ Needs path fix: 7 (64%)

**See:** [../WORKING_SCRIPTS_TEST_REPORT.md](../WORKING_SCRIPTS_TEST_REPORT.md) for detailed results

---

## Quick Fixes

### Install Missing Dependencies
```bash
# For arxiv_search.py and xai_tools.py
pip install arxiv

# For xnamer.py
pip install opencv-python pillow

# Investigate utils module for v2 scripts
# May need to create or locate utils.py
```

### Fix Clinical Script Paths
```bash
cd /home/coolhand/projects/WORKING/to_test

# Fix all at once
sed -i 's|/home/coolhand/projects/clinical|/home/coolhand/servers/clinical|g' \
  analyze_content_gaps.py citation_validator.py comprehensive_quality_audit.py \
  content_gap_analyzer.py generate_action_plan.py generate_markdown_report.py

# Fix regex warning
sed -i "s/'\\\Z'/'\\\\\\\Z'/g" citation_audit.py
```

---

## Maintenance

- **Scripts tested:** November 18, 2025 (comprehensive)
- **Dependencies:** Documented in test report
- **Path issues:** Identified and fix provided
- **Production-ready:** 13/25 scripts (52%)

---

**Last Updated:** November 18, 2025  
**Total Scripts:** 14 (main) + 11 (to_test) = 25 total  
**Status:** 52% production-ready, 48% needs minor fixes
