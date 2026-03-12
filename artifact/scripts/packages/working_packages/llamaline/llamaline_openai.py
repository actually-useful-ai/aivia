#!/usr/bin/env python3
"""
llamaline_openai.py

File Purpose: OpenAI-powered version of llamaline CLI - natural-language to shell/Python assistant
Primary Functions/Classes: 
  - Tools: Executor class for Python and bash commands (unchanged)
  - OpenAIChat: Interface for interacting with OpenAI models via API
  - main(): CLI entry point with rich interactive loop and narrow terminal support
Inputs and Outputs (I/O):
  - Input: Natural language prompts from user (supports narrow terminals)
  - Output: Executed code results with responsive Rich console output

A CLI tool that uses OpenAI's API (GPT-4, GPT-3.5-turbo, etc.) to interpret natural-language prompts,
select between Python and shell execution tools, generate the needed code/command,
and execute it securely in a restricted environment. Optimized for narrow terminals
with comprehensive Rich styling for enhanced interactivity.
"""
import os
import sys
import json
import ast
import asyncio
import tempfile
import textwrap
from typing import Generator, Optional, Dict, List
from datetime import datetime

import argparse

# Rich imports for comprehensive styled CLI output
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.layout import Layout
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule
from rich import box
from rich.live import Live
from rich.spinner import Spinner
from rich.style import Style
from rich.theme import Theme

# OpenAI imports
try:
    from openai import AsyncOpenAI
except ImportError:
    print("Error: openai package not found. Install with: pip install openai")
    sys.exit(1)

# Custom theme for consistent styling
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "prompt": "bold magenta",
    "code": "bold blue",
    "dim": "dim white",
})

# Instantiate a Rich console for styled output with custom theme
console = Console(theme=custom_theme)

# -----------------------------------------------------------------------------
# Configuration (override via environment variables)
DEFAULT_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4.1-mini-2025-04-14')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    console.print("[error]Error: OPENAI_API_KEY environment variable is required[/error]")
    console.print("Please set your OpenAI API key:")
    console.print("export OPENAI_API_KEY='your-api-key-here'")
    sys.exit(1)

# -----------------------------------------------------------------------------
# Cheat-sheet shortcuts for common tasks 
# -----------------------------------------------------------------------------
CHEAT_SHEETS: Dict[str, Dict[str, str]] = {
    "disk usage": {
        "tool": "bash",
        "code": "df -h",
        "desc": "Show disk space usage"
    },
    "find large files": {
        "tool": "bash",
        "code": "du -ah . | sort -rh | head -n 20",
        "desc": "Top 20 largest files/dirs"
    },
    "memory usage": {
        "tool": "bash",
        "code": "vm_stat",
        "desc": "Show memory statistics"
    },
    "running processes": {
        "tool": "bash",
        "code": "ps aux --sort -rss | head",
        "desc": "Top memory-hungry processes"
    },
    "network ports": {
        "tool": "bash",
        "code": "lsof -i -P -n | grep LISTEN",
        "desc": "Show listening network ports"
    },
    "git status": {
        "tool": "bash",
        "code": "git status -sb",
        "desc": "Compact Git status"
    },
    "say hello": {
        "tool": "python",
        "code": "print('Hello, world!')",
        "desc": "Simple Python greeting"
    },
    "show date": {
        "tool": "bash",
        "code": "date",
        "desc": "Show current date and time"
    }
}

# -----------------------------------------------------------------------------
# Utility Functions for Narrow Terminal Support
# -----------------------------------------------------------------------------
def get_terminal_width() -> int:
    """Get the current terminal width for responsive design"""
    return console.width

def show_startup_menu(model: str):
    """Display startup menu with responsive design"""
    terminal_width = get_terminal_width()
    
    if terminal_width > 50:
        splash_text = """╦  ╦  ╔═╗╔╦╗╔═╗╦  ╦╔╗╔╔═╗
║  ║  ╠═╣║║║╠═╣║  ║║║║║╣ 
╩═╝╩═╝╩ ╩╩ ╩╩ ╩╩═╝╩╝╚╝╚═╝
🤖 Powered by OpenAI"""
        splash = Text(splash_text, style="bold cyan")
        console.print(Align.center(splash))
        console.print()
    
    # Model info
    info_text = f"Model: [bold yellow]{model}[/bold yellow]"
    if terminal_width > 60:
        info_text += f"   Provider: [bold yellow]OpenAI[/bold yellow]"
    
    content = f"{info_text}\nCommands: [bold]help[/bold] • [bold]cheats[/bold] • [bold]model[/bold] • [bold]quit[/bold]"
    
    panel = Panel(
        content,
        title="🚀 Llamaline CLI (OpenAI)" if terminal_width > 30 else "Llamaline",
        border_style="cyan",
        expand=False
    )
    
    console.print(Align.center(panel))

