"""
Time and Calculation tools combining timezone conversion and mathematical operations
Enhanced with accessibility features and improved formatting
"""

import pytz
import dateparser
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, List
from pydantic import BaseModel, Field

def _parse_time(time_str: str, source_tz: Optional[str] = None) -> datetime:
    """Parse time string with timezone support"""
    settings = {}
    if source_tz:
        settings['TIMEZONE'] = source_tz
    
    parsed = dateparser.parse(time_str, settings=settings)
    if not parsed:
        raise ValueError(f"Could not parse time string: {time_str}")
    return parsed

def _format_time(dt: datetime, format_str: Optional[str] = None) -> str:
    """Format datetime with optional format string"""
    if format_str:
        return dt.strftime(format_str)
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")

def _convert_timezone(dt: datetime, target_tz: str) -> datetime:
    """Convert datetime to target timezone"""
    target_timezone = pytz.timezone(target_tz)
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    return dt.astimezone(target_timezone)

def _calculate_time_difference(
    time1: datetime,
    time2: datetime,
    unit: str = "seconds"
) -> float:
    """Calculate time difference in specified unit"""
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
    """Safely evaluate mathematical expression"""
    # Define allowed mathematical functions
    safe_dict = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'pow': pow,
        'sum': sum,
        'len': len,
        # NumPy functions
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
        # Replace '^' with '**' for exponentiation
        expression = expression.replace('^', '**')
        # Evaluate the expression using the safe dictionary
        return float(eval(expression, {"__builtins__": {}}, safe_dict))
    except Exception as e:
        raise ValueError(f"Invalid expression: {str(e)}")

class Tools:
    """Time and calculation tools with enhanced accessibility"""
    
    class Valves(BaseModel):
        DEFAULT_TIMEZONE: str = Field(
            default="UTC",
            description="Default timezone for time operations"
        )
        TIME_FORMAT: str = Field(
            default="%Y-%m-%d %H:%M:%S %Z",
            description="Default time format string"
        )
        ROUND_DIGITS: int = Field(
            default=6,
            description="Number of decimal places for rounding calculations"
        )

    def __init__(self):
        self.valves = self.Valves()

    def convert_time(
        self,
        time: str,
        source_timezone: Optional[str] = None,
        target_timezone: str = "UTC",
        format: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Convert time between timezones with enhanced formatting options.
        
        :param time: Time string to convert
        :param source_timezone: Source timezone (optional)
        :param target_timezone: Target timezone
        :param format: Output format string (optional)
        :return: Dictionary with conversion results
        """
        try:
            # Parse input time
            dt = _parse_time(time, source_timezone)
            
            # Convert to target timezone
            converted = _convert_timezone(dt, target_timezone)
            
            # Format output
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
    ) -> Dict[str, Union[str, float]]:
        """
        Calculate time difference between two timestamps.
        
        :param time1: First time string
        :param time2: Second time string
        :param unit: Unit for the result (seconds, minutes, hours, days)
        :param timezone: Timezone for parsing times (optional)
        :return: Dictionary with calculation results
        """
        try:
            # Parse input times
            dt1 = _parse_time(time1, timezone)
            dt2 = _parse_time(time2, timezone)
            
            # Calculate difference
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
    ) -> Dict[str, Union[str, float]]:
        """
        Evaluate mathematical expression with support for variables and functions.
        
        :param expression: Mathematical expression to evaluate
        :param variables: Dictionary of variable values (optional)
        :return: Dictionary with evaluation results
        """
        try:
            # Replace variables if provided
            if variables:
                for var, value in variables.items():
                    expression = expression.replace(var, str(value))
            
            # Evaluate expression
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
    ) -> Dict[str, str]:
        """
        Get current time in specified timezone and format.
        
        :param timezone: Target timezone (optional)
        :param format: Output format string (optional)
        :return: Dictionary with current time
        """
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

    def list_timezones(self, filter: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List available timezones with optional filtering.
        
        :param filter: Filter string for timezone names (optional)
        :return: Dictionary with matching timezone names
        """
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