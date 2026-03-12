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
from openai import AsyncOpenAI

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
# Cheat-sheet shortcuts for common tasks (same as original)
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
    "lines of code": {
        "tool": "bash",
        "code": "find . -name '*.py' -not -path '*/venv/*' | xargs wc -l | sort -n",
        "desc": "Count lines in Python files"
    },
    "running processes": {
        "tool": "bash",
        "code": "ps aux --sort -rss | head",
        "desc": "Top memory-hungry processes"
    },
    "systemd services": {
        "tool": "bash",
        "code": "systemctl list-units --type=service --state=running",
        "desc": "Show running systemd services"
    },
    "network ports": {
        "tool": "bash",
        "code": "lsof -i -P -n | grep LISTEN",
        "desc": "Show listening network ports"
    },
    "docker containers": {
        "tool": "bash",
        "code": "docker ps --format '{{.Names}}\\t{{.Status}}'",
        "desc": "List running Docker containers"
    },
    "tail logs": {
        "tool": "bash",
        "code": "tail -n 100 -f /var/log/syslog",
        "desc": "Live-tail system log"
    },
    "quick webserver": {
        "tool": "bash",
        "code": "python3 -m http.server 8000",
        "desc": "Serve current dir on port 8000"
    },
    "git status": {
        "tool": "bash",
        "code": "git status -sb",
        "desc": "Compact Git status"
    },
    "git sync": {
        "tool": "bash",
        "code": "git pull --ff-only && git push",
        "desc": "Pull then push current branch"
    },
    "current directory": {
        "tool": "bash",
        "code": "pwd",
        "desc": "Print working directory"
    },
    "search TODO": {
        "tool": "bash",
        "code": "grep -Rin 'TODO' --exclude-dir=.git .",
        "desc": "Find TODO comments recursively"
    },
    "say hello": {
        "tool": "python",
        "code": "print('Hello, world!')",
        "desc": "Simple Python greeting"
    },
    "json pretty": {
        "tool": "python",
        "code": "import json, sys; print(json.dumps(json.load(sys.stdin), indent=2))",
        "desc": "Pretty-print JSON from stdin"
    },
    "http get": {
        "tool": "python",
        "code": "import requests, pprint; pprint.pp(requests.get('https://api.github.com').json())",
        "desc": "Fetch & print GitHub API JSON"
    },
    "list open files": {
        "tool": "bash",
        "code": "lsof | head -20",
        "desc": "Show first 20 open files"
    },
    "check internet": {
        "tool": "bash",
        "code": "ping -c 4 8.8.8.8",
        "desc": "Test internet connectivity"
    },
    "python version": {
        "tool": "python",
        "code": "import sys; print(sys.version)",
        "desc": "Show Python version"
    },
    "show date": {
        "tool": "bash",
        "code": "date",
        "desc": "Show current date and time"
    },
    "find text": {
        "tool": "bash",
        "code": "grep -r 'search_term' .",
        "desc": "Find text in files recursively"
    }
}

# -----------------------------------------------------------------------------
# Utility Functions for Narrow Terminal Support (same as original)
# -----------------------------------------------------------------------------
def get_terminal_width() -> int:
    """Get the current terminal width for responsive design"""
    return console.width

def wrap_text(text: str, width: Optional[int] = None) -> str:
    """Wrap text to fit terminal width"""
    if width is None:
        width = get_terminal_width() - 4  # Account for panel borders
    return "\n".join(textwrap.wrap(text, width=width))

def create_responsive_panel(content: str, title: str = "", border_style: str = "cyan", 
                          width_fraction: float = 1.0) -> Panel:
    """Create a panel that adapts to terminal width"""
    terminal_width = get_terminal_width()
    panel_width = min(int(terminal_width * width_fraction), terminal_width - 2)
    
    # Wrap content to fit panel
    wrapped_content = wrap_text(content, panel_width - 4)
    
    return Panel(
        wrapped_content,
        title=title,
        border_style=border_style,
        width=panel_width,
        expand=False
    )

def show_splash_screen():
    """Display an animated splash screen"""
    terminal_width = get_terminal_width()
    
    # Responsive splash for narrow terminals
    if terminal_width < 50:
        splash_text = "LLAMALINE (OpenAI)"
    else:
        splash_text = """╦  ╦  ╔═╗╔╦╗╔═╗╦  ╦╔╗╔╔═╗
║  ║  ╠═╣║║║╠═╣║  ║║║║║╣ 
╩═╝╩═╝╩ ╩╩ ╩╩ ╩╩═╝╩╝╚╝╚═╝
🤖 Powered by OpenAI"""
    
    # Center the splash text
    splash = Text(splash_text, style="bold cyan")
    console.print(Align.center(splash))
    console.print()
    
    # Center the subtitle
    subtitle = Text("Natural Language → Code", style="dim")
    console.print(Align.center(subtitle))