# -----------------------------------------------------------------------------
# Executor Tools
# -----------------------------------------------------------------------------
class Tools:
    def __init__(self):
        self.python_path = sys.executable
        self.temp_dir = tempfile.gettempdir()

    async def run_python_code(self, code: str) -> str:
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name

            proc = await asyncio.create_subprocess_exec(
                self.python_path,
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd(),
                env=os.environ.copy()
            )
            stdout, stderr = await proc.communicate()
            os.unlink(temp_path)

            out = stdout.decode().strip()
            err = stderr.decode().strip()
            
            if err:
                return f"Error:\n{err}"
            return out or "No output"

        except Exception as e:
            return f"Error running Python code: {e}"

    async def run_bash_command(self, command: str) -> str:
        try:
            unsafe = ['sudo', 'rm -rf', '>', '>>', '|', '&', ';']
            if any(tok in command for tok in unsafe):
                return "Error: Command contains unsafe operations"

            proc = await asyncio.create_subprocess_exec(
                'sh', '-c', command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd(),
                env=os.environ.copy()
            )
            stdout, stderr = await proc.communicate()

            out = stdout.decode().strip()
            err = stderr.decode().strip()
            if err:
                return f"Error:\n{err}"
            return out or "No output"

        except Exception as e:
            return f"Error running bash command: {e}"

