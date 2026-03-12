###############################################################################
# TIME & CALCULATION TOOL MODULE FOR SWARM AGENT ORCHESTRATION
# Provides: Timezone conversion, time difference, math evaluation, current time,
# and timezone listing as agent tools.
# Interactive CLI for agent testing, with colorized output and accessibility.
# This module is intended to be used by a Swarm agent or orchestrator.
###############################################################################

import os
import sys
import json
import argparse
import pytz
import dateparser
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env for credentials and settings
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

# Swarm logo and settings
def load_swarm_logo():
    swarm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.swarm')
    if os.path.exists(swarm_path):
        with open(swarm_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

SWARM_LOGO = load_swarm_logo()

# Colorama for CLI styling
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    class Dummy:
        def __getattr__(self, k): return ''
    Fore = Style = Dummy()

###############################################################################
# TOOL FUNCTIONALITY
###############################################################################

def _parse_time(time_str: str, source_tz: Optional[str] = None) -> datetime:
    settings = {}
    if source_tz:
        settings['TIMEZONE'] = source_tz
    parsed = dateparser.parse(time_str, settings=settings)
    if not parsed:
        raise ValueError(f"Could not parse time string: {time_str}")
    return parsed

def _format_time(dt: datetime, format_str: Optional[str] = None) -> str:
    if format_str:
        return dt.strftime(format_str)
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")

def _convert_timezone(dt: datetime, target_tz: str) -> datetime:
    target_timezone = pytz.timezone(target_tz)
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    return dt.astimezone(target_timezone)

def _calculate_time_difference(
    time1: datetime,
    time2: datetime,
    unit: str = "seconds"
) -> float:
    diff = abs(time2 - time1)
    if unit == "seconds":
        return diff.total_seconds()
    elif unit == "minutes":
        return diff.total_seconds() / 60
    elif unit == "hours":
        return diff.total_seconds() / 3600
    elif unit == "days":
        return diff.days + (diff.seconds / 86400)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")

def _evaluate_expression(expression: str) -> float:
    safe_dict = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'pow': pow,
        'sum': sum,
        'len': len,
        'sin': np.sin,
        'cos': np.cos,
        'tan': np.tan,
        'exp': np.exp,
        'log': np.log,
        'sqrt': np.sqrt,
        'pi': np.pi,
        'e': np.e
    }
    try:
        expression = expression.replace('^', '**')
        return float(eval(expression, {"__builtins__": {}}, safe_dict))
    except Exception as e:
        raise ValueError(f"Invalid expression: {str(e)}")

