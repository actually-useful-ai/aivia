#!/usr/bin/env python3
"""
OpenAI Chat CLI with Web Search and Vector Store Support

This script provides a CLI for interacting with the OpenAI API, including:
- Streaming chat responses
- Web search and file search (vector store) tools
- Model selection and listing
- Vector store management

Accessibility: CLI output is screen reader and terminal friendly.
Error Handling: Robust error handling for API and JSON parsing.
"""

import sys
import os
import json
from typing import List, Dict, Optional, Union
from datetime import datetime

# --- OpenAI Python SDK Import ---
try:
    from openai import OpenAI
except ImportError:
    print("The openai Python package is required. Install with: pip install openai", file=sys.stderr)
    sys.exit(1)

class OpenAIChat:
    """
    High-level interface for OpenAI model listing, vector store management,
    and /v1/responses (web and file search tools).
    """
    DEFAULT_MODELS = {
        "gpt-4-vision-preview": {
            "id": "gpt-4-vision-preview",
            "context_length": 128000,
            "description": "GPT-4 Turbo with image understanding",
            "capabilities": ["text", "vision", "function"]
        },
        "gpt-4-0125-preview": {
            "id": "gpt-4-0125-preview",
            "context_length": 128000,
            "description": "Most capable GPT-4 model",
            "capabilities": ["text", "function"]
        },
        "gpt-4": {
            "id": "gpt-4",
            "context_length": 8192,
            "description": "More capable GPT-4 model",
            "capabilities": ["text", "function"]
        },
        "gpt-3.5-turbo-0125": {
            "id": "gpt-3.5-turbo-0125",
            "context_length": 16385,
            "description": "Most capable GPT-3.5 model",
            "capabilities": ["text", "function"]
        }
    }

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.models = self._fetch_models()
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on providing accurate and detailed responses."
        }]

    def _fetch_models(self) -> Dict:
        try:
            models = {}
            response = self.client.models.list()
            for model in response.data:
                mid = model.id
                created = datetime.fromtimestamp(model.created)
                caps = ["text"]
                if "vision" in mid.lower():
                    caps.append("vision")
                if not any(x in mid.lower() for x in ["instruct", "base"]):
                    caps.append("function")
                ctx_len = 8192
                if "32k" in mid:
                    ctx_len = 32768
                elif "16k" in mid:
                    ctx_len = 16385
                elif "128k" in mid or "vision" in mid:
                    ctx_len = 128000
                desc = "OpenAI " + mid
                if "4" in mid:
                    desc = "Most capable GPT-4 model"
                elif "3.5" in mid:
                    desc = "Efficient GPT-3.5 model"
                if "vision" in mid:
                    desc += " with image understanding"
                generation = "4" if "4" in mid else "3.5" if "3.5" in mid else "3"
                version = "preview" if "preview" in mid else (mid.split('-')[-1] if '-' in mid else None)
                models[mid] = {
                    "id": mid,
                    "context_length": ctx_len,
                    "description": desc,
                    "capabilities": caps,
                    "capability_count": len(caps),
                    "created": created,
                    "created_str": created.strftime("%Y-%m-%d"),
                    "generation": generation,
                    "version": version,
                    "owned_by": getattr(model, "owned_by", "openai")
                }
            return models or self.DEFAULT_MODELS
        except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            return self.DEFAULT_MODELS

    def list_models(
        self,
        sort_by: str = "created",
        reverse: bool = True,
        page: int = 1,
        page_size: int = 5,
        generation: Optional[str] = None
    ) -> List[Dict]:
        models_list = [
            {
                "id": info["id"],
                "name": mid,
                "context_length": info["context_length"],
                "description": info["description"],
                "capabilities": info["capabilities"],
                "capability_count": info.get("capability_count", len(info.get("capabilities", []))),
                "created": info["created"],
                "created_str": info["created_str"],
                "generation": info["generation"],
                "version": info["version"],
                "owned_by": info["owned_by"]
            }
            for mid, info in self.models.items()
            if not generation or info["generation"] == generation
        ]
        if sort_by == "created":
            models_list.sort(key=lambda x: x["created"], reverse=reverse)
        elif sort_by == "context_length":
            models_list.sort(key=lambda x: x["context_length"], reverse=reverse)
        elif sort_by == "capabilities":
            models_list.sort(key=lambda x: (
                x["capability_count"],
                "vision" in x["capabilities"],
                "function" in x["capabilities"]
            ), reverse=reverse)
        else:
            models_list.sort(key=lambda x: x["id"], reverse=reverse)

        start = (page - 1) * page_size
        return models_list[start:start + page_size]

    def list_vector_stores(self) -> List[Dict]:
        try:
            result = self.client.vector_stores.list()
            return [vs.model_dump() for vs in result.data]
        except Exception as e:
            print(f"Error listing vector stores: {e}", file=sys.stderr)
            return []

    def create_response_with_web_search(
        self,
        input_text: str,
        model: str = "gpt-4.1-mini",
        tools: Optional[List[Dict]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        seed: Optional[int] = None,
        extra_kwargs: Optional[dict] = None
    ) -> str:
        payload = {"model": model, "input": input_text}
        if tools:
            for tool in tools:
                if tool.get("type") == "web_search_preview":
                    tool["type"] = "web_search"
            payload["tools"] = tools
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_output_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if stop is not None:
            payload["stop"] = stop
        if seed is not None:
            payload["seed"] = seed
        if extra_kwargs:
            payload.update(extra_kwargs)

        try:
            result = self.client.responses.create(**payload)
            output = getattr(result, "output", None)
            if output:
                for item in output:
                    item_dict = item.model_dump() if hasattr(item, "model_dump") else (
                        item.to_dict() if hasattr(item, "to_dict") else item)
                    item_type = item_dict.get("type") or getattr(item, "type", None)
                    if item_type == "message":
                        text_parts: List[str] = []
                        for part in item_dict.get("content", []):
                            part_dict = part.model_dump() if hasattr(part, "model_dump") else (
                                part.to_dict() if hasattr(part, "to_dict") else part)
                            if part_dict.get("type") == "output_text":
                                text_parts.append(part_dict.get("text", ""))
                        return "".join(text_parts).strip() or json.dumps(item_dict, indent=2)
                dumped_list = [
                    itm.model_dump() if hasattr(itm, "model_dump") else (
                        itm.to_dict() if hasattr(itm, "to_dict") else itm
                    )
                    for itm in output
                ]
                return json.dumps(dumped_list, indent=2)
            full_resp = result.model_dump() if hasattr(result, "model_dump") else (
                result.to_dict() if hasattr(result, "to_dict") else result.__dict__)
            return json.dumps(full_resp, indent=2)
        except Exception as e:
            print(f"Error in create_response_with_web_search: {e}", file=sys.stderr)
            return f"Error: {e}"

    def clear_conversation(self):
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on providing accurate and detailed responses."
        }]

