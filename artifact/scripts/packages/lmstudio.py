"""
LM Studio API Chat Implementation
This module provides a simple interface to the LM Studio API for chat, text completion, and embeddings.
Supports streaming responses and multiple model types.
"""

import requests
import sys
import json
import os
import base64
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
from PIL import Image
import io

class LMStudioChat:
    def __init__(self, base_url: str = "https://api.assisted.space/v1"):
        """Initialize the LM Studio client with the base API URL."""
        self.base_url = base_url.rstrip('/')  # Keep /v1 in the endpoint calls
        self.chat_history = [{
            "role": "system", 
            "content": "You are a helpful AI assistant."
        }]

    def list_models(
        self,
        sort_by: str = "id",
        reverse: bool = False,
        page: int = 1,
        page_size: int = 5,
        capability_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch available models from LM Studio API with pagination and filtering.
        
        Args:
            sort_by (str): Field to sort by ('id', 'type', 'capabilities')
            reverse (bool): Whether to reverse sort order
            page (int): Page number (1-based)
            page_size (int): Number of items per page
            capability_filter (Optional[str]): Filter models by capability ('chat', 'function', 'vision')
            
        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            response = requests.get(f"{self.base_url}/models")
            response.raise_for_status()
            
            # Process and enhance model data
            models = []
            for model_data in response.json()["data"]:
                # Extract model ID and capabilities
                model_id = model_data["id"]
                
                # Determine model capabilities
                capabilities = ["chat"]  # All models support chat
                
                # Infer additional capabilities from model properties and ID
                if "vision" in model_id.lower():
                    capabilities.append("vision")
                if any(x in model_id.lower() for x in ["function", "tool"]):
                    capabilities.append("function")
                if "embedding" in model_id.lower():
                    capabilities.append("embeddings")
                if any(x in model_id.lower() for x in ["llama", "mistral", "mixtral", "completion"]):
                    capabilities.append("completion")
                
                # Skip if doesn't match capability filter
                if capability_filter and capability_filter not in capabilities:
                    continue
                
                # Determine model type
                model_type = "chat"
                if "embedding" in model_id.lower():
                    model_type = "embedding"
                elif any(x in model_id.lower() for x in ["llama", "mistral", "mixtral"]):
                    model_type = "llm"
                
                models.append({
                    "id": model_id,
                    "name": model_data.get("name", model_id).replace("-", " ").title(),
                    "type": model_type,
                    "capabilities": capabilities,
                    "capability_count": len(capabilities),
                    "created": model_data.get("created", datetime.now().timestamp()),
                    "owned_by": model_data.get("owned_by", "local")
                })
            
            # Sort models
            if sort_by == "type":
                models.sort(key=lambda x: x["type"], reverse=reverse)
            elif sort_by == "capabilities":
                models.sort(key=lambda x: x["capability_count"], reverse=reverse)
            else:  # sort by id
                models.sort(key=lambda x: x["id"], reverse=reverse)
            
            # Calculate pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            return models[start_idx:end_idx]
            
        except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            return []

    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific model.
        
        Args:
            model_id (str): The ID of the model to query
            
        Returns:
            Optional[Dict]: Model details if found, None otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/models/{model_id}")
            response.raise_for_status()
            
            model_data = response.json()
            capabilities = ["chat"]  # Base capability
            
            # Infer additional capabilities
            if "vision" in model_id.lower():
                capabilities.append("vision")
            if any(x in model_id.lower() for x in ["function", "tool"]):
                capabilities.append("function")
            if "embedding" in model_id.lower():
                capabilities.append("embeddings")
            if any(x in model_id.lower() for x in ["llama", "mistral", "mixtral", "completion"]):
                capabilities.append("completion")
            
            # Determine model type
            model_type = "chat"
            if "embedding" in model_id.lower():
                model_type = "embedding"
            elif any(x in model_id.lower() for x in ["llama", "mistral", "mixtral"]):
                model_type = "llm"
            
            return {
                "id": model_id,
                "name": model_data.get("name", model_id).replace("-", " ").title(),
                "type": model_type,
                "capabilities": capabilities,
                "created": model_data.get("created", datetime.now().timestamp()),
                "owned_by": model_data.get("owned_by", "local")
            }
        except Exception as e:
            print(f"Error fetching model info: {e}", file=sys.stderr)
            return None

    def stream_chat_response(
        self,
        message: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = -1,
        image_data: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from LM Studio. Supports optional image data.
        
        For vision-capable models, if image_data is provided the image is sent as a separate
        parameter with its base64 encoding prefixed (e.g., "data:image/png;base64,").
        Otherwise, the image is included using the standard message formatting.
        
        Args:
            message (str): The user's input message.
            model (str): The model to use.
            temperature (float): Response temperature (0.0 to 1.0).
            max_tokens (int): Maximum tokens in response (-1 for no limit).
            image_data (Optional[str]): Base64 encoded image data (without the data URL prefix).
            
        Yields:
            str: Chunks of the response text as they arrive.
        """
        try:
            # Check if the model is vision-capable by looking for keywords in its id/name.
            if image_data and any(keyword in model.lower() for keyword in ['vision', 'image', 'multimodal']):
                # For vision models, attach the image as a separate key.
                self.chat_history.append({
                    "role": "user",
                    "content": message
                })
                payload = {
                    "model": model,
                    "messages": self.chat_history,
                    "image": f"data:image/png;base64,{image_data}",
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True
                }
            else:
                # For non-vision models or when no image data is provided,
                # include the image (if any) as part of the message.
                content = self.format_message_with_image(message, image_data)
                self.chat_history.append({
                    "role": "user",
                    "content": content
                })
                payload = {
                    "model": model,
                    "messages": self.chat_history,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True
                }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                stream=True
            )
            response.raise_for_status()

            full_response = ""
            buffer = ""

            for line in response.iter_lines():
                if not line:
                    continue

                buffer += line.decode('utf-8') + "\n"
                if buffer.strip() == "data: [DONE]":
                    break

                if "data: " in buffer:
                    chunks = buffer.split("data: ")
                    buffer = chunks[-1]  # retain the last incomplete chunk

                    for chunk in chunks[:-1]:
                        chunk = chunk.strip()
                        if not chunk or chunk == "[DONE]":
                            continue

                        try:
                            data = json.loads(chunk)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content_chunk = delta["content"]
                                    full_response += content_chunk
                                    yield content_chunk
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON: {e}", file=sys.stderr)
                            continue

            if full_response:
                self.chat_history.append({
                    "role": "assistant",
                    "content": full_response
                })

        except Exception as e:
            print(f"Error in stream_chat_response: {e}", file=sys.stderr)
            if self.chat_history:
                self.chat_history.pop()  # Remove the latest user message on error
            yield f"Error: {str(e)}"

    def text_completion(
        self,
        prompt: str,
        model: str = "pixtral-12b",
        temperature: float = 0.7,
        max_tokens: int = 10,
        stop: Optional[str] = "\n",
        file_path: Optional[str] = None
    ) -> str:
        """
        Generate a text completion. Supports optional file attachments (e.g., images).
        
        Args:
            prompt (str): The input prompt
            model (str): The model to use
            temperature (float): Response temperature (0.0 to 1.0)
            max_tokens (int): Maximum tokens in response
            stop (Optional[str]): Stop sequence
            file_path (Optional[str]): Path to a file (e.g., an image) to attach
            
        Returns:
            str: The generated completion
        """
        try:
            # Prepare the prompt content
            content = prompt
            if file_path and os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    base64_data = base64.b64encode(file_data).decode('utf-8')
                    content = [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{os.path.splitext(file_path)[1][1:]};base64,{base64_data}"
                            }
                        }
                    ]

            response = requests.post(
                f"{self.base_url}/v1/completions",
                json={
                    "model": model,
                    "prompt": content,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False,
                    "stop": stop
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["text"]
        except Exception as e:
            print(f"Error in text_completion: {e}", file=sys.stderr)
            return str(e)

    def get_embeddings(
        self,
        text: str,
        model: str = "text-embedding-nomic-embed-text-v1.5"
    ) -> List[float]:
        """
        Generate embeddings for input text.
        
        Args:
            text (str): The input text to embed
            model (str): The embedding model to use
            
        Returns:
            List[float]: The generated embedding vector
        """
        try:
            response = requests.post(
                f"{self.base_url}/v1/embeddings",
                json={
                    "model": model,
                    "input": text
                }
            )
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]
        except Exception as e:
            print(f"Error in get_embeddings: {e}", file=sys.stderr)
            return []

    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant."
        }]

    def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> str:
        """
        Create a test image and return its base64 encoding.
        
        Args:
            color (str): Color of the test image
            size (tuple): Size of the image in pixels (width, height)
            
        Returns:
            str: Base64 encoded image data
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

    def load_image_from_file(self, file_path: str) -> Optional[str]:
        """
        Load an image from a file and return its base64 encoding.
        
        Args:
            file_path (str): Path to the image file
            
        Returns:
            Optional[str]: Base64 encoded image data or None if loading fails
        """
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                # Resize if too large (max 2048x2048)
                if img.size[0] > 2048 or img.size[1] > 2048:
                    img.thumbnail((2048, 2048))
                # Save to bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                return base64.b64encode(img_byte_arr).decode('utf-8')
        except Exception as e:
            print(f"Error loading image: {e}", file=sys.stderr)
            return None

    def format_message_with_image(
        self,
        message: str,
        image_data: Optional[str] = None
    ) -> Union[str, List[Dict]]:
        """Format a message with optional image data for the API."""
        if not image_data:
            return message
        
        return [
            {
                "type": "text",
                "text": message
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_data}"
                }
            }
        ]

