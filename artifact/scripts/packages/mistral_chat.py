"""
Mistral API Chat Implementation
This module provides a simple interface to the Mistral AI API for streaming chat responses.
Supports model selection, multi-turn conversations, and image analysis with streaming responses.
"""

import os
import sys
import requests
import json
import base64
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
from PIL import Image
import io

class MistralChat:
    def __init__(self, api_key: str):
        """Initialize the Mistral client with the provided API key."""
        self.api_key = api_key
        self.api_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Initialize with system message
        self.conversation_history = [{
            "role": "system", 
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]

    def list_models(
        self,
        sort_by: str = "created",
        reverse: bool = True,
        page: int = 1,
        page_size: int = 5,
        capability_filter: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve available Mistral models with pagination.
        
        Args:
            sort_by (str): Field to sort by ('created', 'id', 'context_length')
            reverse (bool): Whether to reverse sort order
            page (int): Page number (1-based)
            page_size (int): Number of items per page
            capability_filter (Optional[str]): Filter models by capability ('chat', 'function', 'vision')
            category_filter (Optional[str]): Filter models by category ('mistral', 'mixtral', 'pixtral')
            
        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            response = requests.get(
                f"{self.api_url}/models",
                headers=self.headers
            )
            response.raise_for_status()
            
            models = []
            for model in response.json()["data"]:
                # Extract model capabilities
                capabilities = []
                if model["capabilities"]["completion_chat"]:
                    capabilities.append("chat")
                if model["capabilities"]["function_calling"]:
                    capabilities.append("function")
                if model["capabilities"].get("vision"):  # Add vision capability check
                    capabilities.append("vision")
                
                # Determine model category
                model_id = model["id"].lower()
                if "mixtral" in model_id:
                    category = "mixtral"
                elif "pixtral" in model_id:
                    category = "pixtral"
                else:
                    category = "mistral"
                
                # Skip if doesn't match filters
                if capability_filter and capability_filter not in capabilities:
                    continue
                if category_filter and category_filter != category:
                    continue
                
                models.append({
                    "id": model["id"],
                    "name": model["name"] or model["id"].replace("-", " ").title(),
                    "description": model["description"] or f"Mistral {model['id']} model",
                    "context_length": model["max_context_length"],
                    "created_at": datetime.fromtimestamp(model["created"]).strftime("%Y-%m-%d"),
                    "created": model["created"],
                    "capabilities": capabilities,
                    "category": category,
                    "owned_by": model["owned_by"],
                    "deprecated_at": model.get("deprecation")
                })
            
            # Sort models
            if sort_by == "created":
                models.sort(key=lambda x: x["created"], reverse=reverse)
            elif sort_by == "context_length":
                models.sort(key=lambda x: x["context_length"], reverse=reverse)
            else:  # sort by id
                models.sort(key=lambda x: x["id"], reverse=reverse)
            
            # Calculate pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            return models[start_idx:end_idx]
            
        except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            # Fallback to known models if API fails
            fallback_models = [{
                "id": "mistral-tiny",
                "name": "Mistral Tiny",
                "description": "Fast and efficient model for simple tasks",
                "context_length": 32768,
                "created_at": "2024-03-01",
                "created": datetime.now().timestamp(),
                "capabilities": ["chat"],
                "category": "mistral",
                "owned_by": "mistralai"
            }, {
                "id": "mistral-small",
                "name": "Mistral Small",
                "description": "Balanced model for general use",
                "context_length": 32768,
                "created_at": "2024-03-01",
                "created": datetime.now().timestamp(),
                "capabilities": ["chat", "functions"],
                "category": "mistral",
                "owned_by": "mistralai"
            }, {
                "id": "mistral-medium",
                "name": "Mistral Medium",
                "description": "More capable model for complex tasks",
                "context_length": 32768,
                "created_at": "2024-03-01",
                "created": datetime.now().timestamp(),
                "capabilities": ["chat", "functions"],
                "category": "mistral",
                "owned_by": "mistralai"
            }]
            
            # Apply filters to fallback models
            if capability_filter:
                fallback_models = [
                    model for model in fallback_models 
                    if capability_filter in model["capabilities"]
                ]
            if category_filter:
                fallback_models = [
                    model for model in fallback_models
                    if category_filter == model["category"]
                ]
            
            # Apply pagination to fallback models
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return fallback_models[start_idx:end_idx]

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

    def load_image_from_file(self, file_path: str) -> Optional[str]:
        """
        Load an image from a file and return its base64 encoding.
        Supports PNG, JPEG, WEBP, and single-frame GIF formats.
        
        Args:
            file_path (str): Path to the image file
            
        Returns:
            Optional[str]: Base64 encoded image data or None if loading fails
        """
        try:
            with Image.open(file_path) as img:
                # Check file format
                if img.format not in ['PNG', 'JPEG', 'WEBP', 'GIF']:
                    print(f"Unsupported image format: {img.format}. Must be PNG, JPEG, WEBP, or single-frame GIF.", 
                          file=sys.stderr)
                    return None
                
                # Check if GIF is animated
                if img.format == 'GIF' and getattr(img, 'is_animated', False):
                    print("Animated GIFs are not supported.", file=sys.stderr)
                    return None
                
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Check file size (max 10MB)
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format)
                if img_byte_arr.tell() > 10 * 1024 * 1024:  # 10MB in bytes
                    print("Image file size exceeds 10MB limit.", file=sys.stderr)
                    return None
                
                # Resize if dimensions are too large (max 1024x1024)
                if img.size[0] > 1024 or img.size[1] > 1024:
                    # Calculate new dimensions maintaining aspect ratio
                    ratio = min(1024/img.size[0], 1024/img.size[1])
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Convert to base64
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format)
                img_byte_arr = img_byte_arr.getvalue()
                return base64.b64encode(img_byte_arr).decode('utf-8')
                
        except Exception as e:
            print(f"Error loading image: {e}", file=sys.stderr)
            return None

    def format_message_with_image(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
        """
        Format a message with optional image data for the API.
        
        Args:
            message (str): The text message
            image_data (Optional[Union[str, List[str]]]): Image URL(s) or base64 data
            is_url (bool): Whether image_data contains URLs
            
        Returns:
            Union[str, List[Dict]]: Formatted message for the API
        """
        if not image_data:
            return message
        
        # Convert single image to list
        if isinstance(image_data, str):
            image_data = [image_data]
        
        # Limit to 8 images per request
        if len(image_data) > 8:
            print("Warning: Maximum 8 images per request. Using first 8 images.", file=sys.stderr)
            image_data = image_data[:8]
        
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
                    "image_url": f"data:image/jpeg;base64,{img}"
                })
        
        return content

    def format_message_with_file(
        self,
        message: str,
        file_data: Optional[Union[str, List[str]]] = None
    ) -> Union[str, List[Dict]]:
        """
        Format a message with optional file data for the API.

        Args:
            message (str): The text message
            file_data (Optional[Union[str, List[str]]]): File ID(s) from Mistral API

        Returns:
            Union[str, List[Dict]]: Formatted message for the API
        """
        if not file_data:
            return message

        # Convert single file ID to list
        if isinstance(file_data, str):
            file_data = [file_data]

        content = [{"type": "text", "text": message}]
        
        for file_id in file_data:
            content.append({
                "type": "file",
                "file_id": file_id
            })
        
        return content

    def stream_chat_response(
        self,
        message: str,
        model: str = "mistral-tiny",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        safe_prompt: bool = True,
        image_data: Optional[Union[str, List[str]]] = None,
        is_url: bool = False,
        file_data: Optional[Union[str, List[str]]] = None
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from Mistral.
        
        Args:
            message (str): The user's input message
            model (str): The Mistral model to use
            temperature (float): Response temperature (0.0 to 1.5)
            max_tokens (Optional[int]): Maximum tokens to generate
            top_p (float): Nucleus sampling parameter (0.0 to 1.0)
            safe_prompt (bool): Whether to use safety prompts
            image_data (Optional[Union[str, List[str]]]): Image URL(s) or base64 data
            is_url (bool): Whether image_data contains URLs
            file_data (Optional[Union[str, List[str]]]): File ID(s) from Mistral API
            
        Yields:
            str: Chunks of the response text as they arrive
        """
        # Format message content based on whether we have images or files
        content = message
        if image_data:
            content = self.format_message_with_image(message, image_data, is_url)
        elif file_data:
            content = self.format_message_with_file(message, file_data)
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": content
        })

        payload = {
            "model": model,
            "messages": self.conversation_history,
            "stream": True,
            "temperature": temperature,
            "top_p": top_p,
            "safe_prompt": safe_prompt
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=self.headers,
                json=payload,
                stream=True
            )
            response.raise_for_status()
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith("data: "):
                        line_text = line_text[6:]  # Remove "data: " prefix
                    if line_text == "[DONE]":
                        continue
                        
                    try:
                        data = json.loads(line_text)
                        content = data['choices'][0]['delta'].get('content', '')
                        if content:
                            full_response += content
                            yield content
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error processing chunk: {e}", file=sys.stderr)
                        continue

            # Add assistant's response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            self.conversation_history.pop()  # Remove the user message if request failed
            yield f"Error: {str(e)}"
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            self.conversation_history.pop()
            yield f"Error: {str(e)}"

    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.conversation_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]

    def upload_file(self, file_path: str) -> Optional[str]:
        """
        Upload a file to Mistral's servers and return the file ID.

        Args:
            file_path (str): Path to the file to upload
        
        Returns:
            Optional[str]: File ID if successful, None otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                upload_headers = {"Authorization": f"Bearer {self.api_key}"}
                response = requests.post(f"{self.api_url}/files", headers=upload_headers, files=files)
                response.raise_for_status()
                return response.json().get("id")
        except Exception as e:
            print(f"Error uploading file: {e}", file=sys.stderr)
            return None

    def list_files(self, purpose: Optional[str] = None) -> List[Dict]:
        """
        List files uploaded to Mistral.
        
        Args:
            purpose (Optional[str]): Filter by purpose ('fine-tune', 'assistants')
            
        Returns:
            List[Dict]: List of file metadata
        """
        try:
            params = {"purpose": purpose} if purpose else {}
            response = requests.get(
                f"{self.api_url}/files",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            print(f"Error listing files: {e}", file=sys.stderr)
            return []

    def retrieve_file(self, file_id: str) -> Dict:
        """
        Retrieve metadata for a specific file.
        
        Args:
            file_id (str): ID of the file to retrieve
            
        Returns:
            Dict: File metadata
        """
        try:
            response = requests.get(
                f"{self.api_url}/files/{file_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error retrieving file: {e}", file=sys.stderr)
            return None

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file.
        
        Args:
            file_id (str): ID of the file to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            response = requests.delete(
                f"{self.api_url}/files/{file_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}", file=sys.stderr)
            return False

    def get_file_content(self, file_id: str) -> Optional[bytes]:
        """
        Download a file's content.
        
        Args:
            file_id (str): ID of the file to download
            
        Returns:
            Optional[bytes]: File content or None if download fails
        """
        try:
            response = requests.get(
                f"{self.api_url}/files/{file_id}/content",
                headers=self.headers
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading file: {e}", file=sys.stderr)
            return None

    def get_file_url(self, file_id: str) -> Optional[str]:
        """
        Get a temporary URL to download a file.
        
        Args:
            file_id (str): ID of the file
            
        Returns:
            Optional[str]: Temporary download URL or None if failed
        """
        try:
            response = requests.post(
                f"{self.api_url}/files/{file_id}/download_url",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()["download_url"]
        except Exception as e:
            print(f"Error getting file URL: {e}", file=sys.stderr)
            return None

def display_models(
    models: List[Dict],
    current_page: int,
    total_pages: int,
    sort_by: str,
    category_filter: Optional[str] = None,
    capability_filter: Optional[str] = None
) -> None:
    """Display available models in a formatted way."""
    print(f"\nAvailable Mistral Models (Page {current_page}/{total_pages}):")
    print(f"Sorting by: {sort_by}")
    if category_filter:
        print(f"Category: {category_filter}")
    if capability_filter:
        print(f"Capability: {capability_filter}")
    print("-" * 50)
    
    # Group models by category
    models_by_category = {}
    for model in models:
        category = model["category"]
        if category not in models_by_category:
            models_by_category[category] = []
        models_by_category[category].append(model)
    
    # Display models by category
    idx = 1
    for category in sorted(models_by_category.keys()):
        if not category_filter:  # Only show category header if not filtered
            print(f"\n{category.upper()} MODELS:")
        for model in models_by_category[category]:
            print(f"{idx}. {model['name']}")
            print(f"   Model: {model['id']}")
            print(f"   Description: {model['description']}")
            print(f"   Context Length: {model['context_length']} tokens")
            print(f"   Capabilities: {', '.join(model['capabilities'])}")
            print(f"   Released: {model['created_at']}")
            if model.get("deprecated_at"):
                print(f"   Deprecated: {model['deprecated_at']}")
            print(f"   Owner: {model['owned_by']}")
            print()
            idx += 1

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
    api_key = os.getenv("MISTRAL_API_KEY") or "n8R347515VqP48oDHwBeL9BS6nW1L8zY"
    
    if not api_key:
        print("Error: MISTRAL_API_KEY environment variable not set")
        sys.exit(1)
    
    chat = MistralChat(api_key)
    
    # Model browsing loop
    page = 1
    page_size = 5
    sort_by = "created"
    category_filter = None
    capability_filter = None
    
    # Get initial full list of models
    all_models = chat.list_models(
        sort_by=sort_by,
        page=1,
        page_size=1000,
        category_filter=category_filter,
        capability_filter=capability_filter
    )
    total_pages = (len(all_models) + page_size - 1) // page_size
    
    while True:
        # Get current page of models
        models = chat.list_models(
            sort_by=sort_by,
            page=page,
            page_size=page_size,
            category_filter=category_filter,
            capability_filter=capability_filter
        )
        
        # Display models
        display_models(models, page, total_pages, sort_by, category_filter, capability_filter)
        
        # Show options
        print("\nOptions:")
        print("1. Select model")
        print("2. Next page")
        print("3. Previous page")
        print("4. Sort by (created/context_length/id)")
        print("5. Filter by category (mistral/mixtral/pixtral/none)")
        print("6. Filter by capability (chat/function/vision/none)")
        print("7. Change page size")
        print("8. File Management")
        print("9. Quit")
        
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
                "Sort by (created/context_length/id)",
                "created"
            )
            # Refresh model list with new sorting
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                category_filter=category_filter,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1  # Reset to first page
        elif choice == "5":
            # Filter by category
            cat_choice = get_user_input(
                "Filter by category (mistral/mixtral/pixtral/none)",
                "none"
            ).lower()
            category_filter = None if cat_choice == "none" else cat_choice
            # Refresh model list with new filter
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                category_filter=category_filter,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1  # Reset to first page
        elif choice == "6":
            # Filter by capability
            cap_choice = get_user_input(
                "Filter by capability (chat/function/vision/none)",
                "none"
            ).lower()
            capability_filter = None if cap_choice == "none" else cap_choice
            # Refresh model list with new filter
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                category_filter=category_filter,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1  # Reset to first page
        elif choice == "7":
            # Change page size
            try:
                new_size = int(get_user_input("Enter page size", str(page_size)))
                if new_size > 0:
                    page_size = new_size
                    total_pages = (len(all_models) + page_size - 1) // page_size
                    page = 1  # Reset to first page
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "8":
            # File Management Menu
            while True:
                print("\nFile Management:")
                print("1. Upload File")
                print("2. List Files")
                print("3. Download File")
                print("4. Delete File")
                print("5. Get File URL")
                print("6. Back to Main Menu")
                
                file_choice = get_user_input("Select option", "1")
                
                if file_choice == "1":
                    file_path = get_user_input("Enter file path")
                    if os.path.exists(file_path):
                        result = chat.upload_file(file_path)
                        if result:
                            print(f"File uploaded successfully. ID: {result}")
                    else:
                        print("File not found.")
                
                elif file_choice == "2":
                    purpose = get_user_input("Filter by purpose (fine-tune/assistants/none)", "none")
                    purpose = None if purpose.lower() == "none" else purpose
                    files = chat.list_files(purpose)
                    if files:
                        print("\nAvailable Files:")
                        for file in files:
                            print(f"ID: {file['id']}")
                            print(f"Name: {file['filename']}")
                            print(f"Size: {file['bytes']} bytes")
                            print(f"Created: {file['created_at']}")
                            print("-" * 30)
                    else:
                        print("No files found.")
                
                elif file_choice == "3":
                    file_id = get_user_input("Enter file ID")
                    content = chat.get_file_content(file_id)
                    if content:
                        save_path = get_user_input("Enter save path")
                        try:
                            with open(save_path, 'wb') as f:
                                f.write(content)
                            print(f"File saved to {save_path}")
                        except Exception as e:
                            print(f"Error saving file: {e}")
                
                elif file_choice == "4":
                    file_id = get_user_input("Enter file ID")
                    if chat.delete_file(file_id):
                        print("File deleted successfully.")
                    else:
                        print("Failed to delete file.")
                
                elif file_choice == "5":
                    file_id = get_user_input("Enter file ID")
                    url = chat.get_file_url(file_id)
                    if url:
                        print(f"Temporary download URL: {url}")
                    else:
                        print("Failed to get file URL.")
                
                elif file_choice == "6":
                    break
                
                print()  # Add spacing between operations
        
        elif choice == "9":
            print("Exiting...")
            sys.exit(0)
        
        print()  # Add spacing between iterations
    
    # Start conversation loop
    while True:
        # Check if model supports images
        supports_images = "vision" in models[selection]["capabilities"]
        
        # Only show image options for vision models
        if supports_images:
            print("\nImage options:")
            print("1. No image")
            print("2. Test image (colored square)")
            print("3. Load image from file")
            print("4. Image from URL")
            print("5. Test image via File API")
            
            image_choice = get_user_input("Select image option", "1")
            image_data = None
            is_url = False
            
            if image_choice == "2":
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
            elif image_choice == "3":
                # Load image from file
                file_path = get_user_input("Enter image file path")
                image_data = chat.load_image_from_file(file_path)
                if not image_data:
                    print("Failed to load image. Continuing without image...")
            elif image_choice == "4":
                # Use image URL
                url = get_user_input("Enter image URL")
                if url:
                    image_data = url
                    is_url = True
            elif image_choice == "5":
                # Create and upload test image through File API
                print("\nCreating test image...")
                color = get_user_input("Enter color (e.g., red, blue, green)", "red")
                size_str = get_user_input("Enter size (width,height)", "100,100")
                try:
                    width, height = map(int, size_str.split(","))
                    test_image_data = chat.create_test_image(color=color, size=(width, height))
                    if test_image_data:
                        # Save temporary image file
                        temp_path = f"temp_test_image_{color}.png"
                        try:
                            with open(temp_path, 'wb') as f:
                                f.write(base64.b64decode(test_image_data))
                            
                            # Upload to Mistral
                            print("Uploading image to Mistral...")
                            result = chat.upload_file(temp_path)
                            if result:
                                print(f"Image uploaded successfully. ID: {result}")
                                
                                # Get file URL
                                url = chat.get_file_url(result)
                                if url:
                                    print("Retrieved file URL for chat.")
                                    image_data = url
                                    is_url = True
                                else:
                                    print("Failed to get file URL. Continuing without image...")
                        
                            # Clean up temporary file
                            os.remove(temp_path)
                            
                        except Exception as e:
                            print(f"Error in file API flow: {e}")
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                    else:
                        print("Failed to create test image. Continuing without image...")
                except ValueError:
                    print("Invalid size format. Continuing without image...")
        else:
            image_data = None
            is_url = False
        
        # Get message
        default_prompt = "What do you see in this image?" if image_data else "Tell me about yourself and your capabilities"
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
            temperature=0.7,
            top_p=1.0,
            safe_prompt=True,
            image_data=image_data,
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