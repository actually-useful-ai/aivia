import os
import sys
import json
import asyncio
import tempfile
import subprocess
from typing import Dict, Any, Optional

class Tools:
    """Tools for running code in a restricted environment"""
    
    def __init__(self):
        self.python_path = sys.executable
        self.temp_dir = tempfile.gettempdir()
        
    async def run_python_code(self, code: str) -> str:
        """Run Python code in a restricted environment"""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            # Run with restricted permissions
            process = await asyncio.create_subprocess_exec(
                self.python_path,
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.temp_dir,
                env={
                    'PATH': os.environ.get('PATH', ''),
                    'PYTHONPATH': '',  # Restrict imports
                    'PYTHONHOME': '',  # Restrict Python environment
                }
            )
            
            stdout, stderr = await process.communicate()
            os.unlink(temp_path)  # Clean up temp file
            
            output = stdout.decode() if stdout else ''
            error = stderr.decode() if stderr else ''
            
            if error:
                return f"Error:\n{error}"
            return output if output else "No output"
            
        except Exception as e:
            return f"Error running Python code: {str(e)}"
    
    async def run_bash_command(self, command: str) -> str:
        """Run a bash command with restricted permissions"""
        try:
            # Basic command validation
            if any(unsafe in command.lower() for unsafe in ['sudo', 'rm -rf', '>', '>>', '|', '&', ';']):
                return "Error: Command contains unsafe operations"
            
            # Run with restricted shell
            process = await asyncio.create_subprocess_exec(
                'sh',
                '-c',
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.temp_dir,
                env={
                    'PATH': '/usr/bin:/bin',  # Restrict available commands
                    'HOME': self.temp_dir,
                }
            )
            
            stdout, stderr = await process.communicate()
            
            output = stdout.decode() if stdout else ''
            error = stderr.decode() if stderr else ''
            
            if error:
                return f"Error:\n{error}"
            return output if output else "No output"
            
        except Exception as e:
            return f"Error running bash command: {str(e)}" 