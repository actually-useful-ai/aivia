"""
OpenAI Chat Implementation
This module provides a simple interface to the OpenAI API for streaming chat responses.
Supports model selection, multi-turn conversations, and image analysis with streaming responses.
"""

from openai import OpenAI
import sys
import base64
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
from PIL import Image
import io
import os

class OpenAIChat:
    # Default models in case API fetch fails
    DEFAULT_MODELS = {
        "gpt-4-vision-preview": {
            "id": "gpt-4-vision-preview",
            "context_length": 128000,
            "description": "GPT-4 Turbo with image understanding",
            "capabilities": ["text", "vision", "function"],
            "capability_count": 3,
            "created": datetime.fromtimestamp(0),
            "created_str": "1970-01-01",
            "generation": "4",
            "version": "preview",
            "owned_by": "openai"
        },
        "gpt-4-0125-preview": {
            "id": "gpt-4-0125-preview",
            "context_length": 128000,
            "description": "Most capable GPT-4 model",
            "capabilities": ["text", "function"],
            "capability_count": 2,
            "created": datetime.fromtimestamp(0),
            "created_str": "1970-01-01",
            "generation": "4",
            "version": "0125-preview",
            "owned_by": "openai"
        },
        "gpt-4": {
            "id": "gpt-4",
            "context_length": 8192,
            "description": "More capable GPT-4 model",
            "capabilities": ["text", "function"],
            "capability_count": 2,
            "created": datetime.fromtimestamp(0),
            "created_str": "1970-01-01",
            "generation": "4",
            "version": None,
            "owned_by": "openai"
        },
        "gpt-3.5-turbo-0125": {
            "id": "gpt-3.5-turbo-0125",
            "context_length": 16385,
            "description": "Most capable GPT-3.5 model",
            "capabilities": ["text", "function"],
            "capability_count": 2,
            "created": datetime.fromtimestamp(0),
            "created_str": "1970-01-01",
            "generation": "3.5",
            "version": "0125",
            "owned_by": "openai"
        }
    }

    def __init__(self, api_key: str):
        """Initialize the OpenAI client with the provided API key."""
        if not hasattr(OpenAI, '_patched_no_proxies'):
            original_init = OpenAI.__init__
            def patched_init(self, api_key: str, **kwargs):
                kwargs.pop('proxies', None)
                original_init(self, api_key=api_key, **kwargs)
            OpenAI.__init__ = patched_init
            OpenAI._patched_no_proxies = True

        self.client = OpenAI(api_key=api_key)
        self.models = self._fetch_models()
        # Initialize with system message
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on providing accurate and detailed responses."
        }]
    
    def _fetch_models(self) -> Dict:
        """
        Fetch available models from OpenAI API.
        
        Returns:
            Dict: Dictionary of available models with their details
        """
        try:
            models = {}
            response = self.client.models.list()
            
            # Filter for chat models and organize them
            for model in response.data:
                model_id = model.id
                created = datetime.fromtimestamp(model.created)
                
                # Filter for chat-capable models
                if any(x in model_id.lower() for x in ["gpt-4", "gpt-3.5", "gpt-3"]):
                    capabilities = ["text"]
                    
                    # Determine capabilities
                    if "vision" in model_id.lower():
                        capabilities.append("vision")
                    if not any(x in model_id.lower() for x in ["instruct", "base"]):
                        capabilities.append("function")  # Most chat models support function calling
                    
                    # Determine context length
                    context_length = 8192  # Default
                    if "32k" in model_id:
                        context_length = 32768
                    elif "16k" in model_id:
                        context_length = 16385
                    elif "128k" in model_id or "vision" in model_id:
                        context_length = 128000
                    
                    # Create model description
                    description = f"OpenAI {model_id} model"
                    if "4" in model_id:
                        description = "Most capable GPT-4 model"
                    elif "3.5" in model_id:
                        description = "Efficient GPT-3.5 model"
                    if "vision" in model_id:
                        description += " with image understanding"
                    
                    # Determine model generation and version
                    generation = "4" if "4" in model_id else "3.5" if "3.5" in model_id else "3"
                    version = "preview" if "preview" in model_id else model_id.split('-')[-1] if '-' in model_id else None
                    
                    models[model_id] = {
                        "id": model_id,
                        "context_length": context_length,
                        "description": description,
                        "capabilities": capabilities,
                        "capability_count": len(capabilities),
                        "created": created,
                        "created_str": created.strftime("%Y-%m-%d"),
                        "generation": generation,
                        "version": version,
                        "owned_by": model.owned_by
                    }
            
            return models if models else self.DEFAULT_MODELS
            
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
        """
        Get available OpenAI models with sorting and pagination.
        
        Args:
            sort_by (str): Field to sort by ('created', 'context_length', 'id', 'capabilities')
            reverse (bool): Whether to reverse sort order
            page (int): Page number (1-based)
            page_size (int): Number of items per page
            generation (Optional[str]): Filter by model generation ('4', '3.5', '3')
            
        Returns:
            List[Dict]: List of available models with their details
        """
        # Convert models to list and optionally filter by generation
        models_list = [
            {
                "id": info["id"],
                "name": model_id,
                "context_length": info["context_length"],
                "description": info["description"],
                "capabilities": info["capabilities"],
                "capability_count": info["capability_count"],
                "created": info["created"],
                "created_str": info["created_str"],
                "generation": info["generation"],
                "version": info["version"],
                "owned_by": info["owned_by"]
            }
            for model_id, info in self.models.items()
            if not generation or info["generation"] == generation
        ]
        
        # Sort models
        if sort_by == "created":
            models_list.sort(key=lambda x: x["created"], reverse=reverse)
        elif sort_by == "context_length":
            models_list.sort(key=lambda x: x["context_length"], reverse=reverse)
        elif sort_by == "capabilities":
            # Sort by number of capabilities first, then by specific capabilities
            models_list.sort(key=lambda x: (
                x["capability_count"],
                "images" in x["capabilities"],
                "text" in x["capabilities"]
            ), reverse=reverse)
        else:  # sort by id
            models_list.sort(key=lambda x: x["id"], reverse=reverse)
        
        # Calculate pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return models_list[start_idx:end_idx]

    def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Optional[str]: Base64 encoded image data or None if encoding fails
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}", file=sys.stderr)
            return None

    def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> Optional[str]:
        """
        Create a test image and return its base64 encoding.
        
        Args:
            color (str): Color of the test image
            size (tuple): Size of the image in pixels (width, height)
            
        Returns:
            Optional[str]: Base64 encoded image data or None if creation fails
        """
        try:
            img = Image.new('RGB', size, color=color)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            return base64.b64encode(img_byte_arr).decode('utf-8')
        except Exception as e:
            print(f"Error creating test image: {e}", file=sys.stderr)
            return None

    def create_test_file(self, content: str = None) -> str:
        """
        Create a test text file and return its base64 encoding.
        
        Args:
            content (str): Optional content for the test file
            
        Returns:
            str: Base64 encoded file content
        """
        if not content:
            content = "This is a test file.\nIt contains multiple lines.\nHello, GPT!"
        return base64.b64encode(content.encode('utf-8')).decode('utf-8')

    def encode_file(self, file_path: str) -> Optional[str]:
        """
        Encode a file to base64.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            Optional[str]: Base64 encoded file data or None if encoding fails
        """
        try:
            with open(file_path, "rb") as file:
                return base64.b64encode(file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding file: {e}", file=sys.stderr)
            return None

    def format_message_with_image(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
        """Format a message with optional image data for the API."""
        if not image_data:
            return message
        
        # Convert single image to list
        if isinstance(image_data, str):
            image_data = [image_data]
        
        content = [{"type": "text", "text": message}]
        
        for img in image_data:
            if is_url:
                content.append({
                    "type": "image_url",
                    "image_url": img
                })
            else:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img}"
                    }
                })
        
        return content

    def format_message_with_attachments(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        file_data: Optional[str] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
        """Format a message with optional image and file data for the API."""
        if not image_data and not file_data:
            return message
        
        content = [{"type": "text", "text": message}]
        
        # Add images
        if image_data:
            # Convert single image to list
            if isinstance(image_data, str):
                image_data = [image_data]
            
            for img in image_data:
                if is_url:
                    content.append({
                        "type": "image_url",
                        "image_url": img
                    })
                else:
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img}"
                        }
                    })
        
        # Add file if provided
        if file_data:
            content.append({
                "type": "text",
                "text": f"\nFile content:\n{base64.b64decode(file_data).decode('utf-8', errors='ignore')}"
            })
        
        return content

    def stream_chat_response(
        self,
        message: str,
        model: str = "gpt-3.5-turbo-0125",
        temperature: float = 0.7,
        image_data: Optional[Union[str, List[str]]] = None,
        file_data: Optional[str] = None,
        is_url: bool = False
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from OpenAI.
        
        Args:
            message (str): The user's input message
            model (str): The OpenAI model to use
            temperature (float): Response temperature (0.0 to 1.0)
            image_data (Optional[Union[str, List[str]]]): Image URL(s) or base64 data
            file_data (Optional[str]): Base64 encoded file data
            is_url (bool): Whether image_data contains URLs
            
        Yields:
            str: Chunks of the response text as they arrive
        """
        try:
            # Format message content based on whether we have attachments
            content = self.format_message_with_attachments(message, image_data, file_data, is_url)
            
            # Add user message to history
            self.chat_history.append({
                "role": "user",
                "content": content
            })
            
            # Create messages list for API
            messages = []
            for msg in self.chat_history:
                if isinstance(msg["content"], list):
                    # This is a message with attachments, keep as is
                    messages.append(msg)
                else:
                    # Text-only message
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Get model ID from our models dict
            model_id = self.models[model]["id"] if model in self.models else model
            
            stream = self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_response += text
                    yield text
            
            # Add assistant's response to history
            self.chat_history.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            print(f"Error in stream_chat_response: {e}", file=sys.stderr)
            # Remove the user message if request failed
            if self.chat_history:
                self.chat_history.pop()
            yield f"Error: {str(e)}"

    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on providing accurate and detailed responses."
        }]

def display_models(
    models: List[Dict],
    current_page: int,
    total_pages: int,
    sort_by: str,
    generation: Optional[str] = None
) -> None:
    """Display available models in a formatted way."""
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
    """Get user input with an optional default value."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    response = input(prompt).strip()
    return response if response else default

def main():
    """Main CLI interface."""
    # Initialize with API key
    api_key = "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"
    
    chat = OpenAIChat(api_key)
    
    # Model browsing loop
    page = 1
    page_size = 5
    sort_by = "created"
    generation = None
    capability_filter = None
    
    while True:
        # Get total number of models for pagination
        all_models = chat.list_models(sort_by=sort_by, page=1, page_size=1000, generation=generation)
        
        # Apply capability filter if set
        if capability_filter:
            all_models = [
                model for model in all_models 
                if capability_filter in model["capabilities"]
            ]
        
        total_pages = (len(all_models) + page_size - 1) // page_size
        
        # Get current page of models
        models = chat.list_models(
            sort_by=sort_by,
            page=page,
            page_size=page_size,
            generation=generation
        )
        
        # Apply capability filter if set
        if capability_filter:
            models = [
                model for model in models 
                if capability_filter in model["capabilities"]
            ]
        
        # Display models
        display_models(models, page, total_pages, sort_by, generation)
        
        # Show options
        print("\nOptions:")
        print("1. Select model")
        print("2. Next page")
        print("3. Previous page")
        print("4. Sort by (created/context_length/id/capabilities)")
        print("5. Filter by generation (4/3.5/3/none)")
        print("6. Filter by capability (text/function/vision/none)")
        print("7. Change page size")
        print("8. Quit")
        
        choice = get_user_input("Select option", "1")
        
        if choice == "1":
            # Select model
            try:
                selection = int(get_user_input("Select a model number", "1")) - 1
                if 0 <= selection < len(models):
                    selected_model = models[selection]["name"]
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "2":
            # Next page
            if page < total_pages:
                page += 1
        elif choice == "3":
            # Previous page
            if page > 1:
                page -= 1
        elif choice == "4":
            # Sort by
            sort_by = get_user_input(
                "Sort by (created/context_length/id/capabilities)",
                "created"
            )
            page = 1  # Reset to first page
        elif choice == "5":
            # Filter by generation
            gen = get_user_input(
                "Filter by generation (4/3.5/3/none)",
                "none"
            )
            generation = None if gen.lower() == "none" else gen
            page = 1  # Reset to first page
        elif choice == "6":
            # Filter by capability
            cap_choice = get_user_input(
                "Filter by capability (text/function/vision/none)",
                "none"
            ).lower()
            capability_filter = None if cap_choice == "none" else cap_choice
            page = 1  # Reset to first page
        elif choice == "7":
            # Change page size
            try:
                new_size = int(get_user_input("Enter page size", str(page_size)))
                if new_size > 0:
                    page_size = new_size
                    page = 1  # Reset to first page
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "8":
            print("Exiting...")
            sys.exit(0)
        
        print()  # Add spacing between iterations
    
    # Start conversation loop
    while True:
        # Check if model supports images
        supports_images = "vision" in chat.models[selected_model]["capabilities"]
        
        # Always show input options
        print("\nInput options:")
        if not supports_images:
            print("[Note: Selected model does not support image understanding]")
        
        print("\nAttachment options:")
        print("1. Text only")
        print("2. Test image (colored square)")
        print("3. Load image from file")
        print("4. Image from URL")
        print("5. Test file (sample text)")
        print("6. Load file from disk")
        
        input_choice = get_user_input("Select input option", "1")
        image_data = None
        file_data = None
        is_url = False
        
        if input_choice == "2" and supports_images:
            # Create test image with custom color
            color = get_user_input("Enter color (e.g., red, blue, green)", "red")
            size_str = get_user_input("Enter size (width,height)", "100,100")
            try:
                width, height = map(int, size_str.split(","))
                image_data = chat.create_test_image(color=color, size=(width, height))
                if not image_data:
                    print("Failed to create test image. Continuing without image...")
            except ValueError:
                print("Invalid size format. Using default 100x100...")
                image_data = chat.create_test_image(color=color)
        elif input_choice == "3" and supports_images:
            # Load image from file
            file_path = get_user_input("Enter image file path")
            image_data = chat.encode_image(file_path)
            if not image_data:
                print("Failed to load image. Continuing without image...")
        elif input_choice == "4" and supports_images:
            # Use image URL
            url = get_user_input("Enter image URL")
            if url:
                image_data = url
                is_url = True
        elif input_choice == "5":
            # Create test file
            content = get_user_input("Enter file content (or press Enter for default)")
            file_data = chat.create_test_file(content if content else None)
        elif input_choice == "6":
            # Load file from disk
            file_path = get_user_input("Enter file path")
            file_data = chat.encode_file(file_path)
            if not file_data:
                print("Failed to load file. Continuing without file...")
        
        # Get message
        default_prompt = "What do you see in this image?" if image_data else "Please analyze this file" if file_data else "Hello! How can I help you today?"
        message = get_user_input(
            "Enter your message",
            default_prompt
        )
        
        # Stream response
        print("\nStreaming response:")
        print("-" * 50)
        for chunk in chat.stream_chat_response(
            message,
            selected_model,
            image_data=image_data,
            file_data=file_data,
            is_url=is_url
        ):
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