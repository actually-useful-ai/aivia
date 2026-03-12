#!/usr/bin/env python3
"""
X.AI Unified Tool
A comprehensive tool that integrates various X.AI API functionalities:
- Full-featured CLI chat interface with Grok models
- Generate alt text for images
- Perform specialized searches via Grok and dedicated modules
- Process ArXiv papers
- Handle multimodal inputs

This tool combines multiple functionalities from various scripts in a unified interface.
"""

import os
import sys
import json
import re
import time
import argparse
from datetime import datetime
from base64 import b64encode
from typing import Generator, List, Dict, Optional, Union, Tuple
import requests
import readline  # For command history support
import random
import textwrap

# Import OpenAI client for X.AI API
from openai import OpenAI

# Optional imports - will be used if available
try:
    from PIL import Image
    import io
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Try to import colorama for colored terminal output
try:
    from colorama import init, Fore, Style
    init()  # Initialize colorama
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    # Create dummy color constants
    class DummyFore:
        def __getattr__(self, name):
            return ""
    class DummyStyle:
        def __getattr__(self, name):
            return ""
    Fore = DummyFore()
    Style = DummyStyle()

# Import ArXiv processing module
try:
    import arXiv
except ImportError:
    print(f"{Fore.YELLOW}arXiv module not found. ArXiv functionality will be limited.{Style.RESET_ALL}", file=sys.stderr)

# Default API key - should be overridden via environment variable
DEFAULT_XAI_API_KEY = "REDACTED_XAI_KEY"

# File names for alt text generation
IMAGE_DATA_JS = "image-data.js"
UPDATED_IMAGE_DATA_JS = "image-data.updated.js"
BACKUP_IMAGE_DATA_JS = "image-data.backup.js"
CACHE_FILE = "generated_alts.json"

# Default model - using Grok-3 model with web search capabilities
DEFAULT_MODEL = "grok-3-beta"

