"""
Perplexity API Chat Implementation

This module provides a detailed, transparent interface to the Perplexity API for streaming chat responses,
including a 5x adjacent query multi-search mode inspired by ChatGPT Web Multi-Search.

All available metadata, tool feedback, and links are surfaced to the terminal for maximum transparency.
A special section at the end of each multi-search and summary run collects and displays all links and metadata found.

Accessibility: All output is formatted for screen readers and terminal clarity.
Error Handling: Comprehensive error handling for API and JSON parsing.
"""

# Module metadata for CLI and registry
MODULE_DISPLAY_NAME = "Perplexity Search"
MODULE_DESCRIPTION = "Perplexity API tools for web search, including multi-search capabilities with adjacent queries."

import requests
import json
import sys
import concurrent.futures
import re
from typing import Generator, List, Dict, Optional, Any
from datetime import datetime

def extract_links(text: str) -> List[str]:
    """Extract all URLs from a block of text."""
    if not text:
        return []
    # Simple regex for URLs (http/https)
    url_pattern = r'(https?://[^\s\]\)]+)'
    return re.findall(url_pattern, text)

def print_metadata_section(metadata: Dict[str, Any], section_title: str = "Metadata"):
    """Print a metadata dictionary in a readable way."""
    if not metadata:
        return
    print(f"\n--- {section_title} ---")
    for k, v in metadata.items():
        print(f"{k}: {v}")

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

