###############################################################################
# SWARM KNOWLEDGE DICTIONARY MODULE
# Interactive CLI for Dictionary & Terminology Lookup (Merriam-Webster)
# ----------------------------------------------------------------------
# This module is a tool for a Swarm agent or orchestrator.
# Use it to look up definitions and explanations for general, academic,
# or medical terms using the Merriam-Webster API.
#
# TOOLS AVAILABLE:
#   1. define_word: Look up a word in the Learner's or Medical dictionary.
#
# HOW TO USE:
#   - Use this module when you need to provide clear, accessible definitions
#     for users, especially in educational, clinical, or technical contexts.
#   - The CLI is interactive, styled, and supports direct chat with the Swarm agent.
#   - "test all" will run all available tool tests.
###############################################################################

import os
import sys
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    class Dummy:
        def __getattr__(self, k): return ''
    Fore = Style = Dummy()

# Load .env for credentials
load_dotenv()

# Swarm logo (if available)
SWARM_LOGO = ""
try:
    with open(os.path.join(os.path.dirname(__file__), "..", ".swarm"), "r", encoding="utf-8") as f:
        SWARM_LOGO = f.read()
except Exception:
    SWARM_LOGO = "🐝 SWARM"

XAI_API_ENDPOINT = "https://api.x.ai/v1/chat/completions"

def get_mw_api_keys() -> Dict[str, str]:
    learners = os.environ.get("MIRRIAM_WEBSTER_LEARNERS")
    medical = os.environ.get("MIRRIAM_WEBSTER_MEDICAL")
    if not learners or not medical:
        raise ValueError("Both MIRRIAM_WEBSTER_LEARNERS and MIRRIAM_WEBSTER_MEDICAL must be set in .env")
    return {"learners": learners, "medical": medical}

def define_word(word: str, dictionary_type: str = "learners") -> Dict[str, Any]:
    """
    Look up a word in the Merriam-Webster Learner's or Medical dictionary.
    Returns a dictionary with the word, definitions, and any error.
    """
    keys = get_mw_api_keys()
    base_url = "https://www.dictionaryapi.com/api/v3/references/"
    if dictionary_type == "medical":
        api_key = keys["medical"]
        endpoint = "medical/json/"
    else:
        api_key = keys["learners"]
        endpoint = "learners/json/"
    url = f"{base_url}{endpoint}{word}?key={api_key}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        definitions = resp.json()
        if not definitions or (isinstance(definitions, list) and not definitions[0]):
            return {"word": word, "definitions": [], "error": f"No definition found for '{word}'."}
        entry = definitions[0]
        word_id = entry.get("meta", {}).get("id", word)
        shortdef = entry.get("shortdef", ["No definition available"])
        return {"word": word_id, "definitions": shortdef, "error": None}
    except Exception as e:
        return {"word": word, "definitions": [], "error": str(e)}

def get_tool_schema() -> dict:
    schema = {
        "type": "function",
        "function": {
            "name": "define_word",
            "description": "Look up a word in the Merriam-Webster Learner's or Medical dictionary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "word": {
                        "type": "string",
                        "description": "The word to look up."
                    },
                    "dictionary_type": {
                        "type": "string",
                        "description": "Dictionary type: 'learners' or 'medical'.",
                        "default": "learners"
                    }
                },
                "required": ["word"]
            }
        }
    }
    if "function" in schema:
        schema["function"]["module"] = "swarm_dictionary"
    return schema

def get_tool_schemas():
    schemas = [get_tool_schema()]
    for schema in schemas:
        if "function" in schema:
            schema["function"]["module"] = "swarm_dictionary"
    return schemas

# Define TOOL_SCHEMAS for discovery by the swarm master
TOOL_SCHEMAS = get_tool_schemas()