class XAIUnified:
    """Unified class for X.AI API interactions."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the X.AI client with the provided API key.
        
        Args:
            api_key: The X.AI API key. If None, will use environment variable XAI_API_KEY
                    or fall back to the default key.
        """
        # Get API key from args, environment, or default
        self.api_key = api_key or os.getenv("XAI_API_KEY") or DEFAULT_XAI_API_KEY
        
        # Initialize OpenAI client for X.AI
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )
        
        # Initialize conversation with system prompt
        self.conversation_history = [
            {
                "role": "system",
                "content": "You are Grok, a helpful AI assistant with access to web search. You can help users with a wide range of tasks, provide information, and engage in conversation."
            }
        ]
        
        # Load alt text cache if exists
        self.alt_cache = self.load_cache()
        
        # Track if search was used in last response
        self.search_used = False
    
    # ---- Chat Functionality ----
    
    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.conversation_history = [self.conversation_history[0]]
    
    def set_system_prompt(self, prompt: str):
        """Update the system prompt for the conversation."""
        if self.conversation_history and self.conversation_history[0]["role"] == "system":
            self.conversation_history[0]["content"] = prompt
        else:
            self.conversation_history.insert(0, {"role": "system", "content": prompt})
    
    def list_models(self) -> List[Dict]:
        """
        Retrieve available X.AI models dynamically.
        
        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            # Fetch models from the X.AI API
            response = self.client.models.list()
            
            # Process and format the models
            models = []
            for model in response.data:
                # Extract capabilities from model metadata
                capabilities = []
                if "vision" in model.id or "image" in model.id:
                    capabilities.append("images")
                if "grok-3" in model.id:
                    capabilities.append("web-search")
                capabilities.extend(["text", "code"])  # All models support text and code
                
                models.append({
                    "id": model.id,
                    "name": model.id.replace("-", " ").title(),
                    "capabilities": capabilities,
                    "context_window": getattr(model, "context_window", 8192),  # Default if not specified
                    "created_at": datetime.fromtimestamp(model.created).strftime("%Y-%m-%d")
                })
            
            return sorted(models, key=lambda x: x["created_at"], reverse=True)
            
        except Exception as e:
            print(f"{Fore.RED}Error fetching models: {e}{Style.RESET_ALL}", file=sys.stderr)
            # Fallback to basic Grok models if API fails
            return [
                {
                    "id": "grok-3-mini-latest",
                    "name": "Grok 3 Mini Latest",
                    "capabilities": ["text", "code", "web-search"],
                    "context_window": 16384,
                    "created_at": "2024-08-01"
                },
                {
                    "id": "grok-2-vision-latest",
                    "name": "Grok 2 Vision Latest",
                    "capabilities": ["text", "code", "images"],
                    "context_window": 8192,
                    "created_at": "2024-02-01"
                }
            ]
    
    def process_tool_call(self, tool_call, model: str) -> str:
        """
        Process a tool call and return the result.
        
        Args:
            tool_call: The tool call object from the model
            model: The model ID being used
            
        Returns:
            The result of the tool call as a string
        """
        try:
            function_name = tool_call.function.name
            
            if function_name == "web_search":
                try:
                    args = json.loads(tool_call.function.arguments)
                    query = args.get("query", "")
                    
                    # First, try to use the direct Grok web search implementation
                    try:
                        # Import SearchWrapper - more reliable direct web search
                        from search_wrapper import SearchWrapper
                        
                        print(f"{Fore.YELLOW}Using direct Grok web search with SearchWrapper{Style.RESET_ALL}", file=sys.stderr)
                        search_wrapper = SearchWrapper(api_key=self.api_key)
                        result = search_wrapper.search(query)
                        
                        # Mark that search was used in this conversation
                        self.search_used = True
                        
                        # Add the search results to the conversation history as a system message
                        self.conversation_history.append({
                            "role": "system",
                            "content": f"The assistant searched the web for information about '{query}' and found the following information:\n\n{result}"
                        })
                        
                        return result
                    except ImportError:
                        print(f"{Fore.YELLOW}SearchWrapper not available, falling back to other methods{Style.RESET_ALL}", file=sys.stderr)
                        # If SearchWrapper is not available, continue to the multi-provider approach
                    except Exception as e:
                        print(f"{Fore.RED}Error using SearchWrapper: {str(e)}{Style.RESET_ALL}", file=sys.stderr)
                        # If there's an error with SearchWrapper, continue to the multi-provider approach
                    
                    # If we got here, try the multi-provider approach as a fallback
                    # Import all available search modules
                    search_results = []
                    error_messages = []
                    
                    # Track which search methods were successful
                    search_methods_used = []
                    
                    # 1. Try using WebSearchTools for unified search
                    try:
                        from search_providers.web_search_tools import WebSearchTools
                        search_tools = WebSearchTools(api_key=self.api_key)
                        
                        # Use "basic" strategy for faster results
                        result = search_tools.unified_search(query, strategy="basic")
                        
                        if result["status"] == "success":
                            search_response = search_tools.generate_combined_response(result)
                            search_results.append(search_response)
                            search_methods_used.append("WebSearchTools")
                    except Exception as e:
                        error_messages.append(f"WebSearchTools error: {str(e)}")
                    
                    # 2. Try using OpenAI WebSearch
                    try:
                        from search_providers.openai_websearch import OpenAIWebSearch
                        # Initialize with OpenAI API key
                        openai_websearch = OpenAIWebSearch(api_key=self.api_key)
                        
                        # Get the response without stream to avoid complexity
                        response = ""
                        for chunk in openai_websearch.stream_chat_with_web_search(
                            query, 
                            model="gpt-3.5-turbo",
                            use_web_search=True
                        ):
                            response += chunk
                        
                        if response and not response.startswith("Error:"):
                            search_results.append(response)
                            search_methods_used.append("OpenAI WebSearch")
                    except Exception as e:
                        error_messages.append(f"OpenAI WebSearch error: {str(e)}")
                    
                    # 3. Try using SearXNG Tools
                    try:
                        sys.path.append("gen/api-tools/tools")
                        from web_search import Tools as SearXNGTools
                        
                        searxng = SearXNGTools()
                        # Set the SearXNG URL if available
                        if os.environ.get("SEARXNG_URL"):
                            searxng.valves.SEARXNG_ENGINE_API_BASE_URL = os.environ.get("SEARXNG_URL")
                        
                        import asyncio
                        result = asyncio.run(searxng.search_web(query))
                        
                        # Parse the JSON result
                        result_data = json.loads(result)
                        if result_data and not isinstance(result_data, dict) or not result_data.get("error"):
                            formatted_result = "SearXNG Search Results:\n\n"
                            for item in result_data:
                                formatted_result += f"## {item.get('title', 'No Title')}\n"
                                formatted_result += f"URL: {item.get('url', 'No URL')}\n"
                                formatted_result += f"Summary: {item.get('snippet', 'No snippet available')}\n\n"
                            
                            search_results.append(formatted_result)
                            search_methods_used.append("SearXNG")
                    except Exception as e:
                        error_messages.append(f"SearXNG error: {str(e)}")
                    
                    # 4. Try using XAI Search as fallback
                    try:
                        from to_strip.xai_search import XaiWebSearcher
                        xai_searcher = XaiWebSearcher()
                        result = xai_searcher.search(query)
                        
                        if result and not result.get("error"):
                            import json
                            formatted_result = "XAI Search Results:\n\n" + json.dumps(result, indent=2)
                            search_results.append(formatted_result)
                            search_methods_used.append("XAI Search")
                    except Exception as e:
                        error_messages.append(f"XAI Search error: {str(e)}")
                    
                    # 5. Try using DuckDuckGo Search
                    try:
                        from search_providers.duckduckgo.duckduckgo_search import DuckDuckGoSearcher
                        ddg_searcher = DuckDuckGoSearcher()
                        result = ddg_searcher.search(query)
                        
                        if result and not result.get("error"):
                            # Format the results in a readable way
                            formatted_result = "DuckDuckGo Search Results:\n\n"
                            
                            # Add abstract if available
                            if result.get("abstract"):
                                formatted_result += f"## {result.get('abstract_source', 'Summary')}\n"
                                formatted_result += f"{result['abstract']}\n"
                                formatted_result += f"Source: {result['abstract_url']}\n\n"
                            
                            # Add search results
                            for i, item in enumerate(result.get("results", []), 1):
                                formatted_result += f"## {item.get('title', f'Result {i}')}\n"
                                formatted_result += f"{item.get('snippet', 'No description available')}\n"
                                formatted_result += f"URL: {item.get('url', 'No URL')}\n\n"
                            
                            search_results.append(formatted_result)
                            search_methods_used.append("DuckDuckGo")
                    except Exception as e:
                        error_messages.append(f"DuckDuckGo Search error: {str(e)}")
                    
                    # Combine results or return errors if all methods failed
                    if search_results:
                        # Mark that search was used in this conversation
                        self.search_used = True
                        
                        # Format the combined results with clear instructions for the assistant
                        combined_result = f"Search results for: {query}\n\n"
                        combined_result += f"Search providers used: {', '.join(search_methods_used)}\n\n"
                        combined_result += "\n\n---\n\n".join(search_results)
                        
                        # CRITICAL ADDITION: Add explicit instructions for how to use these results
                        # This gets added to the conversation history so the assistant knows to use this information
                        guidance = (
                            "\n\nUSE THE ABOVE SEARCH RESULTS to answer the user's query. "
                            "Base your response on the factual information provided in these search results. "
                            "If the search results don't contain sufficient information to answer completely, "
                            "acknowledge the limitations of the available information. "
                            "If search results contain conflicting information, acknowledge this and present multiple viewpoints. "
                            "DO NOT fabricate information beyond what's present in the search results. "
                            "Provide a clear, concise summary of the information relevant to the query."
                        )
                        
                        # Add the search results to the conversation history as a system message
                        # This is critical to ensure the model has context about the search results
                        self.conversation_history.append({
                            "role": "system",
                            "content": f"The assistant searched the web for information about '{query}' and found the following information:\n\n{combined_result}{guidance}"
                        })
                        
                        # Return the formatted results to display to the user
                        return combined_result
                    else:
                        # If all search methods failed, return the error messages
                        error_summary = "All search methods failed:\n\n" + "\n".join(error_messages)
                        return f"Search failed. {error_summary}. Try rephrasing your question."
                    
                except json.JSONDecodeError:
                    return "Error: Invalid JSON in web_search arguments."
                except Exception as e:
                    error_msg = f"Error during web search: {str(e)}"
                    print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}", file=sys.stderr)
                    return error_msg
                    
            elif function_name == "generate_image":
                try:
                    args = json.loads(tool_call.function.arguments)
                    prompt = args.get("prompt", "")
                    
                    if not prompt:
                        return "Error: No prompt provided for image generation."
                    
                    try:
                        print(f"{Fore.YELLOW}Generating image for prompt: {prompt}{Style.RESET_ALL}", file=sys.stderr)
                        
                        # Call X.AI's image generation API
                        response = self.client.images.generate(
                            model="grok-3-image-latest",
                            prompt=prompt,
                            n=1,
                            size="1024x1024"
                        )
                        
                        # Extract the image URL from the response
                        if response and response.data and len(response.data) > 0:
                            image_url = response.data[0].url
                            return f"Generated image: {image_url}"
                        else:
                            return "Image generation failed: No image data in response."
                    
                    except Exception as e:
                        error_msg = f"Error during image generation: {str(e)}"
                        print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}", file=sys.stderr)
                        return f"Image generation failed: {error_msg}"
                
                except json.JSONDecodeError:
                    return "Error: Invalid JSON in generate_image arguments."
                except Exception as e:
                    error_msg = f"Error processing image generation: {str(e)}"
                    print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}", file=sys.stderr)
                    return error_msg
            
            # Handle other tool types here
            return f"Unknown tool: {function_name}"
                
        except Exception as e:
            error_msg = f"Error processing tool call: {str(e)}"
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}", file=sys.stderr)
            return error_msg
    
    def continue_after_tool_call(self, model: str, temperature: float = 0.7) -> Generator[str, None, None]:
        """
        Continue the conversation after a tool call.
        
        Args:
            model: The model ID to use
            temperature: Controls randomness (0.0 to 1.0)
            
        Yields:
            Chunks of the response text as they arrive
        """
        try:
            # Create a new chat completion to continue the conversation
            response = self.client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                stream=True,
                temperature=temperature
            )
            
            response_text = ""
            
            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                    text = chunk.choices[0].delta.content
                    response_text += text
                    yield text
            
            # Add assistant's response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
        except Exception as e:
            error_msg = f"Error continuing conversation: {e}"
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}", file=sys.stderr)
            yield f"\n\n{Fore.RED}[ERROR: {error_msg}]{Style.RESET_ALL}"
    
    def stream_chat_response(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        image_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_search: bool = True
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from X.AI.
        
        Args:
            prompt: The user's input message
            model: The X.AI model to use
            image_url: Optional URL to an image (or data URI with base64 encoding)
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            use_search: Whether to enable web search (for Grok-3 models)
            
        Yields:
            Chunks of the response text as they arrive
        """
        # Reset search used flag
        self.search_used = False
        
        # Add image content if provided
        if image_url:
            # Check if model supports vision capabilities
            vision_supported = False
            
            # These models explicitly support vision
            if ("vision" in model.lower() or 
                "image" in model.lower() or 
                "grok-2-vision" in model.lower()):
                vision_supported = True
            
            # If current model doesn't support vision, switch to a vision model
            if not vision_supported:
                # Try to find a vision model from the list
                try:
                    models = self.list_models()
                    vision_models = [m for m in models if "images" in m.get("capabilities", [])]
                    if vision_models:
                        # Select the first vision-capable model
                        model = vision_models[0]["id"]
                        print(f"{Fore.YELLOW}Switching to vision model: {model}{Style.RESET_ALL}")
                    else:
                        # Fallback to a known vision model
                        model = "grok-2-vision-1212"
                        print(f"{Fore.YELLOW}Switching to vision model: {model}{Style.RESET_ALL}")
                except Exception as e:
                    # Fallback to a known vision model on error
                    model = "grok-2-vision-1212"
                    print(f"{Fore.YELLOW}Switching to vision model: {model}{Style.RESET_ALL}")
                    print(f"{Fore.RED}Error finding vision models: {e}{Style.RESET_ALL}")
            
            # Format the image correctly for the API
            message_content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                        "detail": "high"
                    }
                }
            ]
        else:
            message_content = prompt

        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message_content
        })

        try:
            # Create completion with streaming
            params = {
                "model": model,
                "messages": self.conversation_history,
                "stream": True,
                "temperature": temperature
            }
            
            # Define available tools based on model capabilities
            if "grok-3" in model and use_search:
                # Web search tool for Grok-3 models
                params["tools"] = [
                    {
                        "type": "function",
                        "function": {
                            "name": "web_search",
                            "description": "Search the web for relevant information",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "The search query to use"
                                    }
                                },
                                "required": ["query"]
                            }
                        }
                    }
                ]
                # Allow the model to choose when to use tools
                params["tool_choice"] = "auto"
            
            if max_tokens:
                params["max_tokens"] = max_tokens
                
            stream = self.client.chat.completions.create(**params)
            
            response_text = ""
            tool_calls = []
            current_tool_call = None
            
            for chunk in stream:
                delta = chunk.choices[0].delta
                
                # Check for tool calls
                if hasattr(delta, 'tool_calls') and delta.tool_calls:
                    tool_call = delta.tool_calls[0]
                    
                    # Initialize tool call tracking if this is a new tool call
                    if tool_call.index is not None and (current_tool_call is None or 
                                                       current_tool_call.index != tool_call.index):
                        if not self.search_used:
                            self.search_used = True
                            yield f"\n{Fore.CYAN}[Using tools...]{Style.RESET_ALL}\n"
                        
                        # Create a new tool call object
                        current_tool_call = type('obj', (object,), {
                            'id': getattr(tool_call, 'id', f"tool_{len(tool_calls)}"),
                            'index': getattr(tool_call, 'index', len(tool_calls)),
                            'type': 'function',
                            'function': type('obj', (object,), {
                                'name': '',
                                'arguments': ''
                            })
                        })
                        tool_calls.append(current_tool_call)
                    
                    # Update tool call information as it streams in
                    if hasattr(tool_call, 'function'):
                        if hasattr(tool_call.function, 'name') and tool_call.function.name:
                            current_tool_call.function.name = tool_call.function.name
                            
                        if hasattr(tool_call.function, 'arguments') and tool_call.function.arguments:
                            current_tool_call.function.arguments = (
                                current_tool_call.function.arguments + tool_call.function.arguments
                            )
                
                # Process regular content
                if hasattr(delta, 'content') and delta.content is not None:
                    text = delta.content
                    response_text += text
                    yield text
                
                # Check if the response is finished
                if chunk.choices[0].finish_reason is not None:
                    # If we have tool calls, process them
                    if tool_calls and chunk.choices[0].finish_reason == 'tool_calls':
                        # Add assistant's response with tool_calls to conversation history
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": response_text,
                            "tool_calls": [
                                {
                                    "id": tc.id,
                                    "type": "function",
                                    "function": {
                                        "name": tc.function.name,
                                        "arguments": tc.function.arguments
                                    }
                                } for tc in tool_calls
                            ]
                        })
                        
                        # Process each tool call
                        for tc in tool_calls:
                            result = self.process_tool_call(tc, model)
                            yield result
                        
                        # Continue the conversation with the tool results
                        yield f"\n{Fore.CYAN}[Continuing with tool results...]{Style.RESET_ALL}\n"
                        for chunk in self.continue_after_tool_call(model, temperature):
                            yield chunk
                        
                        return
            
            # Only add the assistant's response to conversation history if we didn't already do it for tool calls
            if not tool_calls:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response_text
                })
                    
        except Exception as e:
            error_msg = f"Error in stream_chat_response: {e}"
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}", file=sys.stderr)
            yield f"\n\n{Fore.RED}[ERROR: {error_msg}]{Style.RESET_ALL}"

    # ---- Image Handling ----
    
    def create_test_image(self, width: int = 100, height: int = 100, color: str = 'red') -> str:
        """
        Create a simple test image and return its base64 data URI.
        
        Args:
            width: Width of the test image
            height: Height of the test image
            color: Color of the test image
            
        Returns:
            Base64-encoded data URI for the image
        """
        if not HAS_PIL:
            print(f"{Fore.RED}PIL not available. Cannot create test image.{Style.RESET_ALL}", file=sys.stderr)
            return None
            
        # Create a colored square image
        img = Image.new('RGB', (width, height), color=color)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Return as data URI
        return f"data:image/png;base64,{b64encode(img_byte_arr).decode('utf-8')}"
    
    def load_image_from_url(self, url: str) -> str:
        """
        Download image from URL and return as base64-encoded data URI.
        
        Args:
            url: URL of the image to download
            
        Returns:
            Base64-encoded data URI for the image
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            image_data = response.content
            
            # Determine image type from content
            content_type = response.headers.get('content-type', 'image/jpeg')
            
            # Return as data URI
            return f"data:{content_type};base64,{b64encode(image_data).decode('utf-8')}"
        except Exception as e:
            print(f"{Fore.RED}Error loading image from URL: {e}{Style.RESET_ALL}", file=sys.stderr)
            return None
    
    # ---- Alt Text Generation ----
    
    def load_cache(self):
        """Load the generated alt texts cache if it exists."""
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as fp:
                return json.load(fp)
        return {}

    def save_cache(self):
        """Save the generated alt texts cache to file."""
        with open(CACHE_FILE, "w", encoding="utf-8") as fp:
            json.dump(self.alt_cache, fp, indent=4, ensure_ascii=False)

    def backup_file(self, src, backup):
        """Create a backup of the file if it does not already exist."""
        if not os.path.exists(backup):
            with open(src, "r", encoding="utf-8") as fin, open(backup, "w", encoding="utf-8") as fout:
                fout.write(fin.read())
            print(f"Backup created: {backup}")
        else:
            print(f"Backup already exists: {backup}")

    def extract_gallery_images(self, js_content):
        """
        Extract the galleryImages array from image-data.js.
        Assumes the file contains a line starting with "const galleryImages =" and ending with "];".
        """
        pattern = re.compile(r"const\s+galleryImages\s*=\s*(\[\s*{.*?}\s*\]);", re.DOTALL)
        match = pattern.search(js_content)
        if match:
            json_text = match.group(1)
            try:
                gallery = json.loads(json_text)
                return gallery
            except json.JSONDecodeError as e:
                print(f"{Fore.RED}Error parsing galleryImages JSON: {e}{Style.RESET_ALL}")
                raise
        else:
            raise RuntimeError("Could not extract galleryImages from image-data.js")

    def update_js_file(self, gallery_images, output_file):
        """
        Writes the updated galleryImages array to the specified output file.
        """
        with open(output_file, "w", encoding="utf-8") as fp:
            fp.write("const galleryImages = ")
            fp.write(json.dumps(gallery_images, indent=4, ensure_ascii=False))
            fp.write(";\n")
        print(f"Updated image data written to {output_file}")

    def generate_alt_text(self, image_url, prompt=None):
        """
        Generate alt text for an image using X.AI vision model.
        
        Args:
            image_url: URL of the image
            prompt: Custom prompt to use (optional)
            
        Returns:
            Generated alt text
        """
        if prompt is None:
            prompt = (
                "Write comprehensive alt text for this image, as though for a blind engineer who needs "
                "to understand every detail of the information including text. Write at maximum length. "
                "Do not include prepended or appended content like 'Alt Text', just respond with the description "
                "verbatim and nothing else."
            )
            
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                            "detail": "high"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
        
        try:
            completion = self.client.chat.completions.create(
                model="grok-2-vision-latest",
                messages=messages,
                temperature=0.01,
            )
            generated_text = completion.choices[0].message.content.strip()
            return generated_text
        except Exception as e:
            print(f"{Fore.RED}Error generating alt text for {image_url}: {e}{Style.RESET_ALL}")
            return None

    def process_gallery_images(self, input_file=IMAGE_DATA_JS, output_file=UPDATED_IMAGE_DATA_JS):
        """
        Process a gallery of images to generate alt text.
        
        Args:
            input_file: Path to the input image-data.js file
            output_file: Path to the output file
            
        Returns:
            Tuple of (total images, processed images, skipped images, error images)
        """
        # Back up the original file
        backup_file = f"{input_file}.backup.js"
        self.backup_file(input_file, backup_file)
        
        # Read and extract galleryImages from input file
        with open(input_file, "r", encoding="utf-8") as fp:
            js_content = fp.read()
            
        gallery_images = self.extract_gallery_images(js_content)
        print(f"Found {len(gallery_images)} images in {input_file}")
        
        # Process images
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        for idx, image in enumerate(gallery_images):
            image_id = image.get("id")
            if not image_id:
                print(f"Image at index {idx} is missing an 'id' field. Skipping.")
                skipped_count += 1
                continue
                
            print(f"\n[{idx+1}/{len(gallery_images)}] Processing image ID: {image_id}")
            
            # Check cache first
            if image_id in self.alt_cache:
                generated_text = self.alt_cache[image_id]
                print(f"[{image_id}] Using cached alt text.")
                processed_count += 1
            else:
                print(f"[{image_id}] Generating new alt text...")
                image_url = image.get("url")
                if not image_url:
                    print(f"[{image_id}] Missing URL. Skipping.")
                    skipped_count += 1
                    continue
                    
                generated_text = self.generate_alt_text(image_url)
                if not generated_text:
                    print(f"[{image_id}] Failed to generate alt text. Skipping update.")
                    error_count += 1
                    continue
                    
                # Save to cache
                self.alt_cache[image_id] = generated_text
                self.save_cache()
                processed_count += 1
                
                # Sleep briefly to avoid rate limits
                time.sleep(1)
                
            # Update the image object
            image["description"] = generated_text
            image["alt_text"] = generated_text
            print(f"[{image_id}] Updated description and alt_text fields.")
            
        # Write updated gallery
        self.update_js_file(gallery_images, output_file)
        
        return len(gallery_images), processed_count, skipped_count, error_count

    # ---- ArXiv Integration ----
    
    def process_arxiv_paper(self, paper_id: str, query: str = None) -> str:
        """
        Process an ArXiv paper and answer questions about it.
        
        Args:
            paper_id: ArXiv paper ID
            query: Optional specific question about the paper
            
        Returns:
            Response about the paper
        """
        try:
            # Construct ArXiv URL
            arxiv_url = f"https://arxiv.org/abs/{paper_id}"
            
            # Create system prompt
            system_prompt = (
                f"You are analyzing the ArXiv paper at {arxiv_url}. "
                "Provide a comprehensive analysis of the paper including key findings, "
                "methodology, and implications."
            )
            
            if query:
                prompt = f"Paper: {arxiv_url}\nQuestion: {query}"
            else:
                prompt = f"Summarize the key points of the ArXiv paper at {arxiv_url}"
                
            # Save current conversation
            old_conversation = self.conversation_history.copy()
            
            # Set up new conversation for this query
            self.conversation_history = [{"role": "system", "content": system_prompt}]
            
            # Get non-streaming response
            self.conversation_history.append({"role": "user", "content": prompt})
            
            # First create the completion request
            completion_request = {
                "model": "grok-3-mini-latest",  # Use Grok-3 for better research capabilities
                "messages": self.conversation_history,
                "temperature": 0.3,
                "tools": [{
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "description": "Search the web for relevant information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The search query to use"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                }],
                "tool_choice": "auto"
            }
            
            # Initial completion
            response = self.client.chat.completions.create(**completion_request)
            assistant_msg = response.choices[0].message
            
            # Add the assistant's message to the conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_msg.content or ""
            })
            
            # Check if the model used any tools
            if hasattr(assistant_msg, 'tool_calls') and assistant_msg.tool_calls:
                # Process each tool call
                for tool_call in assistant_msg.tool_calls:
                    try:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        if function_name == "web_search":
                            query = function_args.get("query", "")
                            # Simulate a web search result
                            search_result = f"Web search results for '{query}' about ArXiv paper {paper_id}"
                            
                            # Add the tool result to conversation
                            self.conversation_history.append({
                                "role": "tool",
                                "content": json.dumps({"results": search_result}),
                                "tool_call_id": tool_call.id
                            })
                    except Exception as e:
                        print(f"{Fore.RED}Error processing tool call: {e}{Style.RESET_ALL}")
                
                # Get a follow-up completion with tool results
                follow_up = self.client.chat.completions.create(
                    model="grok-3-mini-latest",
                    messages=self.conversation_history,
                    temperature=0.3
                )
                
                result = follow_up.choices[0].message.content
            else:
                # If no tools were used, just use the initial response
                result = assistant_msg.content
            
            # Restore previous conversation
            self.conversation_history = old_conversation
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing ArXiv paper: {e}"
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}", file=sys.stderr)
            return f"Error: {error_msg}"


# ---- CLI Helper Functions ----

def display_models(models: List[Dict]) -> None:
    """Display available models in a formatted way."""
    print(f"\n{Fore.GREEN}Available X.AI Models:{Style.RESET_ALL}")
    print("-" * 50)
    for idx, model in enumerate(models, 1):
        capabilities_text = ", ".join(model['capabilities'])
        if "web-search" in capabilities_text:
            capabilities_text = capabilities_text.replace("web-search", f"{Fore.CYAN}web-search{Style.RESET_ALL}")
        if "images" in capabilities_text:
            capabilities_text = capabilities_text.replace("images", f"{Fore.MAGENTA}images{Style.RESET_ALL}")
            
        print(f"{Fore.GREEN}{idx}.{Style.RESET_ALL} {Fore.YELLOW}{model['name']}{Style.RESET_ALL} ({model['id']})")
        print(f"   Capabilities: {capabilities_text}")
        print(f"   Context Window: {model['context_window']} tokens")
        print(f"   Released: {model['created_at']}")
        print()

def get_user_input(prompt: str, default: str = None) -> str:
    """Get user input with an optional default value."""
    if default:
        formatted_prompt = f"{Fore.CYAN}{prompt}{Style.RESET_ALL} [{default}]: "
    else:
        formatted_prompt = f"{Fore.CYAN}{prompt}{Style.RESET_ALL}: "
    
    response = input(formatted_prompt).strip()
    return response if response else default

def display_welcome_message():
    """Display a welcome message with ASCII art."""
    welcome_text = [
        f"{Fore.CYAN}╔═══════════════════════════════════════╗{Style.RESET_ALL}",
        f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.YELLOW}X.AI Unified CLI Tool{Style.RESET_ALL}                {Fore.CYAN}║{Style.RESET_ALL}",
        f"{Fore.CYAN}║{Style.RESET_ALL}  Chat with Grok models using CLI        {Fore.CYAN}║{Style.RESET_ALL}",
        f"{Fore.CYAN}║{Style.RESET_ALL}  Including web search and other tools   {Fore.CYAN}║{Style.RESET_ALL}",
        f"{Fore.CYAN}╚═══════════════════════════════════════╝{Style.RESET_ALL}",
    ]
    for line in welcome_text:
        print(line)
    print()

def display_help():
    """Display help information about available commands."""
    help_text = f"""
{Fore.GREEN}Available Commands:{Style.RESET_ALL}
  {Fore.YELLOW}/help{Style.RESET_ALL}           - Display this help message
  {Fore.YELLOW}/clear{Style.RESET_ALL}          - Clear the conversation history
  {Fore.YELLOW}/model <model_id>{Style.RESET_ALL} - Switch to a different model
  {Fore.YELLOW}/image <url>{Style.RESET_ALL}    - Include an image in your next prompt
  {Fore.YELLOW}/temp <value>{Style.RESET_ALL}   - Set temperature (0.0-1.0)
  {Fore.YELLOW}/search <on|off>{Style.RESET_ALL} - Enable or disable web search
  {Fore.YELLOW}/system <prompt>{Style.RESET_ALL} - Set a custom system prompt
  {Fore.YELLOW}/websearch <query>{Style.RESET_ALL} - Perform a direct web search
  {Fore.YELLOW}/websearch --ddg <query>{Style.RESET_ALL} - Search using DuckDuckGo
  {Fore.YELLOW}/exit{Style.RESET_ALL}           - Exit the chat