class Tools:
    class Valves(BaseModel):
        DEFAULT_TIMEZONE: str = Field(default="UTC")
        TIME_FORMAT: str = Field(default="%Y-%m-%d %H:%M:%S %Z")
        ROUND_DIGITS: int = Field(default=6)

    def __init__(self):
        self.valves = self.Valves()

    def convert_time(
        self,
        time: str,
        source_timezone: Optional[str] = None,
        target_timezone: str = "UTC",
        format: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            dt = _parse_time(time, source_timezone)
            converted = _convert_timezone(dt, target_timezone)
            format_str = format or self.valves.TIME_FORMAT
            return {
                "status": "success",
                "data": {
                    "original": _format_time(dt, format_str),
                    "converted": _format_time(converted, format_str),
                    "source_timezone": str(dt.tzinfo),
                    "target_timezone": target_timezone
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def calculate_time_difference(
        self,
        time1: str,
        time2: str,
        unit: str = "seconds",
        timezone: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            dt1 = _parse_time(time1, timezone)
            dt2 = _parse_time(time2, timezone)
            difference = _calculate_time_difference(dt1, dt2, unit)
            return {
                "status": "success",
                "data": {
                    "time1": _format_time(dt1),
                    "time2": _format_time(dt2),
                    "difference": round(difference, self.valves.ROUND_DIGITS),
                    "unit": unit
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def evaluate_math(
        self,
        expression: str,
        variables: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        try:
            if variables:
                for var, value in variables.items():
                    expression = expression.replace(var, str(value))
            result = _evaluate_expression(expression)
            return {
                "status": "success",
                "data": {
                    "expression": expression,
                    "result": round(result, self.valves.ROUND_DIGITS),
                    "variables": variables or {}
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def get_current_time(
        self,
        timezone: Optional[str] = None,
        format: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            now = datetime.now(pytz.UTC)
            if timezone:
                now = _convert_timezone(now, timezone)
            format_str = format or self.valves.TIME_FORMAT
            return {
                "status": "success",
                "data": {
                    "current_time": _format_time(now, format_str),
                    "timezone": str(now.tzinfo)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def list_timezones(self, filter: Optional[str] = None) -> Dict[str, Any]:
        try:
            zones = pytz.all_timezones
            if filter:
                zones = [tz for tz in zones if filter.lower() in tz.lower()]
            return {
                "status": "success",
                "data": {
                    "timezones": zones
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

###############################################################################
# INTERACTIVE CLI FOR AGENT/TOOL TESTING
###############################################################################

def print_banner():
    print(Fore.MAGENTA + "=" * 70)
    if SWARM_LOGO:
        print(Fore.CYAN + SWARM_LOGO)
    print(Fore.YELLOW + "TIME & CALCULATION TOOL MODULE FOR SWARM AGENT")
    print(Fore.GREEN + "This module provides the following tools for agent orchestration:\n")
    print(Fore.CYAN + "  1. convert_time: Convert a time string between timezones.")
    print(Fore.CYAN + "  2. calculate_time_difference: Find the difference between two times.")
    print(Fore.CYAN + "  3. evaluate_math: Evaluate a mathematical expression.")
    print(Fore.CYAN + "  4. get_current_time: Get the current time in a timezone.")
    print(Fore.CYAN + "  5. list_timezones: List available timezones (with optional filter).")
    print(Fore.YELLOW + "\nUse these tools when you need to:")
    print(Fore.YELLOW + "  - Convert or compare times across timezones")
    print(Fore.YELLOW + "  - Perform quick math calculations")
    print(Fore.YELLOW + "  - Retrieve or display current time for a region")
    print(Fore.YELLOW + "  - Show available timezones for user selection")
    print(Fore.MAGENTA + "=" * 70)
    print(Fore.WHITE + Style.BRIGHT + "Type the number of the tool to use, or 'test' to run all tool tests, or 'exit' to quit.\n")

def test_all_tools():
    tools = Tools()
    print(Fore.BLUE + "\n[TEST] convert_time")
    print(json.dumps(tools.convert_time("2024-06-01 12:00", "UTC", "America/Los_Angeles"), indent=2))
    print(Fore.BLUE + "\n[TEST] calculate_time_difference")
    print(json.dumps(tools.calculate_time_difference("2024-06-01 12:00", "2024-06-01 15:00", "hours", "UTC"), indent=2))
    print(Fore.BLUE + "\n[TEST] evaluate_math")
    print(json.dumps(tools.evaluate_math("2 * (3 + 4) ^ 2"), indent=2))
    print(Fore.BLUE + "\n[TEST] get_current_time")
    print(json.dumps(tools.get_current_time("Asia/Tokyo"), indent=2))
    print(Fore.BLUE + "\n[TEST] list_timezones (filter='America')")
    print(json.dumps(tools.list_timezones("America"), indent=2))

def interactive_cli():
    tools = Tools()
    print_banner()
    while True:
        try:
            print(Fore.YELLOW + "\nSelect a tool:")
            print(Fore.CYAN + "  1. convert_time")
            print(Fore.CYAN + "  2. calculate_time_difference")
            print(Fore.CYAN + "  3. evaluate_math")
            print(Fore.CYAN + "  4. get_current_time")
            print(Fore.CYAN + "  5. list_timezones")
            print(Fore.CYAN + "  test. Run all tool tests")
            print(Fore.CYAN + "  exit. Quit\n")
            choice = input(Fore.GREEN + "Enter your choice: ").strip().lower()
            if choice in ("exit", "quit"):
                print(Fore.MAGENTA + "\nGoodbye! 👋")
                break
            elif choice == "test":
                test_all_tools()
                continue
            elif choice == "1" or choice == "convert_time":
                time = input("Enter time string: ")
                source_tz = input("Source timezone (blank for UTC): ") or None
                target_tz = input("Target timezone (default UTC): ") or "UTC"
                fmt = input("Output format (blank for default): ") or None
                result = tools.convert_time(time, source_tz, target_tz, fmt)
                print(Fore.YELLOW + json.dumps(result, indent=2))
            elif choice == "2" or choice == "calculate_time_difference":
                t1 = input("First time string: ")
                t2 = input("Second time string: ")
                unit = input("Unit (seconds/minutes/hours/days, default seconds): ") or "seconds"
                tz = input("Timezone (blank for UTC): ") or None
                result = tools.calculate_time_difference(t1, t2, unit, tz)
                print(Fore.YELLOW + json.dumps(result, indent=2))
            elif choice == "3" or choice == "evaluate_math":
                expr = input("Enter mathematical expression: ")
                vars_input = input("Variables (JSON, blank for none): ")
                variables = None
                if vars_input.strip():
                    try:
                        variables = json.loads(vars_input)
                    except Exception as e:
                        print(Fore.RED + f"Invalid JSON for variables: {e}")
                        continue
                result = tools.evaluate_math(expr, variables)
                print(Fore.YELLOW + json.dumps(result, indent=2))
            elif choice == "4" or choice == "get_current_time":
                tz = input("Timezone (blank for UTC): ") or None
                fmt = input("Output format (blank for default): ") or None
                result = tools.get_current_time(tz, fmt)
                print(Fore.YELLOW + json.dumps(result, indent=2))
            elif choice == "5" or choice == "list_timezones":
                filt = input("Filter string (blank for all): ") or None
                result = tools.list_timezones(filt)
                print(Fore.YELLOW + json.dumps(result, indent=2))
            else:
                print(Fore.RED + "Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print(Fore.MAGENTA + "\n\nSession ended by user. Goodbye! 👋")
            break
        except Exception as e:
            print(Fore.RED + f"Error: {e}")

###############################################################################
# XAI API ENDPOINT AND AGENT TOOL WRAPPER
###############################################################################

XAI_API_ENDPOINT = "https://api.x.ai/v1/chat/completions"

def setup_client(api_key: Optional[str] = None) -> Dict[str, str]:
    api_key = api_key or os.environ.get("XAI_API_KEY")
    if not api_key:
        raise ValueError("xAI API key is required. Set XAI_API_KEY environment variable or provide --api-key argument.")
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

def get_tool_schema() -> dict:
    schema = {
        "type": "function",
        "function": {
            "name": "time_calculator",
            "description": (
                "Time and calculation tools: convert timezones, calculate time differences, "
                "evaluate math, get current time, and list timezones."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "tool": {
                        "type": "string",
                        "description": "Which tool to use (convert_time, calculate_time_difference, evaluate_math, get_current_time, list_timezones)"
                    },
                    "args": {
                        "type": "object",
                        "description": "Arguments for the selected tool"
                    }
                },
                "required": ["tool", "args"]
            }
        }
    }
    if "function" in schema:
        schema["function"]["module"] = "swarm_time"
    return schema

def get_tool_schemas():
    schemas = [get_tool_schema()]
    for schema in schemas:
        if "function" in schema:
            schema["function"]["module"] = "swarm_time"
    return schemas

# Define TOOL_SCHEMAS for discovery by the swarm master
TOOL_SCHEMAS = get_tool_schemas()

def handle_tool_calls(tool_calls: List[Dict[str, Any]], config: dict = None) -> List[Dict[str, Any]]:
    tool_results = []
    tools = Tools()
    for tool_call in tool_calls:
        tool_call_id = tool_call.get("id")
        function = tool_call.get("function", {})
        name = function.get("name")
        arguments = function.get("arguments", "{}")
        try:
            args = json.loads(arguments)
        except Exception:
            args = {}
        if name == "time_calculator":
            tool = args.get("tool")
            tool_args = args.get("args", {})
            try:
                if tool == "convert_time":
                    result = tools.convert_time(**tool_args)
                elif tool == "calculate_time_difference":
                    result = tools.calculate_time_difference(**tool_args)
                elif tool == "evaluate_math":
                    result = tools.evaluate_math(**tool_args)
                elif tool == "get_current_time":
                    result = tools.get_current_time(**tool_args)
                elif tool == "list_timezones":
                    result = tools.list_timezones(**tool_args)
                else:
                    result = {"status": "error", "message": f"Unknown tool: {tool}"}
            except Exception as e:
                result = {"status": "error", "message": str(e)}
            tool_results.append({
                "tool_call_id": tool_call_id,
                "role": "tool",
                "content": json.dumps(result)
            })
        else:
            tool_results.append({
                "tool_call_id": tool_call_id,
                "role": "tool",
                "content": f"Error: Tool '{name}' is not supported."
            })
    return tool_results

def main():
    parser = argparse.ArgumentParser(description="Time & Calculation Tool CLI (Swarm Agent Tool)")
    parser.add_argument("--interactive", action="store_true", help="Run interactive CLI")
    parser.add_argument("--test", action="store_true", help="Test all tools")
    parser.add_argument("--api-key", type=str, default=None, help="xAI API key (optional)")
    args = parser.parse_args()
    if args.interactive:
        interactive_cli()
        return
    if args.test:
        test_all_tools()
        return
    print(Fore.YELLOW + "No mode selected. Use --interactive for CLI or --test for tool tests.")

if __name__ == "__main__":
    main()