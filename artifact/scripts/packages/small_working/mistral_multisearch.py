###############################################################################
# UNIFIED SEARCH TOOL MODULE FOR SWARM AGENT ORCHESTRATION (MISTRAL VERSION)
#
# Provides agent tools for:
#   - Web Search (via Mistral LLM, see mistral_chat.py)
#   - Multi-Search with Summary (like @perplexity_multi.py)
#
# Exposes all tools via get_tool_schemas() and handle_tool_calls() for swarm.py.
# CLI supports --tool, --test, --chat, and tool-specific arguments.
# All output is accessible, colorized, and screen-reader friendly.
###############################################################################

# Module metadata for CLI and registry
MODULE_DISPLAY_NAME = "ChatGPT Multi-Search"
MODULE_DESCRIPTION = "Web search tools powered by OpenAI ChatGPT API"
DESCRIPTION = MODULE_DESCRIPTION

import os
from pathlib import Path
from dotenv import load_dotenv

# Environment variable loading from multiple locations
def load_env_from_multiple_locations():
    """
    Load environment variables from .env files in multiple locations:
    1. Module directory
    2. Parent directory
    3. Current working directory
    4. Home directory
    """
    module_dir = Path(__file__).parent
    env_paths = [
        module_dir / ".env",                  # module directory
        module_dir.parent / ".env",           # parent directory
        Path(os.getcwd()) / ".env",           # current working directory
        Path(os.path.expanduser("~")) / ".env"  # home directory
    ]
    
    # Load from each path if it exists
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=str(env_path))
            if os.environ.get("MISTRAL_API_KEY"):
                break

# Load environment variables on module import
load_env_from_multiple_locations()

from os.path import dirname, abspath, join
import sys
import json
import argparse
import requests
import logging
from typing import Dict, List, Any, Optional


def get(attr, default=None):
    """
    Utility function to get attributes from this module.
    This function is used by the registry system when organizing tools.
    
    Args:
        attr: Attribute name to get
        default: Default value if attribute doesn't exist
        
    Returns:
        Attribute value or default
    """
    module = sys.modules[__name__]
    return getattr(module, attr, default)
# --- Minimal CLI/Config/Logger Utilities (self-contained) ---

def load_dotenv_compat(dotenv_path: Optional[str] = None) -> dict:
    env_vars = {}
    path = dotenv_path or ".env"
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                key = k.strip()
                value = v.strip()
                env_vars[key] = value
                if key not in os.environ:
                    os.environ[key] = value
    return env_vars

def load_config(env_path: Optional[str] = None, swarm_path: Optional[str] = None, cli_args: Optional[dict] = None) -> dict:
    config = {}
    # Check for Mistral API key in environment
    if os.environ.get("MISTRAL_API_KEY"):
        config["MISTRAL_API_KEY"] = os.environ.get("MISTRAL_API_KEY")
    
    if swarm_path and os.path.exists(swarm_path):
        try:
            with open(swarm_path, "r") as f:
                data = json.load(f)
                config.update(data)
        except Exception:
            pass
    if cli_args:
        for k, v in cli_args.items():
            if v is not None:
                config[k] = v
    return config

def add_standard_cli_args(parser: argparse.ArgumentParser):
    parser.add_argument("--env", type=str, help="Path to .env file")
    parser.add_argument("--config", type=str, help="Path to swarm config file")

def load_swarm_settings() -> dict:
    return {"SWARM_LOGO": "[SWARM]"}

def format_error(msg: str) -> str:
    return f"[ERROR] {msg}"

def standardize_tool_response(tool_call_id: str, result: dict, tool_name: str, status: str = "success") -> dict:
    return {
        "id": tool_call_id,
        "tool_name": tool_name,
        "status": status,
        "result": result
    }

# --- Colorama fallback for accessibility/color ---
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    class Dummy:
        def __getattr__(self, k): return ''
    Fore = Style = Dummy()

# --- Swarm Logo ---
SWARM_SETTINGS = load_swarm_settings()
SWARM_LOGO = SWARM_SETTINGS.get("SWARM_LOGO", "[SWARM]")

logger = logging.getLogger("search_tool")
logging.basicConfig(level=logging.INFO)

DEFAULT_USER_AGENT = "SwarmSearchTool/1.0"

# =============================================================================
#  MISTRAL SEARCH TOOL (Web Search via Mistral LLM)
# =============================================================================

