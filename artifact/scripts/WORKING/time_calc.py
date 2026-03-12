#!/usr/bin/env python3
"""
Time Zone Calculator CLI
Simple tool for time zone conversions and time calculations.
"""

import sys
import argparse
from datetime import datetime, timedelta

try:
    import pytz
except ImportError:
    print("Error: pytz package not installed. Install with: pip install pytz")
    sys.exit(1)


def list_timezones(filter_text=None):
    """List all available timezones"""
    timezones = pytz.all_timezones
    
    if filter_text:
        timezones = [tz for tz in timezones if filter_text.lower() in tz.lower()]
    
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


def convert_timezone(time_str, from_tz, to_tz):
    """Convert time between timezones"""
    try:
        print(f"\n🔄 Converting timezone...")
        
        # Parse input time
        if time_str.lower() == 'now':
            dt = datetime.now()
        else:
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        
        # Add source timezone
        source_tz = pytz.timezone(from_tz)
        dt = source_tz.localize(dt)
        
        # Convert to target timezone
        target_tz = pytz.timezone(to_tz)
        converted = dt.astimezone(target_tz)
        
        print(f"\n✅ Conversion result:")
        print(f"{'='*70}")
        print(f"From: {dt.strftime('%Y-%m-%d %H:%M:%S')} {from_tz}")
        print(f"To:   {converted.strftime('%Y-%m-%d %H:%M:%S')} {to_tz}")
        print('='*70)
        
        return True
        
    except ValueError as e:
        print(f"❌ Error: Invalid time format. Use YYYY-MM-DD HH:MM:SS or 'now'")
        return False
    except pytz.exceptions.UnknownTimeZoneError:
        print(f"❌ Error: Invalid timezone. Use --list to see available timezones")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def calculate_difference(time1, time2, timezone):
    """Calculate time difference"""
    try:
        print(f"\n📊 Calculating time difference...")
        
        # Parse times
        dt1 = datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
        dt2 = datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")
        
        # Add timezone
        tz = pytz.timezone(timezone)
        dt1 = tz.localize(dt1)
        dt2 = tz.localize(dt2)
        
        # Calculate difference
        diff = abs(dt2 - dt1)
        
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        seconds = diff.seconds % 60
        
        total_hours = diff.total_seconds() / 3600
        
        print(f"\n✅ Time difference:")
        print(f"{'='*70}")
        print(f"From: {time1} {timezone}")
        print(f"To:   {time2} {timezone}")
        print(f"\nDifference:")
        print(f"  {days} days, {hours} hours, {minutes} minutes, {seconds} seconds")
        print(f"  Total: {total_hours:.2f} hours")
        print('='*70)
        
        return True
        
    except ValueError:
        print(f"❌ Error: Invalid time format. Use YYYY-MM-DD HH:MM:SS")
        return False
    except pytz.exceptions.UnknownTimeZoneError:
        print(f"❌ Error: Invalid timezone. Use --list to see available timezones")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def add_time(time_str, duration, timezone):
    """Add duration to time"""
    try:
        print(f"\n➕ Adding time...")
        
        # Parse base time
        if time_str.lower() == 'now':
            dt = datetime.now()
        else:
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        
        tz = pytz.timezone(timezone)
        dt = tz.localize(dt)
        
        # Parse duration (format: XdYhZm)
        days = hours = minutes = 0
        
        remaining = duration
        if 'd' in remaining:
            days = int(remaining.split('d')[0])
            remaining = remaining.split('d')[1] if len(remaining.split('d')) > 1 else ""
        if 'h' in remaining:
            hours = int(remaining.split('h')[0])
            remaining = remaining.split('h')[1] if len(remaining.split('h')) > 1 else ""
        if 'm' in remaining:
            minutes = int(remaining.split('m')[0])
        
        # Add duration
        result = dt + timedelta(days=days, hours=hours, minutes=minutes)
        
        print(f"\n✅ Result:")
        print(f"{'='*70}")
        print(f"Start:    {dt.strftime('%Y-%m-%d %H:%M:%S')} {timezone}")
        print(f"Duration: {days}d {hours}h {minutes}m")
        print(f"End:      {result.strftime('%Y-%m-%d %H:%M:%S')} {timezone}")
        print('='*70)
        
        return True
        
    except ValueError:
        print(f"❌ Error: Invalid format. Time: YYYY-MM-DD HH:MM:SS, Duration: XdYhZm (e.g., 1d2h30m)")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def interactive_mode():
    """Interactive time calculator mode"""
    print("\n" + "="*70)
    print("Time Zone Calculator - Interactive Mode")
    print("="*70)
    print("Commands:")
    print("  convert    - Convert time between timezones")
    print("  diff       - Calculate time difference")
    print("  add        - Add duration to time")
    print("  list       - List available timezones")
    print("  help       - Show this help")
    print("  quit/exit  - Exit interactive mode")
    print("="*70 + "\n")
    
    while True:
        try:
            user_input = input("time> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\nCommands:")
                print("  convert - Convert time between timezones")
                print("  diff    - Calculate time difference")
                print("  add     - Add duration to time")
                print("  list    - List available timezones")
                print("  help    - Show this help")
                print("  quit    - Exit interactive mode\n")
                continue
            
            command = user_input.lower()
            
            if command == 'convert':
                time_str = input("Time (YYYY-MM-DD HH:MM:SS or 'now'): ").strip()
                from_tz = input("From timezone: ").strip()
                to_tz = input("To timezone: ").strip()
                convert_timezone(time_str, from_tz, to_tz)
                
            elif command == 'diff':
                time1 = input("First time (YYYY-MM-DD HH:MM:SS): ").strip()
                time2 = input("Second time (YYYY-MM-DD HH:MM:SS): ").strip()
                timezone = input("Timezone: ").strip()
                calculate_difference(time1, time2, timezone)
                
            elif command == 'add':
                time_str = input("Base time (YYYY-MM-DD HH:MM:SS or 'now'): ").strip()
                duration = input("Duration (e.g., 1d2h30m): ").strip()
                timezone = input("Timezone: ").strip()
                add_time(time_str, duration, timezone)
                
            elif command == 'list':
                filter_text = input("Filter (optional): ").strip() or None
                list_timezones(filter_text)
                
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Time zone calculator and converter",
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
        list_timezones(args.filter)
        sys.exit(0)
    
    if args.convert:
        if not all([args.time, args.from_tz, args.to_tz]):
            print("Error: --convert requires --time, --from, and --to")
            sys.exit(1)
        success = convert_timezone(args.time, args.from_tz, args.to_tz)
        sys.exit(0 if success else 1)
    
    if args.diff:
        if not all([args.time1, args.time2, args.timezone]):
            print("Error: --diff requires --time1, --time2, and --timezone")
            sys.exit(1)
        success = calculate_difference(args.time1, args.time2, args.timezone)
        sys.exit(0 if success else 1)
    
    if args.add:
        if not all([args.time, args.duration, args.timezone]):
            print("Error: --add requires --time, --duration, and --timezone")
            sys.exit(1)
        success = add_time(args.time, args.duration, args.timezone)
        sys.exit(0 if success else 1)
    
    # No arguments provided
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
