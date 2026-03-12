#!/usr/bin/env python3
"""
Time Zone Calculator CLI (v2 - using shared/utils)

Thin CLI wrapper around shared/utils/time_utils.py for timezone operations.

Usage:
    python time_calc_v2.py --convert --time "2025-01-15 14:30:00" --from "America/New_York" --to "Asia/Tokyo"
    python time_calc_v2.py --diff --time1 "2025-01-15 09:00:00" --time2 "2025-01-15 17:30:00" --timezone "UTC"
    python time_calc_v2.py --add --time "2025-01-15 14:00:00" --duration "2d3h" --timezone "America/Los_Angeles"
    python time_calc_v2.py --list
    python time_calc_v2.py --interactive

Author: Luke Steuber
"""

import sys
import argparse
from pathlib import Path

# Add shared library to path
sys.path.insert(0, str(Path.home() / "shared"))

try:
    from utils import (
        TimeUtilities,
        convert_timezone,
        calculate_difference,
        add_time,
        list_timezones
    )
except ImportError as e:
    print(f"Missing required package: {e}")
    print("\nInstall required packages with:")
    print("pip install pytz")
    sys.exit(1)


def display_timezone_list(filter_text=None):
    """Display available timezones in formatted output."""
    timezones = list_timezones(filter_text)

    print(f"\n{'='*70}")
    print(f"Available Timezones{f' (filtered by {filter_text})' if filter_text else ''}")
    print('='*70)

    # Group by region
    by_region = {}
    for tz in timezones:
        parts = tz.split('/')
        region = parts[0] if len(parts) > 1 else 'Other'
        if region not in by_region:
            by_region[region] = []
        by_region[region].append(tz)

    for region in sorted(by_region.keys()):
        print(f"\n{region}:")
        for tz in sorted(by_region[region]):
            print(f"  • {tz}")

    print(f"\n{'='*70}")
    print(f"Total: {len(timezones)} timezone(s)")
    print('='*70)