class PerplexityChat:
    """
    PerplexityChat provides access to Perplexity's available chat models.
    Model list is kept up-to-date for accurate selection and context length reporting.

    Accessibility: All model descriptions are clear and concise for screen readers.
    """
    MODELS = {
        "sonar-deep-research": {
            "id": "sonar-deep-research",
            "context_length": 128000,
            "description": "Deep research and advanced chat completion"
        },
        "sonar-reasoning-pro": {
            "id": "sonar-reasoning-pro",
            "context_length": 128000,
            "description": "Advanced reasoning and analysis"
        },
        "sonar-reasoning": {
            "id": "sonar-reasoning",
            "context_length": 128000,
            "description": "Enhanced reasoning capabilities"
        },
        "sonar-pro": {
            "id": "sonar-pro",
            "context_length": 200000,
            "description": "Professional grade chat completion"
        },
        "sonar": {
            "id": "sonar",
            "context_length": 128000,
            "description": "Standard chat completion"
        },
        "r1-1776": {
            "id": "r1-1776",
            "context_length": 128000,
            "description": "Chat completion with r1-1776 model"
        }
    }

    def __init__(self, api_key: str):
        """Initialize the Perplexity client with the provided API key."""
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        # Initialize with system message
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]
    
    def list_models(self) -> List[Dict]:
        """
        Get available Perplexity models.
        
        Returns:
            List[Dict]: List of available models with their details
        """
        return [
            {
                "id": model_id,
                "name": model_id,
                "context_length": info["context_length"],
                "description": info["description"]
            }
            for model_id, info in self.MODELS.items()
        ]

    def stream_chat_response(
        self,
        message: str,
        model: str = "sonar",
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from Perplexity, printing all available metadata and tool feedback.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Add user message to history
        self.chat_history.append({
            "role": "user",
            "content": message
        })
        
        payload = {
            "model": model,
            "messages": self.chat_history,
            "temperature": temperature,
            "stream": True
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                stream=True
            )
            response.raise_for_status()
            
            full_response = ""
            all_metadata = []
            all_links = set()
            for line in response.iter_lines():
                if line:
                    try:
                        line_text = line.decode('utf-8')
                        if line_text.startswith("data: "):
                            line_text = line_text[6:]  # Remove "data: " prefix
                        if line_text == "[DONE]":
                            break
                        data = json.loads(line_text)
                        # Print all available metadata for this chunk
                        print_metadata_section(data, section_title="Perplexity API Chunk Metadata")
                        if data.get("choices") and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                content = delta["content"]
                                full_response += content
                                # Print any tool feedback or links in this chunk
                                links = extract_links(content)
                                if links:
                                    print(f"\n[Links found in chunk]:")
                                    for l in links:
                                        print(f"  {l}")
                                    all_links.update(links)
                                yield content
                        # Collect all metadata for later
                        all_metadata.append(data)
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error processing chunk: {e}", file=sys.stderr)
                        continue
            
            # Add assistant's response to history
            self.chat_history.append({
                "role": "assistant",
                "content": full_response
            })

            # Print a summary of all links found
            if all_links:
                print("\n=== All Links Found in This Chat Response ===")
                for l in sorted(all_links):
                    print(l)
                print("===")

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            # Remove the user message if request failed
            self.chat_history.pop()
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            # Remove the user message if request failed
            self.chat_history.pop()

    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]

    def generate_adjacent_queries(self, user_query: str, model: str = "sonar", temperature: float = 0.3) -> List[str]:
        """
        Generate five distinct but closely related search queries for a given user prompt.
        Returns a list of five queries. If parsing fails, returns five copies of the original query.
        Prints all metadata and feedback from the Perplexity assistant.
        """
        prompt = (
            f"Given the query '{user_query}', generate five distinct but closely related search queries. "
            "Return ONLY a JSON array of exactly five strings."
        )
        try:
            # Use a fresh chat history for this meta-query
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that generates related search queries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": temperature,
                "stream": False
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            print_metadata_section(data, section_title="Perplexity Adjacent Query Generation Metadata")
            text = ""
            if data.get("choices") and len(data["choices"]) > 0:
                text = data["choices"][0].get("message", {}).get("content", "")
                # Print any links in the assistant's message
                links = extract_links(text)
                if links:
                    print(f"\n[Links found in adjacent query generation]:")
                    for l in links:
                        print(f"  {l}")
            if not text:
                raise ValueError("No text content found in Perplexity response.")
            # Try to parse JSON
            try:
                queries = json.loads(text)
            except json.JSONDecodeError as je:
                text_stripped = text.strip()
                # Remove markdown code block if present
                if text_stripped.startswith("```") and text_stripped.endswith("```"):
                    text_stripped = "\n".join(text_stripped.splitlines()[1:-1])
                try:
                    queries = json.loads(text_stripped)
                except Exception:
                    raise ValueError(f"Could not parse JSON from Perplexity response: {text_stripped}") from je
            if isinstance(queries, list) and len(queries) == 5 and all(isinstance(q, str) for q in queries):
                return queries
            else:
                raise ValueError("Parsed queries are not a list of five strings.")
        except Exception as e:
            print(f"[Error] Generating adjacent queries: {e}", file=sys.stderr)
            # Fallback: return five copies of the original query
            return [user_query] * 5

    def fetch_search_result(self, query: str, model: str = "sonar", temperature: float = 0.7) -> Dict[str, Any]:
        """
        Perform a web search for the given query using Perplexity's API.
        Returns a dictionary with the query, summary, and all available metadata.
        Handles API and parsing errors gracefully.
        Prints all metadata and links found in the response.
        """
        prompt = f"Search the web for '{query}'. Provide a concise summary and include citations if available."
        try:
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that summarizes web search results with citations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": temperature,
                "stream": False
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            print_metadata_section(data, section_title=f"Perplexity Search Metadata for Query: {query}")
            summary = ""
            links = []
            if data.get("choices") and len(data["choices"]) > 0:
                summary = data["choices"][0].get("message", {}).get("content", "")
                links = extract_links(summary)
                if links:
                    print(f"\n[Links found in search result for '{query}']:")
                    for l in links:
                        print(f"  {l}")
            return {
                "query": query,
                "summary": summary.strip() if summary else "No summary available.",
                "metadata": data,
                "links": links
            }
        except Exception as e:
            print(f"[Error] Fetching search result for '{query}': {e}", file=sys.stderr)
            return {
                "query": query,
                "summary": f"Error: Could not fetch search result for '{query}'.",
                "metadata": {},
                "links": []
            }

    def summarize_final(self, results: List[Dict[str, Any]], model: str = "sonar", temperature: float = 0.7) -> Dict[str, Any]:
        """
        Summarize a list of search results into a cohesive overview.
        Returns a dictionary with the summary and all available metadata.
        Prints all metadata and links found in the summary.
        """
        combined = "\n\n".join(f"Query: {r['query']}\nSummary: {r['summary']}" for r in results)
        prompt = f"Summarize these search results into a cohesive overview:\n\n{combined}"
        try:
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that summarizes multiple search results."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": temperature,
                "stream": False
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            print_metadata_section(data, section_title="Perplexity Final Summary Metadata")
            summary = ""
            links = []
            if data.get("choices") and len(data["choices"]) > 0:
                summary = data["choices"][0].get("message", {}).get("content", "")
                links = extract_links(summary)
                if links:
                    print(f"\n[Links found in final summary]:")
                    for l in links:
                        print(f"  {l}")
            return {
                "summary": summary.strip() if summary else "No summary generated.",
                "metadata": data,
                "links": links
            }
        except Exception as e:
            print(f"[Error] Final summarization: {e}", file=sys.stderr)
            return {
                "summary": "Error: Could not generate final summary.",
                "metadata": {},
                "links": []
            }