def display_models(
    models: List[Dict],
    current_page: int,
    total_pages: int,
    sort_by: str,
    capability_filter: Optional[str] = None
) -> None:
    """Display available models in a formatted way."""
    print(f"\nAvailable LM Studio Models (Page {current_page}/{total_pages}):")
    print(f"Sorting by: {sort_by}")
    if capability_filter:
        print(f"Filtering by capability: {capability_filter}")
    print("-" * 50)
    
    for idx, model in enumerate(models, 1):
        print(f"{idx}. {model['name']}")
        print(f"   Model: {model['id']}")
        print(f"   Type: {model['type']}")
        print(f"   Capabilities: {', '.join(model['capabilities'])}")
        print(f"   Owner: {model.get('owned_by', 'local')}")
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
    chat = LMStudioChat()
    
    # Model browsing loop
    page = 1
    page_size = 5
    sort_by = "id"
    capability_filter = None
    
    # Get initial full list of models
    all_models = chat.list_models(
        sort_by=sort_by,
        page=1,
        page_size=1000,
        capability_filter=capability_filter
    )
    total_pages = (len(all_models) + page_size - 1) // page_size if all_models else 0
    
    if not all_models:
        print("Error: No models available. Please check if the API endpoint is accessible.")
        sys.exit(1)
    
    while True:
        # Get current page of models
        models = chat.list_models(
            sort_by=sort_by,
            page=page,
            page_size=page_size,
            capability_filter=capability_filter
        )
        
        # Display models
        display_models(models, page, total_pages, sort_by, capability_filter)
        
        # Show options
        print("\nOptions:")
        print("1. Select model")
        print("2. Next page")
        print("3. Previous page")
        print("4. Sort by (id/type/capabilities)")
        print("5. Filter by capability (chat/function/vision/completion/embeddings/none)")
        print("6. Change page size")
        print("7. Quit")
        
        choice = get_user_input("Select option", "1")
        
        if choice == "1":
            # Select model
            try:
                selection = int(get_user_input("Select a model number", "1")) - 1
                if 0 <= selection < len(models):
                    selected_model = models[selection]["id"]
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
                "Sort by (id/type/capabilities)",
                "id"
            )
            # Refresh model list with new sorting
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1  # Reset to first page
        elif choice == "5":
            # Filter by capability
            cap_choice = get_user_input(
                "Filter by capability (chat/function/vision/completion/embeddings/none)",
                "none"
            ).lower()
            capability_filter = None if cap_choice == "none" else cap_choice
            # Refresh model list with new filter
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1  # Reset to first page
        elif choice == "6":
            # Change page size
            try:
                new_size = int(get_user_input("Enter page size", str(page_size)))
                if new_size > 0:
                    page_size = new_size
                    total_pages = (len(all_models) + page_size - 1) // page_size
                    page = 1  # Reset to first page
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "7":
            print("Exiting...")
            sys.exit(0)
        
        print()  # Add spacing between iterations
    
    # Start conversation loop
    while True:
        # Check if model supports images
        supports_images = any(x in selected_model.lower() for x in ["vision", "image", "multimodal"])
        
        # Always show image options, with warning for non-vision models
        print("\nImage options:")
        if not supports_images:
            print("[Note: Selected model does not support image understanding]")
        print("1. No image")
        print("2. Test image (colored square)")
        print("3. Load image from file")
        
        image_choice = get_user_input("Select image option", "1")
        test_image = None
        
        if image_choice == "2":
            # Create test image with custom color
            color = get_user_input("Enter color (e.g., red, blue, green)", "red")
            size_str = get_user_input("Enter size (width,height)", "100,100")
            try:
                width, height = map(int, size_str.split(","))
                test_image = chat.create_test_image(color=color, size=(width, height))
            except ValueError:
                print("Invalid size format. Using default 100x100...")
                test_image = chat.create_test_image(color=color)
        elif image_choice == "3":
            # Load image from file
            file_path = get_user_input("Enter image file path")
            test_image = chat.load_image_from_file(file_path)
            if not test_image:
                print("Failed to load image. Continuing without image...")
        
        # Get message
        default_prompt = "What do you see in this image?" if test_image else "Tell me about yourself"
        message = get_user_input(
            "Enter your message",
            default_prompt
        )
        
        # Stream response
        print("\nStreaming response:")
        print("-" * 50)
        for chunk in chat.stream_chat_response(message, selected_model, image_data=test_image):
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