# --- CLI Utilities ---

def display_models(
    models: List[Dict],
    current_page: int,
    total_pages: int,
    sort_by: str,
    generation: Optional[str] = None
) -> None:
    print(f"\nAvailable OpenAI Models (Page {current_page}/{total_pages}):")
    if generation:
        print(f"Filtering: GPT-{generation} models")
    print(f"Sorting by: {sort_by}")
    print("-" * 50)
    for idx, model in enumerate(models, 1):
        print(f"{idx}. {model['name']}")
        print(f"   Model: {model['id']}")
        print(f"   Context Length: {model['context_length']} tokens")
        print(f"   Description: {model['description']}")
        print(f"   Capabilities: {', '.join(model['capabilities'])}")
        print(f"   Released: {model['created_str']}")
        if model['version']:
            print(f"   Version: {model['version']}")
        print(f"   Owner: {model['owned_by']}")
        print()

def get_user_input(prompt: str, default: str = None) -> str:
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    response = input(prompt).strip()
    return response if response else default

def main():
    """
    Interactive CLI for OpenAI vector store and /v1/responses tool usage.
    """
    api_key = os.environ.get("OPENAI_API_KEY") or ""
    if not api_key:
        print("Please set the OPENAI_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)
    chat = OpenAIChat(api_key)
    default_model = "gpt-4.1-mini"
    selected_model = default_model
    default_vs_id = ""
    default_file_id = ""

    def model_selection_menu():
        nonlocal selected_model
        page = 1
        page_size = 5
        sort_by = "created"
        generation = None
        capability_filter = None
        while True:
            all_models = chat.list_models(sort_by=sort_by, page=1, page_size=1000, generation=generation)
            if capability_filter:
                all_models = [
                    model for model in all_models 
                    if capability_filter in model["capabilities"]
                ]
            total_pages = (len(all_models) + page_size - 1) // page_size
            models = chat.list_models(
                sort_by=sort_by,
                page=page,
                page_size=page_size,
                generation=generation
            )
            if capability_filter:
                models = [
                    model for model in models 
                    if capability_filter in model["capabilities"]
                ]
            display_models(models, page, total_pages, sort_by, generation)
            print("\nOptions:")
            print("1. Select model")
            print("2. Next page")
            print("3. Previous page")
            print("4. Sort by (created/context_length/id/capabilities)")
            print("5. Filter by generation (4/3.5/3/none)")
            print("6. Filter by capability (text/function/vision/none)")
            print("7. Change page size")
            print("8. Back to main menu")
            choice = get_user_input("Select option", "1")
            if choice == "1":
                try:
                    selection = int(get_user_input("Select a model number", "1")) - 1
                    if 0 <= selection < len(models):
                        selected_model = models[selection]["name"]
                        print(f"Selected model: {selected_model}")
                        break
                    print("Invalid selection. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
            elif choice == "2":
                if page < total_pages:
                    page += 1
            elif choice == "3":
                if page > 1:
                    page -= 1
            elif choice == "4":
                sort_by = get_user_input(
                    "Sort by (created/context_length/id/capabilities)",
                    "created"
                )
                page = 1
            elif choice == "5":
                gen = get_user_input(
                    "Filter by generation (4/3.5/3/none)",
                    "none"
                )
                generation = None if gen.lower() == "none" else gen
                page = 1
            elif choice == "6":
                cap_choice = get_user_input(
                    "Filter by capability (text/function/vision/none)",
                    "none"
                ).lower()
                capability_filter = None if cap_choice == "none" else cap_choice
                page = 1
            elif choice == "7":
                try:
                    new_size = int(get_user_input("Enter page size", str(page_size)))
                    if new_size > 0:
                        page_size = new_size
                        page = 1
                except ValueError:
                    print("Please enter a valid number.")
            elif choice == "8":
                break
            print()

    while True:
        print("\n=== OpenAI Chat CLI ===")
        print(f"Default model: {selected_model}")
        print("1. Ask a question (quick start)")
        print("2. Model selection")
        print("3. Quit")
        main_choice = get_user_input("Select an option", "1")
        if main_choice == "1":
            while True:
                print("\n--- Ask OpenAI (Quick) ---")
                input_text = get_user_input("Input (your question)", "What was a positive news story from today?")
                print(f"Using model: {selected_model}")
                tools = [{"type": "web_search"}]
                if get_user_input("Enable file search tool? (y/n)", "n").lower() == "y":
                    vs_id = get_user_input("Vector store ID (only one allowed)", default_vs_id)
                    max_results = get_user_input("Max number of results (int)", "10")
                    try:
                        max_results = int(max_results)
                    except ValueError:
                        max_results = 10
                    file_id_for_query = get_user_input("File ID to use for file search (leave blank to use all files in vector store)", default_file_id)
                    vector_store_ids = [vs_id] if vs_id else []
                    tools.append({
                        "type": "file_search",
                        "vector_store_ids": vector_store_ids,
                        "max_num_results": max_results
                    })
                if get_user_input("Enable computer use tool? (y/n)", "n").lower() == "y":
                    integration = get_user_input("Integration (playwright)", "playwright")
                    tools.append({
                        "type": "computer_use",
                        "integration": integration
                    })
                if get_user_input("Show advanced parameters? (y/n)", "n").lower() == "y":
                    temperature = get_user_input("Temperature (float 0-2)", "")
                    temperature = float(temperature) if temperature else None

                    max_tokens = get_user_input("Max tokens (int)", "")
                    max_tokens = int(max_tokens) if max_tokens else None

                    top_p = get_user_input("Top-p (float 0-1)", "")
                    top_p = float(top_p) if top_p else None

                    stop = get_user_input("Stop sequence(s) (comma separated or blank)", "")
                    if stop:
                        stop = [s.strip() for s in stop.split(",")] if "," in stop else stop.strip()
                    else:
                        stop = None

                    seed = get_user_input("Seed (int)", "")
                    seed = int(seed) if seed else None

                    extra_kwargs = {}
                    add_extra = get_user_input("Add extra parameters? (y/n)", "n").lower() == "y"
                    while add_extra:
                        key = get_user_input("Parameter name (or blank to stop)", "")
                        if not key:
                            break
                        value = get_user_input(f"Value for '{key}'", "")
                        try:
                            parsed = json.loads(value)
                        except Exception:
                            parsed = value
                        extra_kwargs[key] = parsed
                else:
                    temperature = None
                    max_tokens = None
                    top_p = None
                    stop = None
                    seed = None
                    extra_kwargs = None

                print("\nSending request to /v1/responses ...\n")
                response = chat.create_response_with_web_search(
                    input_text=input_text,
                    model=selected_model,
                    tools=tools,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    stop=stop,
                    seed=seed,
                    extra_kwargs=extra_kwargs if extra_kwargs else None
                )
                print("\n--- Response ---")
                print(response)
                print("-" * 50)

                if get_user_input("\nAsk another question? (y/n)", "y").lower() != 'y':
                    print("\nClearing conversation history and returning to main menu...")
                    chat.clear_conversation()
                    break
                print("\nContinuing...\n")
        elif main_choice == "2":
            model_selection_menu()
        elif main_choice == "3":
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid selection, try again.")

if __name__ == "__main__":
    main()