def display_models(models: List[Dict]) -> None:
    """Display available models in a formatted way."""
    print("\nAvailable Perplexity Models:")
    print("-" * 50)
    for idx, model in enumerate(models, 1):
        print(f"{idx}. {model['name']}")
        print(f"   Context Length: {model['context_length']} tokens")
        print(f"   Description: {model['description']}")
        print()

def get_user_input(prompt: str, default: str = None) -> str:
    """Get user input with an optional default value."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    response = input(prompt).strip()
    return response if response else default

def display_multi_search_results(results: List[Dict[str, Any]]) -> None:
    """Display multi-search results in a readable, accessible format, including all metadata and links."""
    print("\nMulti-Search Results (5x):")
    print("-" * 70)
    for idx, r in enumerate(results, 1):
        summary = r['summary'][:150] + "..." if len(r['summary']) > 150 else r['summary']
        print(f"{idx}. Query: {r['query']}")
        print(f"   Summary: {summary}")
        if r.get("links"):
            print(f"   Links:")
            for l in r["links"]:
                print(f"     {l}")
        if r.get("metadata"):
            print(f"   [Metadata available, see above for details]")
        print()
    print("-" * 70)

def display_all_links(results: List[Dict[str, Any]], final_summary: Dict[str, Any]):
    """Display a special section for all links captured throughout all searches and summary."""
    all_links = set()
    for r in results:
        for l in r.get("links", []):
            all_links.add(l)
    for l in final_summary.get("links", []):
        all_links.add(l)
    if all_links:
        print("\n=== Special Section: All Links Captured ===")
        for l in sorted(all_links):
            print(l)
        print("=" * 40)
    else:
        print("\n=== Special Section: No Links Captured ===")

def main():
    """
    Main CLI interface.
    Now supports:
      1. Standard chat
      2. 5x Multi-Search (adjacent queries)
    All available metadata, tool feedback, and links are surfaced to the terminal.
    """
    # Initialize with API key
    api_key = "REDACTED_XAI_KEY"
    chat = PerplexityChat(api_key)
    models = chat.list_models()
    display_models(models)

    # Get model selection
    while True:
        try:
            selection = int(get_user_input("Select a model number", "4")) - 1  # Default to sonar
            if 0 <= selection < len(models):
                selected_model = models[selection]["id"]
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

    # Main menu loop
    while True:
        print("\nChoose mode:")
        print("1. Standard chat")
        print("2. 5x Multi-Search (adjacent queries)")
        print("3. Exit")
        mode = get_user_input("Select option", "1")
        if mode == "3":
            print("\nClearing conversation history and exiting...")
            chat.clear_conversation()
            break
        elif mode == "2":
            # Multi-search mode
            user_query = get_user_input(
                "Enter your main search query",
                "What are the latest advances in AI for accessibility?"
            )
            print("\nGenerating 5 adjacent queries...")
            queries = chat.generate_adjacent_queries(user_query, model=selected_model)
            print("Running 5 parallel searches...\n")
            results = []
            # Use ThreadPoolExecutor for parallel API calls
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_query = {
                    executor.submit(chat.fetch_search_result, q, selected_model): q for q in queries
                }
                for future in concurrent.futures.as_completed(future_to_query):
                    try:
                        result = future.result()
                    except Exception as e:
                        result = {
                            "query": future_to_query[future],
                            "summary": f"Error: {e}",
                            "metadata": {},
                            "links": []
                        }
                    results.append(result)
            # Sort results to match original query order for accessibility
            results_sorted = []
            for q in queries:
                match = next((r for r in results if r["query"] == q), None)
                results_sorted.append(match if match else {"query": q, "summary": "No result.", "metadata": {}, "links": []})
            display_multi_search_results(results_sorted)
            print("Generating final comprehensive summary...\n")
            final_summary = chat.summarize_final(results_sorted, model=selected_model)
            print("Final Comprehensive Summary:")
            print("-" * 70)
            print(final_summary["summary"])
            print("-" * 70)
            display_all_links(results_sorted, final_summary)
            # Ask to continue
            if get_user_input("\nContinue? (y/n)", "y").lower() != 'y':
                print("\nClearing conversation history and exiting...")
                chat.clear_conversation()
                break
            print("\nReturning to main menu...\n")
        else:
            # Standard chat mode
            message = get_user_input(
                "Enter your message",
                "Tell me about yourself and your capabilities"
            )
            print("\nStreaming response:")
            print("-" * 50)
            for chunk in chat.stream_chat_response(message, selected_model):
                print(chunk, end="", flush=True)
            print("\n" + "-" * 50)
            # Ask to continue
            if get_user_input("\nContinue conversation? (y/n)", "y").lower() != 'y':
                print("\nClearing conversation history and exiting...")
                chat.clear_conversation()
                break
            print("\nContinuing conversation...\n")

if __name__ == "__main__":
    main()

# ---------------------------
# Documentation Updates:
# - README.md: Add section for 5x Multi-Search mode, usage, and accessibility notes.
# - CHANGELOG.md: Note addition of multi-search functionality and improved error handling.
# Accessibility Considerations:
# - All output is plain text, formatted for screen readers.
# - Results are sorted to match query order for easier navigation.
# - All available metadata and links are surfaced to the terminal for transparency.
# CORS/DOM: Not applicable (CLI only).
# Alternative Approach:
# - For richer output, consider integrating with a TUI library (e.g., rich) for color and tables.

def get_tool_schemas():
    """Get schemas for all perplexity search tools."""
    return [
        {
            "name": "Perplexity Search",
            "display_name": "Perplexity Search",
            "description": "Search the web using Perplexity to get comprehensive, up-to-date information.",
            "type": "function",
            "function": {
                "name": "perplexity_search",
                "display_name": "Perplexity Search",
                "description": "Search the web using Perplexity to get comprehensive, up-to-date information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to ask Perplexity."
                        },
                        "model": {
                            "type": "string",
                            "description": "Perplexity model to use (sonar, sonar-medium, etc).",
                            "default": "sonar"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "name": "Perplexity Multi-Search",
            "display_name": "Perplexity Multi-Search",
            "description": "Perform multiple adjacent web searches using Perplexity and return a summary.",
            "type": "function",
            "function": {
                "name": "perplexity_multi_search",
                "display_name": "Perplexity Multi-Search",
                "description": "Perform multiple adjacent web searches using Perplexity and return a summary.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The core search query to expand upon."
                        },
                        "model": {
                            "type": "string",
                            "description": "Perplexity model to use (sonar, sonar-medium, etc).",
                            "default": "sonar"
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