def get_mistral_api_key(config: Optional[dict] = None) -> str:
    """
    Get Mistral API key from config, environment variables, or a default value.
    Order of precedence:
    1. Explicit config
    2. Environment variable
    3. Return empty string (will cause proper error handling)
    """
    # Prefer explicit config
    if config and "MISTRAL_API_KEY" in config:
        key = config["MISTRAL_API_KEY"]
        # Strip quotes if present
        if isinstance(key, str) and key.startswith('"') and key.endswith('"'):
            key = key[1:-1]
        return key
    
    # Check environment variable
    env_key = os.environ.get("MISTRAL_API_KEY")
    if env_key:
        # Strip quotes if present
        if isinstance(env_key, str) and env_key.startswith('"') and env_key.endswith('"'):
            env_key = env_key[1:-1]
        return env_key
        
    # Return empty string to trigger proper error handling
    return ""

def mistral_search_tool(
    query: str,
    context: Optional[str] = None,
    model: str = "mistral-small-latest",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use Mistral LLM to answer a web search question, optionally with context.
    Attempts to use API key from argument or environment.
    Returns a dict with 'success', 'query', and either 'answer' or 'error'.
    """
    key = api_key or os.environ.get("MISTRAL_API_KEY") or get_mistral_api_key()
    if not key:
        return {
            "success": False,
            "error": "MISTRAL_API_KEY not set in environment.",
            "query": query
        }
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    system_prompt = (
        "You are a helpful web search assistant. "
        "Answer the user's question using the provided context if available. "
        "If you do not know the answer, say so."
    )
    messages = [
        {"role": "system", "content": system_prompt},
    ]
    if context:
        messages.append({"role": "user", "content": f"Context:\n{context}"})
    messages.append({"role": "user", "content": query})
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 512
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        answer = data["choices"][0]["message"]["content"]
        return {
            "success": True,
            "query": query,
            "answer": answer
        }
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401:
            return {
                "success": False,
                "error": f"Unauthorized (401): Check your MISTRAL_API_KEY. {resp.text}",
                "query": query
            }
        return {
            "success": False,
            "error": f"HTTP error: {str(e)} - {resp.text}",
            "query": query
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }

def mistral_multi_search_tool(
    queries: List[str],
    summary_prompt: Optional[str] = None,
    model: str = "mistral-small-latest",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Perform multiple adjacent queries and summarize the results using Mistral LLM.
    Args:
        queries: List of search queries.
        summary_prompt: Optional custom prompt for summary.
        model: Mistral model to use.
        api_key: API key for Mistral.
    Returns:
        Dict with 'success', 'queries', 'results', and 'summary' or 'error'.
    """
    key = api_key or os.environ.get("MISTRAL_API_KEY") or get_mistral_api_key()
    if not key:
        return {
            "success": False,
            "error": "MISTRAL_API_KEY not set in environment.",
            "queries": queries
        }
    # Step 1: Run each query individually
    individual_results = []
    for q in queries:
        res = mistral_search_tool(q, api_key=key, model=model)
        individual_results.append({
            "query": q,
            "answer": res.get("answer"),
            "success": res.get("success"),
            "error": res.get("error") if not res.get("success") else None
        })
    # Step 2: Compose a summary prompt
    summary_prompt = summary_prompt or (
        "You are a helpful assistant. Summarize and synthesize the following search results for the user, "
        "highlighting key points and any consensus or disagreement. "
        "If any results are missing or failed, note that as well."
    )
    # Compose context for summary
    context_lines = []
    for idx, res in enumerate(individual_results):
        if res["success"]:
            context_lines.append(f"Result {idx+1} for '{res['query']}':\n{res['answer']}\n")
        else:
            context_lines.append(f"Result {idx+1} for '{res['query']}':\n[Error: {res['error']}]\n")
    summary_context = "\n".join(context_lines)
    # Step 3: Ask Mistral to summarize
    summary_result = mistral_search_tool(
        query="Please summarize and synthesize the above search results.",
        context=summary_context,
        model=model,
        api_key=key
    )
    return {
        "success": True if summary_result.get("success") else False,
        "queries": queries,
        "results": individual_results,
        "summary": summary_result.get("answer"),
        "summary_error": summary_result.get("error") if not summary_result.get("success") else None
    }

# =============================================================================
#  TOOL SCHEMAS
# =============================================================================
def get_mistral_search_schema() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "mistral_search_tool",
            "description": "Ask a web search question to the Mistral LLM, optionally with context.",
            "parameters": {
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {"type": "string", "description": "The question to ask the LLM"},
                    "context": {"type": "string", "description": "Optional context or web text to provide", "default": ""}
                }
            }
        }
    }

def get_mistral_multi_search_schema() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "mistral_multi_search_tool",
            "description": "Ask multiple adjacent web search questions to the Mistral LLM and receive a synthesized summary.",
            "parameters": {
                "type": "object",
                "required": ["queries"],
                "properties": {
                    "queries": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "A list of related search questions to ask the LLM"
                    },
                    "summary_prompt": {
                        "type": "string",
                        "description": "Optional custom prompt for summary synthesis",
                        "default": ""
                    }
                }
            }
        }
    }