# -----------------------------------------------------------------------------
# OpenAIChat for tool selection and code generation
# -----------------------------------------------------------------------------
class OpenAIChat:
    def __init__(self, model: Optional[str] = None):
        self.model = model or DEFAULT_MODEL
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        try:
            models = await self.client.models.list()
            return [model.id for model in models.data if 'gpt' in model.id.lower()]
        except Exception as e:
            console.print(f"[error]Error fetching models: {e}[/error]")
            return ["gpt-4.1-mini-2025-04-14", "gpt-4-turbo", "gpt-3.5-turbo"]

    async def select_tool(self, user_prompt: str) -> Dict[str, str]:
        """Use OpenAI to select tool and generate code"""
        system_prompt = (
            "You are an assistant that takes a single natural-language prompt. "
            "Decide whether to use a shell command or a Python snippet to fulfill it. "
            "Respond with a raw JSON object with exactly two keys: "
            "\"tool\" (\"bash\" or \"python\") and \"code\" (the command or code snippet). "
            "Do NOT wrap the JSON in markdown or code fences. "
            "Do not include any additional text, comments, or formatting."
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown fences if present
            import re
            m = re.search(r"```json\s*(?P<json>{.*?})\s*```", content, flags=re.S)
            json_str = m.group("json") if m else content.strip()
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON from model: {content}")
                
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

# -----------------------------------------------------------------------------
# UI Components for Rich Interactivity
# -----------------------------------------------------------------------------
def show_cheat_sheet():
    """Display cheat sheet in a responsive table"""
    table = Table(
        title="📋 Cheat Sheet Commands",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    
    table.add_column("Command", style="yellow")
    table.add_column("Description", style="dim")
    
    for name, info in CHEAT_SHEETS.items():
        table.add_row(name, info.get('desc', info['tool']))
    
    console.print(table)

def show_help():
    """Display help information"""
    help_items = [
        ("help", "Show this help message"),
        ("cheats", "List available shortcuts"),
        ("model", "Show current model"),
        ("model <name>", "Change OpenAI model"),
        ("history", "Show command history"),
        ("clear", "Clear the screen"),
        ("quit", "Exit the application"),
    ]
    
    table = Table(box=None, show_header=False)
    table.add_column("Command", style="bold cyan")
    table.add_column("Description")
    
    for cmd, desc in help_items:
        table.add_row(f"[bold]{cmd}[/bold]", desc)
    
    console.print(Panel(table, title="🔧 Available Commands", border_style="green"))

def display_code_preview(tool: str, code: str) -> None:
    """Display code with syntax highlighting"""
    if tool == "python":
        syntax = Syntax(code, "python", theme="monokai", word_wrap=True)
    else:
        syntax = Syntax(code, "bash", theme="monokai", word_wrap=True)
    
    title = f"💻 {tool.title()} Code Preview"
    panel = Panel(syntax, title=title, border_style="blue")
    console.print(panel)

def display_result(tool: str, result: str) -> None:
    """Display command results"""
    if "Error" in result:
        panel_style = "red"
        title = "❌ Error Output"
    else:
        panel_style = "green"
        title = f"✅ {tool.title()} Output"
    
    console.print(Panel(result, title=title, border_style=panel_style))

# -----------------------------------------------------------------------------
# Main CLI Processing
# -----------------------------------------------------------------------------
async def process_prompt(prompt: str, chat: OpenAIChat, tools: Tools) -> None:
    """Process a single prompt with rich feedback"""
    # Check for cheat sheet command
    key = prompt.lower()
    if key in CHEAT_SHEETS:
        choice = CHEAT_SHEETS[key]
        console.print(f"\n[dim]Using cheat sheet: {key}[/dim]")
    else:
        # Generate code with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Analyzing prompt with OpenAI...", total=None)
            
            try:
                choice = await chat.select_tool(prompt)
                progress.update(task, completed=True)
            except Exception as e:
                progress.update(task, completed=True)
                console.print(Panel(
                    f"Failed to generate code: {str(e)}",
                    title="❌ Error",
                    border_style="red"
                ))
                return

    tool = choice.get("tool")
    code = choice.get("code", "")
    
    # Display code preview
    console.print()
    display_code_preview(tool, code)
    
    # Confirmation
    console.print()
    if not Confirm.ask("[prompt]Execute this code?[/prompt]", default=True):
        console.print("[warning]⚠️  Execution cancelled[/warning]")
        return
    
    # Execute with progress indicator
    console.print()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Running {tool} code...", total=None)
        
        if tool == "bash":
            result = await tools.run_bash_command(code)
        elif tool == "python":
            result = await tools.run_python_code(code)
        else:
            result = f"Unknown tool: {tool}"
        
        progress.update(task, completed=True)
    
    # Display results
    console.print()
    display_result(tool, result)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Natural-language to code executor (OpenAI)")
    parser.add_argument("-m", "--model", help="OpenAI model to use", default=None)
    parser.add_argument("prompt", nargs=argparse.REMAINDER, help="Natural-language prompt to execute")
    args = parser.parse_args()

    # Initialize
    chat = OpenAIChat(model=args.model)
    tools = Tools()

    # Show startup menu
    show_startup_menu(chat.model)

    # If prompt provided as CLI args, run once and exit
    if args.prompt:
        prompt = " ".join(args.prompt).strip()
        if not prompt:
            console.print("[error]No prompt provided.[/error]")
            return
        
        if prompt.lower() in ("cheats", "help cheats", "list cheats"):
            show_cheat_sheet()
            return
        
        asyncio.run(process_prompt(prompt, chat, tools))
        return

    # Interactive loop
    command_history: List[str] = []
    
    try:
        while True:
            console.print()
            prompt = Prompt.ask("[prompt]Enter your task (or 'quit' to exit):[/prompt]", console=console)
            prompt = prompt.strip()
            
            if prompt.lower() in ('quit', 'exit', 'q'):
                break

            # Handle built-in commands
            if prompt.lower() in ("help", "?", "h"):
                show_help()
                continue

            if prompt.lower() == "clear":
                console.clear()
                show_startup_menu(chat.model)
                continue

            if prompt.lower() == "history":
                if command_history:
                    history_text = "\n".join([f"{i+1}. {cmd}" for i, cmd in enumerate(command_history[-10:])])
                    console.print(Panel(history_text, title="📜 Recent Commands", border_style="blue"))
                else:
                    console.print("[dim]No command history yet[/dim]")
                continue

            if prompt.lower().startswith("model"):
                parts = prompt.split(maxsplit=1)
                if len(parts) == 1:
                    console.print(f"[info]Current model:[/info] [bold]{chat.model}[/bold]")
                    try:
                        available_models = asyncio.run(chat.get_available_models())
                        if available_models:
                            console.print("[info]Available models:[/info]")
                            for model in available_models[:10]:  # Show first 10
                                prefix = "• " if model != chat.model else "• [bold green]"
                                suffix = "[/bold green] (current)" if model == chat.model else ""
                                console.print(f"  {prefix}{model}{suffix}")
                            if len(available_models) > 10:
                                console.print(f"  [dim]... and {len(available_models) - 10} more[/dim]")
                            console.print("\n[dim]Use 'model <name>' to switch[/dim]")
                    except Exception:
                        console.print("[warning]Could not fetch available models[/warning]")
                else:
                    new_model = parts[1].strip()
                    chat.model = new_model
                    console.print(f"[success]✓ Model changed to:[/success] [bold]{chat.model}[/bold]")
                continue

            if prompt.lower() in ("cheats", "help cheats", "list cheats", "shortcuts"):
                show_cheat_sheet()
                continue

            # Add to history and process
            command_history.append(prompt)
            asyncio.run(process_prompt(prompt, chat, tools))

    except KeyboardInterrupt:
        console.print("\n[warning]⚡ Interrupted by user[/warning]")
    except Exception as e:
        console.print(f"\n[error]Unexpected error: {e}[/error]")
    finally:
        console.print("\n[dim]Thanks for using Llamaline (OpenAI)! 👋[/dim]")

if __name__ == '__main__':
    main() 