{Fore.GREEN}Examples:{Style.RESET_ALL}
  {Fore.YELLOW}/model grok-3-mini-latest{Style.RESET_ALL}
  {Fore.YELLOW}/temp 0.8{Style.RESET_ALL}
  {Fore.YELLOW}/image https://example.com/image.jpg{Style.RESET_ALL}
  {Fore.YELLOW}/websearch current AI developments{Style.RESET_ALL}
  {Fore.YELLOW}/websearch --duckduckgo latest news{Style.RESET_ALL}
    """
    print(textwrap.dedent(help_text))

def chat_interface(xai: XAIUnified, model: str, temperature: float = 0.7):
    """
    Run an interactive chat interface with Grok.
    
    Args:
        xai: XAIUnified instance
        model: Model ID to use
        temperature: Temperature for model responses
    """
    display_welcome_message()
    print(f"{Fore.GREEN}Chat initialized with model: {Style.RESET_ALL}{Fore.YELLOW}{model}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Type {Fore.YELLOW}/help{Fore.GREEN} for a list of available commands{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Type {Fore.YELLOW}/exit{Fore.GREEN} to end the conversation{Style.RESET_ALL}\n")
    
    image_url = None
    use_search = True
    
    while True:
        try:
            # Get user input
            user_input = input(f"{Fore.GREEN}You:{Style.RESET_ALL} ").strip()
            
            # Check for commands
            if user_input.startswith('/'):
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""
                
                if command == '/exit':
                    print(f"{Fore.YELLOW}Exiting chat. Goodbye!{Style.RESET_ALL}")
                    break
                    
                elif command == '/help':
                    display_help()
                    continue
                    
                elif command == '/clear':
                    xai.clear_conversation()
                    print(f"{Fore.YELLOW}Conversation history cleared.{Style.RESET_ALL}")
                    continue
                    
                elif command == '/model':
                    if arg:
                        model = arg
                        print(f"{Fore.YELLOW}Switched to model: {model}{Style.RESET_ALL}")
                    else:
                        # List available models
                        models = xai.list_models()
                        display_models(models)
                        
                        try:
                            selection = int(get_user_input("Select a model number", "1")) - 1
                            if 0 <= selection < len(models):
                                model = models[selection]["id"]
                                print(f"{Fore.YELLOW}Switched to model: {model}{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.RED}Invalid selection. Staying with current model.{Style.RESET_ALL}")
                        except ValueError:
                            print(f"{Fore.RED}Invalid input. Staying with current model.{Style.RESET_ALL}")
                    continue
                    
                elif command == '/image':
                    if arg:
                        # Check if it's a URL or a local file
                        if os.path.isfile(arg) and HAS_PIL:
                            try:
                                with open(arg, "rb") as img_file:
                                    image_data = img_file.read()
                                    content_type = "image/jpeg"  # Assuming JPEG
                                    image_url = f"data:{content_type};base64,{b64encode(image_data).decode('utf-8')}"
                                    print(f"{Fore.YELLOW}Image loaded from file: {arg}{Style.RESET_ALL}")
                            except Exception as e:
                                print(f"{Fore.RED}Error loading image file: {e}{Style.RESET_ALL}")
                                image_url = None
                        else:
                            # Assume it's a URL
                            image_url = arg
                            print(f"{Fore.YELLOW}Image URL set: {image_url}{Style.RESET_ALL}")
                    else:
                        # No URL provided, create a test image
                        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
                        image_url = xai.create_test_image(color=random.choice(colors))
                        print(f"{Fore.YELLOW}Created test image{Style.RESET_ALL}")
                        
                    continue
                    
                elif command == '/temp':
                    try:
                        temp = float(arg)
                        if 0.0 <= temp <= 1.0:
                            temperature = temp
                            print(f"{Fore.YELLOW}Temperature set to: {temperature}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED}Temperature must be between 0.0 and 1.0.{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.RED}Invalid temperature value.{Style.RESET_ALL}")
                    continue
                    
                elif command == '/search':
                    if arg.lower() in ('on', 'true', 'yes', '1'):
                        use_search = True
                        print(f"{Fore.YELLOW}Web search enabled.{Style.RESET_ALL}")
                    elif arg.lower() in ('off', 'false', 'no', '0'):
                        use_search = False
                        print(f"{Fore.YELLOW}Web search disabled.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Invalid option. Use '/search on' or '/search off'.{Style.RESET_ALL}")
                    continue
                    
                elif command == '/system':
                    if arg:
                        xai.set_system_prompt(arg)
                        print(f"{Fore.YELLOW}System prompt updated.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Please provide a system prompt.{Style.RESET_ALL}")
                    continue
                
                elif command == '/websearch':
                    if arg:
                        try:
                            # Check if a provider is specified
                            provider = None
                            provider_arg_match = re.match(r'^--([a-zA-Z0-9_-]+)\s+(.+)$', arg)
                            
                            if provider_arg_match:
                                provider = provider_arg_match.group(1).lower()
                                query = provider_arg_match.group(2)
                            else:
                                query = arg
                                
                            print(f"{Fore.YELLOW}Searching the web for: {query}{Style.RESET_ALL}")
                            if provider:
                                print(f"{Fore.YELLOW}Using provider: {provider}{Style.RESET_ALL}")
                            
                            # Use DuckDuckGo if specified
                            if provider == "duckduckgo" or provider == "ddg":
                                try:
                                    from search_providers.duckduckgo.duckduckgo_search import DuckDuckGoSearcher
                                    ddg_searcher = DuckDuckGoSearcher()
                                    result = ddg_searcher.search(query)
                                    
                                    if result and not result.get("error"):
                                        # Format the results in a readable way
                                        formatted_result = "DuckDuckGo Search Results:\n\n"
                                        
                                        # Add abstract if available
                                        if result.get("abstract"):
                                            formatted_result += f"## {result.get('abstract_source', 'Summary')}\n"
                                            formatted_result += f"{result['abstract']}\n"
                                            formatted_result += f"Source: {result['abstract_url']}\n\n"
                                        
                                        # Add search results
                                        for i, item in enumerate(result.get("results", []), 1):
                                            formatted_result += f"## {item.get('title', f'Result {i}')}\n"
                                            formatted_result += f"{item.get('snippet', 'No description available')}\n"
                                            formatted_result += f"URL: {item.get('url', 'No URL')}\n\n"
                                        
                                        print(f"\n{Fore.CYAN}Search Results:{Style.RESET_ALL}")
                                        print(formatted_result)
                                        
                                        # Mark that search was used in this conversation
                                        xai.search_used = True
                                        
                                        # Add guidance for how to use the search results
                                        guidance = (
                                            "\n\nUSE THE ABOVE SEARCH RESULTS to answer the user's query. "
                                            "Base your response on the factual information provided in these search results. "
                                            "If the search results don't contain sufficient information to answer completely, "
                                            "acknowledge the limitations of the available information. "
                                            "If search results contain conflicting information, acknowledge this and present multiple viewpoints. "
                                            "DO NOT fabricate information beyond what's present in the search results. "
                                            "Provide a clear, concise summary of the information relevant to the query."
                                        )
                                        
                                        xai.conversation_history.append({
                                            "role": "system",
                                            "content": f"Web search results for '{query}':\n\n{formatted_result}{guidance}"
                                        })
                                        
                                        print(f"{Fore.GREEN}Search results added to conversation context with summarization guidance.{Style.RESET_ALL}")
                                    else:
                                        error_msg = result.get("error", "No results found")
                                        print(f"{Fore.RED}DuckDuckGo search failed: {error_msg}{Style.RESET_ALL}")
                                except Exception as e:
                                    print(f"{Fore.RED}Error using DuckDuckGo search: {e}{Style.RESET_ALL}")
                                    print(f"{Fore.YELLOW}Falling back to default search methods.{Style.RESET_ALL}")
                                    provider = None  # Fall back to default methods
                            
                            # If no provider specified or fallback needed, use WebSearchTools or built-in search
                            if not provider:
                                # Try to import the WebSearchTools class
                                try:
                                    from search_providers.web_search_tools import WebSearchTools
                                    search_tools = WebSearchTools(api_key=xai.api_key, verbose=True)
                                    
                                    # Perform the search
                                    results = search_tools.unified_search(query)
                                    
                                    # Check if search was successful
                                    if results["status"] == "success" and "grok" in results["results"]:
                                        grok_results = results["results"]["grok"]
                                        if grok_results["status"] == "success":
                                            summary = search_tools.get_search_summary(results)
                                            print(f"\n{Fore.CYAN}Search Results:{Style.RESET_ALL}")
                                            print(summary)
                                            
                                            # Mark that search was used in this conversation
                                            xai.search_used = True
                                            
                                            # Add guidance for how to use the search results
                                            guidance = (
                                                "\n\nUSE THE ABOVE SEARCH RESULTS to answer the user's query. "
                                                "Base your response on the factual information provided in these search results. "
                                                "If the search results don't contain sufficient information to answer completely, "
                                                "acknowledge the limitations of the available information. "
                                                "If search results contain conflicting information, acknowledge this and present multiple viewpoints. "
                                                "DO NOT fabricate information beyond what's present in the search results. "
                                                "Provide a clear, concise summary of the information relevant to the query."
                                            )
                                            
                                            xai.conversation_history.append({
                                                "role": "system",
                                                "content": f"Web search results for '{query}':\n\n{grok_results['results']}{guidance}"
                                            })
                                            
                                            print(f"{Fore.GREEN}Search results added to conversation context with summarization guidance.{Style.RESET_ALL}")
                                        else:
                                            print(f"{Fore.RED}Search failed: {grok_results.get('message', 'Unknown error')}{Style.RESET_ALL}")
                                    else:
                                        print(f"{Fore.RED}Search failed: {results.get('message', 'No results found')}{Style.RESET_ALL}")
                                    
                                except ImportError:
                                    print(f"{Fore.RED}Web search tools not available. Using built-in search.{Style.RESET_ALL}")
                                    
                                    # Create a tool call object
                                    tool_call = type('obj', (object,), {
                                        'id': f"manual_search_{int(time.time())}",
                                        'function': type('obj', (object,), {
                                            'name': 'web_search',
                                            'arguments': json.dumps({"query": query})
                                        })
                                    })
                                    
                                    # Process the tool call
                                    result = xai.process_tool_call(tool_call, model)
                                    print(result)
                                    print(f"{Fore.GREEN}Search results added to conversation context.{Style.RESET_ALL}")
                                except Exception as e:
                                    print(f"{Fore.RED}Error performing web search: {e}{Style.RESET_ALL}")
                                    print(f"{Fore.YELLOW}Try asking your question directly to the model instead.{Style.RESET_ALL}")
                            else:
                                # Add the search results to conversation history as a system message with explicit guidance
                                guidance = (
                                    "\n\nUSE THE ABOVE SEARCH RESULTS to answer the user's query. "
                                    "Base your response on the factual information provided in these search results. "
                                    "If the search results don't contain sufficient information to answer completely, "
                                    "acknowledge the limitations of the available information. "
                                    "If search results contain conflicting information, acknowledge this and present multiple viewpoints. "
                                    "DO NOT fabricate information beyond what's present in the search results. "
                                    "Provide a clear, concise summary of the information relevant to the query."
                                )
                                
                                xai.conversation_history.append({
                                    "role": "system",
                                    "content": f"Web search results for '{query}':\n\n{grok_results['results']}{guidance}"
                                })
                                
                                print(f"{Fore.GREEN}Search results added to conversation context with summarization guidance.{Style.RESET_ALL}")
                        except Exception as e:
                            print(f"{Fore.RED}Error performing web search: {e}{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}Try asking your question directly to the model instead.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Please provide a search query.{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}Usage: /websearch your search query{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}       /websearch --duckduckgo your search query{Style.RESET_ALL}")
                    continue
                    
                else:
                    print(f"{Fore.RED}Unknown command: {command}. Type /help for available commands.{Style.RESET_ALL}")
                    continue
            
            # Skip empty inputs
            if not user_input:
                continue
                
            # Process normal user input
            print(f"\n{Fore.BLUE}Grok:{Style.RESET_ALL} ", end="", flush=True)
            
            # Stream the response
            for chunk in xai.stream_chat_response(
                prompt=user_input, 
                model=model, 
                image_url=image_url,
                temperature=temperature,
                use_search=use_search
            ):
                print(chunk, end="", flush=True)
            
            # Reset image URL after use
            if image_url:
                print(f"\n{Fore.YELLOW}Image processed. Image context cleared for next message.{Style.RESET_ALL}")
                image_url = None
                
            print("\n")
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Interrupted. Type /exit to quit or continue chatting.{Style.RESET_ALL}")
            continue
        except EOFError:
            print(f"\n{Fore.YELLOW}Input stream ended. Exiting chat.{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Continuing chat. Type /exit to quit.{Style.RESET_ALL}")
            continue

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="X.AI Unified Tool")
    
    # Main mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--chat", action="store_true", help="Chat with Grok")
    mode_group.add_argument("--alt-text", action="store_true", help="Generate alt text for images")
    mode_group.add_argument("--arxiv", action="store_true", help="Process ArXiv papers")
    
    # General options
    parser.add_argument("--api-key", help="X.AI API key (overrides environment variable)")
    
    # Chat options
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Specific model to use")
    parser.add_argument("--system-prompt", help="Custom system prompt")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature (0.0-1.0)")
    parser.add_argument("--image", help="Image URL or file path for vision queries")
    parser.add_argument("--no-search", action="store_true", help="Disable web search capability")
    
    # Alt text options
    parser.add_argument("--input-file", default=IMAGE_DATA_JS, help="Input image data JS file")
    parser.add_argument("--output-file", default=UPDATED_IMAGE_DATA_JS, help="Output image data JS file")
    
    # ArXiv options
    parser.add_argument("--paper-id", help="ArXiv paper ID")
    parser.add_argument("--query", help="Specific question about the paper")
    
    args = parser.parse_args()
    
    # Create X.AI client
    xai = XAIUnified(api_key=args.api_key)
    
    # Set system prompt if provided
    if args.system_prompt:
        xai.set_system_prompt(args.system_prompt)
    
    # Determine which mode to run
    if args.alt_text:
        # Alt text generation mode
        print(f"Generating alt text for images in {args.input_file}")
        total, processed, skipped, errors = xai.process_gallery_images(
            input_file=args.input_file,
            output_file=args.output_file
        )
        print("\n======= Processing Complete =======")
        print(f"Total images: {total}")
        print(f"Successfully processed: {processed}")
        print(f"Skipped: {skipped}")
        print(f"Errors: {errors}")
        
    elif args.arxiv:
        # ArXiv processing mode
        if not args.paper_id:
            print("Error: --paper-id is required for ArXiv mode")
            sys.exit(1)
            
        print(f"Processing ArXiv paper: {args.paper_id}")
        result = xai.process_arxiv_paper(args.paper_id, args.query)
        print("\n" + "-" * 50)
        print(result)
        print("-" * 50)
        
    else:
        # Chat mode - now using the enhanced interactive interface
        chat_interface(xai, args.model, args.temperature)

if __name__ == "__main__":
    main() 