def get_tool_schemas():
    """Return all tool schemas for this module."""
    return [
        {
            "name": "ChatGPT Search",
            "display_name": "ChatGPT Search",
            "description": "Search the web using the OpenAI API and retrieve formatted results.",
            "type": "function",
            "function": {
                "name": "chatgpt_search",
                "display_name": "ChatGPT Search",
                "description": "Search the web using the OpenAI API and retrieve formatted results.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to look up."
                        },
                        "model": {
                            "type": "string",
                            "description": "OpenAI model to use for search (e.g., gpt-4)",
                            "default": "gpt-4"
                        },
                        "context": {
                            "type": "string",
                            "description": "Optional context to help guide the search."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "name": "ChatGPT Multi-Search",
            "display_name": "ChatGPT Multi-Search",
            "description": "Perform multiple adjacent web searches using ChatGPT and return a summary.",
            "type": "function",
            "function": {
                "name": "chatgpt_multi_search",
                "display_name": "ChatGPT Multi-Search",
                "description": "Perform multiple adjacent web searches using ChatGPT and return a summary.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The core search query to expand upon."
                        },
                        "model": {
                            "type": "string",
                            "description": "OpenAI model to use for search and summarization.",
                            "default": "gpt-4"
                        },
                        "num_adjacent": {
                            "type": "integer",
                            "description": "Number of adjacent queries to generate.",
                            "default": 4
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]

TOOL_SCHEMAS = get_tool_schemas()

# =============================================================================
#  TOOL CALL HANDLER
# =============================================================================
def handle_tool_calls(tool_calls: List[Dict[str, Any]], config: Optional[dict] = None) -> List[Dict[str, Any]]:
    """
    Handles a list of tool calls, dispatching to the correct tool and returning standardized responses.
    """
    config = load_config(
        env_path=abspath(join(dirname(__file__), '..', '.env')),
        swarm_path=None,
        cli_args=config or {}
    )
    mistral_api_key = get_mistral_api_key(config)
    results = []
    for tool_call in tool_calls:
        tool_call_id = tool_call.get("id", "")
        function = tool_call.get("function", {})
        name = function.get("name", "")
        arguments = function.get("arguments", "{}")
        try:
            args = json.loads(arguments) if isinstance(arguments, str) else arguments
        except Exception:
            args = {}
        if name == "mistral_search_tool":
            query = args.get("query", "")
            context = args.get("context", None)
            if not query:
                error_msg = "Missing required parameter: query"
                results.append(standardize_tool_response(
                    tool_call_id=tool_call_id,
                    result={"message": error_msg},
                    tool_name="mistral_search_tool",
                    status="error"
                ))
                continue
            try:
                result = mistral_search_tool(query, context, api_key=mistral_api_key)
                results.append(standardize_tool_response(
                    tool_call_id=tool_call_id,
                    result=result,
                    tool_name="mistral_search_tool"
                ))
            except Exception as e:
                error_msg = f"Error executing mistral_search_tool: {str(e)}"
                results.append(standardize_tool_response(
                    tool_call_id=tool_call_id,
                    result={"message": error_msg},
                    tool_name="mistral_search_tool",
                    status="error"
                ))
            continue
        elif name == "mistral_multi_search_tool":
            queries = args.get("queries", [])
            summary_prompt = args.get("summary_prompt", None)
            if not queries or not isinstance(queries, list):
                error_msg = "Missing or invalid required parameter: queries (must be a list of strings)"
                results.append(standardize_tool_response(
                    tool_call_id=tool_call_id,
                    result={"message": error_msg},
                    tool_name="mistral_multi_search_tool",
                    status="error"
                ))
                continue
            try:
                result = mistral_multi_search_tool(queries, summary_prompt, api_key=mistral_api_key)
                results.append(standardize_tool_response(
                    tool_call_id=tool_call_id,
                    result=result,
                    tool_name="mistral_multi_search_tool"
                ))
            except Exception as e:
                error_msg = f"Error executing mistral_multi_search_tool: {str(e)}"
                results.append(standardize_tool_response(
                    tool_call_id=tool_call_id,
                    result={"message": error_msg},
                    tool_name="mistral_multi_search_tool",
                    status="error"
                ))
            continue
        else:
            error_msg = f"Unknown tool: {name}"
            results.append(standardize_tool_response(
                tool_call_id=tool_call_id,
                result={"message": error_msg},
                tool_name="swarm_search",
                status="error"
            ))
    return results

# =============================================================================
# Swarm System Integration
# =============================================================================

def register_with_registry(registry=None):
    """
    Register this module's tools with the Swarm registry.
    Compatible with both registry argument pattern and global registry.
    """
    try:
        # If registry is provided directly
        if registry is not None:
            # Check if register_tools_from_schemas method exists
            if hasattr(registry, "register_tools_from_schemas"):
                registry.register_tools_from_schemas(
                    TOOL_SCHEMAS, 
                    handle_tool_calls,
                    module_name="mistral_search"
                )
                return True
            # Fall back to register_tool if needed
            elif hasattr(registry, "register_tool"):
                for schema in TOOL_SCHEMAS:
                    function_name = schema["function"]["name"]
                    registry.register_tool(
                        name=function_name,
                        schema=schema,
                        handler=handle_tool_calls
                    )
                return True
        # Otherwise try to get registry from core module
        else:
            try:
                from core.core_registry import get_registry
                local_registry = get_registry()
                return register_with_registry(local_registry)
            except ImportError:
                print("Could not import core_registry. Tools not registered.")
                return False
    except Exception as e:
        print(f"Error registering Mistral search tools: {str(e)}")
        return False

# =============================================================================
#  CLI ENTRYPOINT (with interactive chat for Mistral)
# =============================================================================
def interactive_cli():
    print(f"{Fore.MAGENTA}{SWARM_LOGO}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Unified Search Tool (Mistral Edition) Interactive CLI{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'help' for commands, 'exit' to quit.{Style.RESET_ALL}")
    while True:
        try:
            user_input = input(f"{Fore.CYAN}search> {Style.RESET_ALL}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print(f"{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
            break
        if user_input.lower() == "help":
            print(f"{Fore.YELLOW}Available commands:{Style.RESET_ALL}")
            print("  mistral <question>            - Ask Mistral LLM a web search question")
            print("  mistralc <question>|<context> - Ask Mistral LLM with context")
            print("  help                          - Show this help")
            print("  exit                          - Exit CLI")
            continue
        if user_input.startswith("mistralc "):
            _, rest = user_input.split(" ", 1)
            if "|" in rest:
                question, context = rest.split("|", 1)
                mistral_api_key = get_mistral_api_key()
                result = mistral_search_tool(question.strip(), context.strip(), api_key=mistral_api_key)
            else:
                mistral_api_key = get_mistral_api_key()
                result = mistral_search_tool(rest.strip(), api_key=mistral_api_key)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif user_input.startswith("mistral "):
            _, question = user_input.split(" ", 1)
            mistral_api_key = get_mistral_api_key()
            result = mistral_search_tool(question.strip(), api_key=mistral_api_key)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"{Fore.RED}Unknown command. Type 'help' for available commands.{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description="Unified Search Tool CLI for Swarm Agent Orchestration (Mistral Edition)")
    add_standard_cli_args(parser)
    parser.add_argument("--chat", action="store_true", help="Run chat-based interactive CLI (recommended)")
    parser.add_argument("--tool", choices=[
        "mistral_search_tool"
    ], help="Which tool to run")
    parser.add_argument("--query", type=str, help="Search query for mistral_search_tool")
    parser.add_argument("--context", type=str, help="Context for mistral_search_tool")
    parser.add_argument("--test", type=str, help="Test a tool or 'all'")
    parser.add_argument("--mistral_api_key", type=str, help="Mistral API key (overrides env/config)")
    parser.add_argument("--register", action="store_true", help="Register tools with Swarm registry")
    args = parser.parse_args()
    
    if args.register:
        register_with_registry()
        return
    
    config = load_config(env_path=args.env, swarm_path=args.config, cli_args=vars(args))
    mistral_api_key = args.mistral_api_key or get_mistral_api_key(config)
    if args.chat or (not args.tool and not args.test):
        interactive_cli()
        return
    if args.test:
        print(f"{Fore.CYAN}Running tests for Search tools...{Style.RESET_ALL}")
        if args.test == "all" or args.test == "mistral_search_tool":
            print(f"{Fore.YELLOW}[mistral_search_tool] test:{Style.RESET_ALL}")
            print(json.dumps(mistral_search_tool("What is the capital of France?", api_key=mistral_api_key), indent=2, ensure_ascii=False))
        return
    if args.tool == "mistral_search_tool":
        if not args.query:
            print(f"{Fore.RED}Error: --query is required for mistral_search_tool{Style.RESET_ALL}")
            sys.exit(1)
        result = mistral_search_tool(args.query, args.context, api_key=mistral_api_key)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        parser.print_help()
        print(f"\n{Fore.YELLOW}Example: python mistral_search.py --tool mistral_search_tool --query 'climate change'{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
###############################################################################