def show_startup_menu(model: str):
    """Display startup menu with responsive design"""
    terminal_width = get_terminal_width()
    
    # Show splash screen only on wide terminals
    if terminal_width > 50:
        show_splash_screen()
        console.print()
    
    # Model info
    info_text = f"Model: [bold yellow]{model}[/bold yellow]"
    if terminal_width > 60:
        info_text += f"   Provider: [bold yellow]OpenAI[/bold yellow]"
    
    # Quick commands
    if terminal_width > 40:
        commands = "Commands: [bold]help[/bold] • [bold]cheats[/bold] • [bold]model[/bold] • [bold]quit[/bold]"
    else:
        commands = "Type [bold]help[/bold] for commands"
    
    content = f"{info_text}\n{commands}"
    
    # Calculate panel width based on content
    content_lines = content.split('\n')
    # Remove markup for width calculation
    import re
    clean_lines = [re.sub(r'\[.*?\]', '', line) for line in content_lines]
    max_content_width = max(len(line) for line in clean_lines)
    
    # Set panel width to be slightly wider than content but not exceed terminal
    panel_width = min(max_content_width + 8, terminal_width - 2)
    
    panel = Panel(
        content,
        title="🚀 Llamaline CLI (OpenAI)" if terminal_width > 30 else "Llamaline",
        border_style="cyan",
        width=panel_width,
        expand=False
    )
    
    # Center the panel
    console.print(Align.center(panel))

# -----------------------------------------------------------------------------
# Executor Tools (same as original)
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
            
            # Pretty-print dict or JSON output
            if not err:
                try:
                    val = ast.literal_eval(out)
                    if isinstance(val, dict):
                        out = json.dumps(val, indent=2, sort_keys=True)
                except Exception:
                    pass
            
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
        """Get list of available OpenAI models (excluding GPT-3.5 models)"""
        try:
            models = await self.client.models.list()
            # Filter out GPT-3.5 models and only include GPT models
            filtered_models = [
                model.id for model in models.data 
                if 'gpt' in model.id.lower() and '3.5' not in model.id.lower()
            ]
            return sorted(filtered_models, key=lambda x: (
                '4o' not in x,  # 4o models first
                '4-turbo' not in x,  # then 4-turbo
                '4' not in x,  # then regular 4
                x  # then alphabetical
            ))
        except Exception as e:
            console.print(f"[error]Error fetching models: {e}[/error]")
            return ["gpt-4.1-mini-2025-04-14", "gpt-4-turbo"]  # Removed 3.5 from fallback

    async def select_tool(self, user_prompt: str) -> Dict[str, str]:
        """Use OpenAI to select tool and generate code"""
        # Build system prompt for classification
        system_prompt = (
            "You are an assistant that takes a single natural-language prompt. "
            "Decide whether to use a shell command or a Python snippet to fulfill it. "
            "Respond with a raw JSON object with exactly two keys: "
            "\"tool\" (\"bash\" or \"python\") and \"code\" (the command or code snippet). "
            "Do NOT wrap the JSON in markdown or code fences. "
            "In the JSON, represent newlines in \"code\" using literal \"\\n\" characters, and do not include any literal line breaks. "
            "Do not include any additional text, comments, or formatting."
        )
        
        try:
            # Use OpenAI's chat completion API
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
# UI Components for Rich Interactivity (same as original)
# -----------------------------------------------------------------------------
def show_cheat_sheet():
    """Display cheat sheet in a responsive table"""
    table = Table(
        title="📋 Cheat Sheet Commands",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        width=min(80, get_terminal_width() - 2)
    )
    
    # Adjust columns based on terminal width
    if get_terminal_width() > 60:
        table.add_column("Command", style="yellow", no_wrap=True)
        table.add_column("Type", style="cyan")
        table.add_column("Code", style="green")
        table.add_column("Description", style="dim")
        
        for name, info in CHEAT_SHEETS.items():
            table.add_row(
                name,
                f"[{info['tool']}]",
                info['code'][:30] + "..." if len(info['code']) > 30 else info['code'],
                info.get('desc', '')
            )
    else:
        # Narrow terminal: simplified view
        table.add_column("Command", style="yellow")
        table.add_column("Description", style="dim")
        
        for name, info in CHEAT_SHEETS.items():
            table.add_row(name, info.get('desc', info['tool']))
    
    console.print(table)

def show_help():
    """Display help information with responsive layout"""
    help_items = [
        ("help", "Show this help message"),
        ("cheats", "List available shortcuts"),
        ("model", "Show current model"),
        ("model <name>", "Change OpenAI model"),
        ("history", "Show command history"),
        ("clear", "Clear the screen"),
        ("quit", "Exit the application"),
    ]
    
    if get_terminal_width() > 50:
        # Wide terminal: two-column layout
        table = Table(box=None, show_header=False, padding=(0, 2))
        table.add_column("Command", style="bold cyan")
        table.add_column("Description")
        
        for cmd, desc in help_items:
            table.add_row(f"[bold]{cmd}[/bold]", desc)
        
        console.print(Panel(table, title="🔧 Available Commands", border_style="green"))
    else:
        # Narrow terminal: vertical list
        content = "\n".join([f"• [bold cyan]{cmd}[/bold cyan]\n  {desc}" for cmd, desc in help_items])
        console.print(create_responsive_panel(content, title="🔧 Commands", border_style="green"))