def display_conversion(time_str, from_tz, to_tz):
    """Display timezone conversion result."""
    try:
        print(f"\n🔄 Converting timezone...")

        result = convert_timezone(time_str, from_tz, to_tz)

        print(f"\n✅ Conversion result:")
        print(f"{'='*70}")
        print(f"From: {result.original_time.strftime('%Y-%m-%d %H:%M:%S')} {from_tz}")
        print(f"To:   {result.converted_time.strftime('%Y-%m-%d %H:%M:%S')} {to_tz}")
        print(f"Offset: {result.offset_hours:.1f} hours")
        print('='*70)
        return True

    except ValueError as e:
        print(f"❌ Error: Invalid time format. Use YYYY-MM-DD HH:MM:SS or 'now'")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def display_difference(time1, time2, timezone):
    """Display time difference calculation."""
    try:
        print(f"\n📊 Calculating time difference...")

        result = calculate_difference(time1, time2, timezone)

        print(f"\n✅ Time difference:")
        print(f"{'='*70}")
        print(f"From:  {time1} {timezone}")
        print(f"To:    {time2} {timezone}")
        print(f"Difference: {result.total_hours:.2f} hours")
        print(f"Breakdown: {result.days}d {result.hours}h {result.minutes}m {result.seconds}s")
        print('='*70)
        return True

    except ValueError as e:
        print(f"❌ Error: Invalid time format. Use YYYY-MM-DD HH:MM:SS")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def display_addition(time_str, duration, timezone):
    """Display time addition result."""
    try:
        print(f"\n➕ Adding duration to time...")

        # Parse base time first to display it
        from datetime import datetime
        if time_str.lower() == 'now':
            base = datetime.now()
        else:
            base = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

        # Add duration
        end_time = add_time(time_str, duration, timezone)

        print(f"\n✅ Result:")
        print(f"{'='*70}")
        print(f"Start: {base.strftime('%Y-%m-%d %H:%M:%S')} {timezone}")
        print(f"Duration: {duration}")
        print(f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S')} {timezone}")
        print('='*70)
        return True

    except ValueError as e:
        print(f"❌ Error: Invalid duration format. Use XdYhZm (e.g., 1d2h30m)")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def interactive_mode():
    """Interactive mode for time calculations."""
    print("\n" + "="*70)
    print("Time Zone Calculator - Interactive Mode")
    print("="*70)
    print("\nCommands:")
    print("  convert - Convert time between timezones")
    print("  diff    - Calculate time difference")
    print("  add     - Add duration to time")
    print("  list    - List available timezones")
    print("  help    - Show this help")
    print("  exit    - Exit interactive mode")
    print("="*70 + "\n")

    while True:
        try:
            command = input("Command: ").strip().lower()

            if command in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break

            if command == 'help':
                print("\nAvailable commands:")
                print("  convert - Convert time between timezones")
                print("  diff    - Calculate time difference")
                print("  add     - Add duration to time")
                print("  list    - List available timezones")
                print("  exit    - Exit interactive mode\n")
                continue

            if command == 'convert':
                time_str = input("Time (YYYY-MM-DD HH:MM:SS or 'now'): ").strip()
                from_tz = input("From timezone: ").strip()
                to_tz = input("To timezone: ").strip()
                display_conversion(time_str, from_tz, to_tz)

            elif command == 'diff':
                time1 = input("First time (YYYY-MM-DD HH:MM:SS): ").strip()
                time2 = input("Second time (YYYY-MM-DD HH:MM:SS): ").strip()
                timezone = input("Timezone: ").strip()
                display_difference(time1, time2, timezone)

            elif command == 'add':
                time_str = input("Base time (YYYY-MM-DD HH:MM:SS or 'now'): ").strip()
                duration = input("Duration (e.g., 1d2h30m): ").strip()
                timezone = input("Timezone: ").strip()
                display_addition(time_str, duration, timezone)

            elif command == 'list':
                filter_text = input("Filter (optional): ").strip() or None
                display_timezone_list(filter_text)

            else:
                print("❌ Unknown command. Type 'help' for available commands.")

            print()

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")


def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(
        description="Time zone calculator and converter (v2 - using shared/utils)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert time between timezones
  %(prog)s --convert --time "2025-01-15 14:30:00" --from "America/New_York" --to "Asia/Tokyo"

  # Calculate time difference
  %(prog)s --diff --time1 "2025-01-15 09:00:00" --time2 "2025-01-15 17:30:00" --timezone "UTC"

  # Add duration to time
  %(prog)s --add --time "2025-01-15 14:00:00" --duration "2d3h" --timezone "America/Los_Angeles"

  # List timezones
  %(prog)s --list

  # Interactive mode
  %(prog)s --interactive

Note: This is a thin wrapper around shared/utils/time_utils.py
        """
    )

    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--list", action="store_true", help="List all available timezones")
    parser.add_argument("--filter", help="Filter timezones by text")
    parser.add_argument("--convert", action="store_true", help="Convert time between timezones")
    parser.add_argument("--diff", action="store_true", help="Calculate time difference")
    parser.add_argument("--add", action="store_true", help="Add duration to time")
    parser.add_argument("--time", help="Time value (YYYY-MM-DD HH:MM:SS or 'now')")
    parser.add_argument("--time1", help="First time value (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--time2", help="Second time value (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--from", dest="from_tz", help="Source timezone")
    parser.add_argument("--to", dest="to_tz", help="Target timezone")
    parser.add_argument("--timezone", help="Timezone")
    parser.add_argument("--duration", help="Duration (format: XdYhZm, e.g., 1d2h30m)")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        sys.exit(0)

    if args.list:
        display_timezone_list(args.filter)
        sys.exit(0)

    if args.convert:
        if not all([args.time, args.from_tz, args.to_tz]):
            print("Error: --convert requires --time, --from, and --to")
            sys.exit(1)
        success = display_conversion(args.time, args.from_tz, args.to_tz)
        sys.exit(0 if success else 1)

    if args.diff:
        if not all([args.time1, args.time2, args.timezone]):
            print("Error: --diff requires --time1, --time2, and --timezone")
            sys.exit(1)
        success = display_difference(args.time1, args.time2, args.timezone)
        sys.exit(0 if success else 1)

    if args.add:
        if not all([args.time, args.duration, args.timezone]):
            print("Error: --add requires --time, --duration, and --timezone")
            sys.exit(1)
        success = display_addition(args.time, args.duration, args.timezone)
        sys.exit(0 if success else 1)

    # No arguments provided
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