def handle_tool_calls(tool_calls, config: dict = None):
    tool_results = []
    for tool_call in tool_calls:
        tool_call_id = tool_call.get("id")
        function = tool_call.get("function", {})
        name = function.get("name")
        arguments = function.get("arguments", "{}")
        try:
            args = json.loads(arguments)
        except json.JSONDecodeError:
            args = {}
        if name == "define_word":
            word = args.get("word", "")
            dictionary_type = args.get("dictionary_type", "learners")
            print(f"\n{Fore.CYAN}📖 Looking up: {Fore.YELLOW}{word} ({dictionary_type}){Style.RESET_ALL}")
            result = define_word(word, dictionary_type)
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

def parse_stream_chunk(chunk: str) -> Optional[Dict[str, Any]]:
    if not chunk.strip() or chunk.strip() == "data: [DONE]":
        return None
    if chunk.startswith("data: "):
        data = chunk[6:]
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None
    return None

def interactive_cli(api_key: Optional[str] = None, model: str = "grok-3",
                    temperature: float = 0.7, max_tokens: int = 800,
                    system_prompt: Optional[str] = None):
    """
    Interactive CLI for dictionary and terminology lookup.
    This version fixes the infinite loop by ensuring the assistant's response
    is handled only once per user input, and tool calls are processed in a single pass.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key or os.environ.get('XAI_API_KEY', '')}"
    }
    tools = [get_tool_schema()]
    if not system_prompt:
        system_prompt = (
            "You are a dictionary and terminology lookup assistant for a Swarm agent. "
            "When the agent or user needs a definition or explanation of a word, "
            "use the define_word tool. Always provide clear, accessible definitions. "
            "Use this tool for: general vocabulary, academic terms, medical terminology, "
            "and when clarification is needed. Do not hallucinate results. "
            "If a word is not found, state so clearly."
        )
    print(f"\n{Fore.GREEN}{SWARM_LOGO}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}SWARM KNOWLEDGE DICTIONARY MODULE - INTERACTIVE CLI FOR AGENT TOOLING{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Available tools in @knowledge_dictionary.py:{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}- define_word{Style.RESET_ALL}: Look up a word in the Learner's or Medical dictionary.")
    print(f"\n{Fore.CYAN}This module is a tool for a Swarm agent or orchestrator. Use it when you need to:\n"
          f"  {Fore.YELLOW}- Provide definitions for general, academic, or medical terms\n"
          f"  - Clarify vocabulary for users\n"
          f"  - Support accessible communication\n"
          f"{Fore.CYAN}Type {Fore.YELLOW}'test all'{Fore.CYAN} to run all tool tests.\n"
          f"Type {Fore.YELLOW}'exit', 'quit', or Ctrl+C{Fore.CYAN} to end the conversation.{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}\n")
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    try:
        while True:
            user_input = input(f"\n{Fore.YELLOW}🧑 You:{Style.RESET_ALL} ")
            if user_input.lower() in ["exit", "quit", "q"]:
                print(f"\n{Fore.GREEN}Goodbye! 👋{Style.RESET_ALL}")
                break
            if user_input.strip().lower() == "test all":
                print(f"\n{Fore.CYAN}Running all tool tests...{Style.RESET_ALL}")
                print(f"\n{Fore.BLUE}[define_word] test:{Style.RESET_ALL}")
                print(json.dumps(define_word("artificial"), indent=2, ensure_ascii=False))
                print(json.dumps(define_word("aphasia", "medical"), indent=2, ensure_ascii=False))
                continue
            messages.append({"role": "user", "content": user_input})

            # --- Single assistant response per user input ---
            print(f"\n{Fore.CYAN}🤖 Dictionary Assistant:{Style.RESET_ALL} ", end="", flush=True)
            payload = {
                "model": model,
                "messages": messages,
                "tools": tools,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            response = requests.post(
                XAI_API_ENDPOINT,
                headers=headers,
                json=payload,
                stream=True
            )
            if response.status_code != 200:
                print(f"\n{Fore.RED}API Error ({response.status_code}): {response.text}{Style.RESET_ALL}")
                continue

            assistant_content = ""
            assistant_tool_calls = []
            current_tool_calls = {}

            # Stream and parse the assistant's response
            for line in response.iter_lines():
                if not line:
                    continue
                chunk_str = line.decode('utf-8')
                if chunk_str.strip() == "data: [DONE]":
                    continue
                if chunk_str.startswith("data: "):
                    try:
                        chunk_data = json.loads(chunk_str[6:])
                    except json.JSONDecodeError:
                        continue
                    choices = chunk_data.get("choices", [])
                    if not choices:
                        continue
                    choice = choices[0]
                    delta = choice.get("delta", {})
                    if "content" in delta and delta["content"]:
                        content = delta["content"]
                        assistant_content += content
                        print(f"{Fore.WHITE}{content}{Style.RESET_ALL}", end="", flush=True)
                    if "tool_calls" in delta:
                        tool_calls_delta = delta["tool_calls"]
                        for tool_call_delta in tool_calls_delta:
                            index = tool_call_delta.get("index", 0)
                            if index not in current_tool_calls:
                                current_tool_calls[index] = {
                                    "id": "",
                                    "function": {"name": "", "arguments": ""}
                                }
                            if "id" in tool_call_delta:
                                current_tool_calls[index]["id"] = tool_call_delta["id"]
                            if "function" in tool_call_delta and "name" in tool_call_delta["function"]:
                                current_tool_calls[index]["function"]["name"] = tool_call_delta["function"]["name"]
                            if "function" in tool_call_delta and "arguments" in tool_call_delta["function"]:
                                current_tool_calls[index]["function"]["arguments"] += tool_call_delta["function"]["arguments"]

            assistant_tool_calls = list(current_tool_calls.values())
            assistant_message = {"role": "assistant", "content": assistant_content}
            messages.append(assistant_message)

            # --- Only process tool calls once per user input ---
            if assistant_tool_calls:
                tool_results = handle_tool_calls(assistant_tool_calls)
                for tool_result in tool_results:
                    messages.append(tool_result)
                    try:
                        content_str = tool_result.get("content", "{}")
                        content = json.loads(content_str) if isinstance(content_str, str) else content_str
                        defs = content.get("definitions", [])
                        if defs:
                            print(f"\n{Fore.GREEN}Found {len(defs)} definition(s).{Style.RESET_ALL}")
                    except (json.JSONDecodeError, AttributeError):
                        pass
                # After tool call, send a follow-up message to get the assistant's response
                print(f"\n{Fore.CYAN}🤖 Dictionary Assistant (after tool call):{Style.RESET_ALL} ", end="", flush=True)
                followup_payload = {
                    "model": model,
                    "messages": messages,
                    "tools": tools,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True
                }
                followup_response = requests.post(
                    XAI_API_ENDPOINT,
                    headers=headers,
                    json=followup_payload,
                    stream=True
                )
                if followup_response.status_code != 200:
                    print(f"\n{Fore.RED}API Error ({followup_response.status_code}): {followup_response.text}{Style.RESET_ALL}")
                    continue
                followup_content = ""
                for line in followup_response.iter_lines():
                    if not line:
                        continue
                    chunk_str = line.decode('utf-8')
                    if chunk_str.strip() == "data: [DONE]":
                        continue
                    if chunk_str.startswith("data: "):
                        try:
                            chunk_data = json.loads(chunk_str[6:])
                        except json.JSONDecodeError:
                            continue
                        choices = chunk_data.get("choices", [])
                        if not choices:
                            continue
                        choice = choices[0]
                        delta = choice.get("delta", {})
                        if "content" in delta and delta["content"]:
                            content = delta["content"]
                            followup_content += content
                            print(f"{Fore.WHITE}{content}{Style.RESET_ALL}", end="", flush=True)
                messages.append({"role": "assistant", "content": followup_content})

    except KeyboardInterrupt:
        print(f"\n\n{Fore.GREEN}Conversation ended by user. Goodbye! 👋{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n\n{Fore.RED}Error in conversation: {str(e)}{Style.RESET_ALL}")

def main():
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print(f"{Fore.RED}XAI_API_KEY not set in environment. Please add it to your .env file.{Style.RESET_ALL}")
        sys.exit(1)
    interactive_cli(api_key=api_key)

if __name__ == "__main__":
    main()