def display_code_preview(tool: str, code: str) -> None:
    """Display code with syntax highlighting and responsive wrapping"""
    terminal_width = get_terminal_width()
    
    # Create syntax-highlighted code
    if tool == "python":
        syntax = Syntax(code, "python", theme="monokai", word_wrap=True, 
                       line_numbers=terminal_width > 60)
    else:
        syntax = Syntax(code, "bash", theme="monokai", word_wrap=True,
                       line_numbers=terminal_width > 60)
    
    # Responsive panel title
    title = f"💻 {tool.title()} Code Preview"
    if terminal_width < 40:
        title = f"{tool.title()}"
    
    panel = Panel(
        syntax,
        title=title,
        border_style="blue",
        width=min(terminal_width - 2, 100),
        expand=False
    )
    console.print(panel)

def display_result(tool: str, result: str) -> None:
    """Display command results with responsive formatting"""
    # Truncate very long results for narrow terminals
    max_lines = 20 if get_terminal_width() < 50 else 50
    lines = result.split('\n')
    
    if len(lines) > max_lines:
        result = '\n'.join(lines[:max_lines])
        result += f"\n\n[dim]... ({len(lines) - max_lines} more lines)[/dim]"
    
    # Create output panel
    if "Error" in result:
        panel_style = "red"
        title = "❌ Error Output"
    else:
        panel_style = "green"
        title = f"✅ {tool.title()} Output"
    
    if get_terminal_width() < 40:
        title = "Output"
    
    console.print(create_responsive_panel(result, title=title, border_style=panel_style))

def display_models_with_pagination(models: List[str], current_model: str, page_size: int = 10) -> bool:
    """Display models with pagination. Returns True if user wants to see more."""
    if not models:
        console.print("[warning]No models available[/warning]")
        return False
    
    # Filter out current model from the list for cleaner display
    other_models = [m for m in models if m != current_model]
    
    # Show current model first
    console.print(f"  • [bold green]{current_model}[/bold green] (current)")
    
    # Paginate through other models
    total_pages = (len(other_models) + page_size - 1) // page_size
    
    for page in range(total_pages):
        start_idx = page * page_size
        end_idx = min(start_idx + page_size, len(other_models))
        page_models = other_models[start_idx:end_idx]
        
        # Display models for this page
        for model in page_models:
            console.print(f"  • {model}")
        
        # Show pagination info
        if page < total_pages - 1:
            remaining = len(other_models) - end_idx
            console.print(f"\n[dim]Showing {end_idx}/{len(other_models)} models. {remaining} more available.[/dim]")
            
            from rich.prompt import Confirm
            if not Confirm.ask("[cyan]Show more models?[/cyan]", default=False):
                if remaining > 0:
                    console.print(f"[dim]... and {remaining} more models (type 'model' again to see all)[/dim]")
                break
            console.print()  # Add spacing between pages
    
    return False

# -----------------------------------------------------------------------------
# Main CLI with Enhanced Interactivity
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
    
    # Confirmation with Rich prompt
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
    # Parse command-line overrides
    parser = argparse.ArgumentParser(description="Natural-language to code executor (OpenAI)")
    parser.add_argument("-m", "--model", help="OpenAI model to use", default=None)
    parser.add_argument("prompt", nargs=argparse.REMAINDER, help="Natural-language prompt to execute")
    args = parser.parse_args()

    # Instantiate with optional overrides
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
        
        # Handle special commands
        if prompt.lower() in ("cheats", "help cheats", "list cheats"):
            show_cheat_sheet()
            return
        
        # Process the prompt
        asyncio.run(process_prompt(prompt, chat, tools))
        return

    # Interactive loop with command history
    command_history: List[str] = []
    
    try:
        while True:
            console.print()
            
            # Responsive prompt
            if get_terminal_width() > 50:
                prompt_text = "[prompt]Enter your task (or 'quit' to exit):[/prompt]"
            else:
                prompt_text = "[prompt]Task:[/prompt]"
            
            prompt = Prompt.ask(prompt_text, console=console)
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
                    history_panel = create_responsive_panel(
                        "\n".join([f"{i+1}. {cmd}" for i, cmd in enumerate(command_history[-10:])]),
                        title="📜 Recent Commands",
                        border_style="blue"
                    )
                    console.print(history_panel)
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
                            console.print("[info]Available models (GPT-3.5 models excluded):[/info]")
                            display_models_with_pagination(available_models, chat.model, page_size=10)
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
        # Farewell message
        console.print("\n[dim]Thanks for using Llamaline (OpenAI)! 👋[/dim]")

if __name__ == '__main__':
    main() 