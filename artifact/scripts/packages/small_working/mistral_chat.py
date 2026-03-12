"""
Mistral API Chat Implementation
This module provides a simple interface to the Mistral AI API for streaming chat responses.
Supports model selection, multi-turn conversations, and image analysis with streaming responses.

This version includes a complete, accessible, and robust implementation of the Mistral Files API:
- Upload file (with required purpose)
- List files
- Retrieve file metadata
- Delete file
- Download file content
- Get signed (temporary) download URL
- Text and chat classification
- OCR endpoint

References:
- [Mistral API Docs: Files](https://docs.mistral.ai/api/#tag/files)
- [Mistral API Docs: Classifications](https://docs.mistral.ai/api/#tag/classifications)
- [Mistral API Docs: OCR](https://docs.mistral.ai/api/#tag/ocr)
"""

import os
import sys
import requests
import json
import base64
from typing import Generator, List, Dict, Optional, Union, Any
from typing import List, Any
from datetime import datetime
from PIL import Image
import io

# Rich imports for enhanced CLI
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

# Initialize a rich console
console = Console()

class MistralChat:
    """
    MistralChat provides a high-level interface to the Mistral AI API, including chat, model listing,
    and a complete implementation of the Files API (upload, list, retrieve, delete, download, get signed URL),
    as well as classification and OCR endpoints.
    """

    def __init__(self, api_key: str):
        """Initialize the Mistral client with the provided API key."""
        # Strip quotes if present
        if isinstance(api_key, str) and api_key.startswith('"') and api_key.endswith('"'):
            api_key = api_key[1:-1]
        
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

    # --- Model Listing (unchanged) ---

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
        """
        try:
            response = requests.get(
                f"{self.api_url}/models",
                headers=self.headers
            )
            response.raise_for_status()
            models = []
            for model in response.json()["data"]:
                capabilities = []
                if model["capabilities"]["completion_chat"]:
                    capabilities.append("chat")
                if model["capabilities"]["function_calling"]:
                    capabilities.append("function")
                if model["capabilities"].get("vision"):
                    capabilities.append("vision")
                model_id = model["id"].lower()
                if "mixtral" in model_id:
                    category = "mixtral"
                elif "pixtral" in model_id:
                    category = "pixtral"
                else:
                    category = "mistral"
                if capability_filter and capability_filter not in capabilities:
                    continue
                if category_filter and category_filter != category:
                    continue
                models.append({
                    "id": model["id"],
                    "name": model.get("name") or model["id"].replace("-", " ").title(),
                    "description": model.get("description") or f"Mistral {model['id']} model",
                    "context_length": model["max_context_length"],
                    "created_at": datetime.fromtimestamp(model["created"]).strftime("%Y-%m-%d"),
                    "created": model["created"],
                    "capabilities": capabilities,
                    "category": category,
                    "owned_by": model["owned_by"],
                    "deprecated_at": model.get("deprecation")
                })
            if sort_by == "created":
                models.sort(key=lambda x: x["created"], reverse=reverse)
            elif sort_by == "context_length":
                models.sort(key=lambda x: x["context_length"], reverse=reverse)
            else:
                models.sort(key=lambda x: x["id"], reverse=reverse)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return models[start_idx:end_idx]
        except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
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
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return fallback_models[start_idx:end_idx]

    # --- Image Utilities (unchanged) ---

    def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> Optional[str]:
        """
        Create a test image and return its base64 encoding.
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
        """
        try:
            with Image.open(file_path) as img:
                if img.format not in ['PNG', 'JPEG', 'WEBP', 'GIF']:
                    print(f"Unsupported image format: {img.format}. Must be PNG, JPEG, WEBP, or single-frame GIF.", file=sys.stderr)
                    return None
                if img.format == 'GIF' and getattr(img, 'is_animated', False):
                    print("Animated GIFs are not supported.", file=sys.stderr)
                    return None
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format)
                if img_byte_arr.tell() > 10 * 1024 * 1024:
                    print("Image file size exceeds 10MB limit.", file=sys.stderr)
                    return None
                if img.size[0] > 1024 or img.size[1] > 1024:
                    ratio = min(1024/img.size[0], 1024/img.size[1])
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format)
                img_byte_arr = img_byte_arr.getvalue()
                return base64.b64encode(img_byte_arr).decode('utf-8')
        except Exception as e:
            print(f"Error loading image: {e}", file=sys.stderr)
            return None

    # --- Message Formatting (unchanged) ---

    def format_message_with_image(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
        """
        Format a message with optional image data for the API.
        """
        if not image_data:
            return message
        if isinstance(image_data, str):
            image_data = [image_data]
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
        """
        if not file_data:
            return message
        if isinstance(file_data, str):
            file_data = [file_data]
        content = [{"type": "text", "text": message}]
        for file_id in file_data:
            content.append({
                "type": "file",
                "file_id": file_id
            })
        return content

    # --- Chat Streaming (unchanged) ---

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
        """
        content = message
        if image_data:
            content = self.format_message_with_image(message, image_data, is_url)
        elif file_data:
            content = self.format_message_with_file(message, file_data)
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
                        line_text = line_text[6:]
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
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            self.conversation_history.pop()
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

    # --- Complete Files API Implementation ---

    def upload_file(self, file_path: str, purpose: str) -> Optional[str]:
        """
        Upload a file to Mistral's servers and return the file ID.

        Args:
            file_path (str): Path to the file to upload
            purpose (str): Purpose of the file ("fine-tune", "batch", "ocr", etc.)

        Returns:
            Optional[str]: File ID if successful, None otherwise

        Accessibility: Ensure file paths are accessible and errors are reported in a screen-reader-friendly way.
        """
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                upload_headers = {"Authorization": f"Bearer {self.api_key}"}
                response = requests.post(
                    f"{self.api_url}/files",
                    headers=upload_headers,
                    files=files,
                    data={"purpose": purpose}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("id")
        except Exception as e:
            print(f"Error uploading file: {e}", file=sys.stderr)
            return None

    def list_files(self, purpose: Optional[str] = None) -> List[Dict]:
        """
        List files uploaded to Mistral.

        Args:
            purpose (Optional[str]): Filter by purpose ('fine-tune', 'assistants', 'ocr', etc.)

        Returns:
            List[Dict]: List of file metadata

        Reference: https://docs.mistral.ai/api/#tag/files/operation/list_files_v1_files_get
        """
        try:
            params = {"purpose": purpose} if purpose else {}
            response = requests.get(
                f"{self.api_url}/files",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception as e:
            print(f"Error listing files: {e}", file=sys.stderr)
            return []

    def retrieve_file(self, file_id: str) -> Optional[Dict]:
        """
        Retrieve metadata for a specific file.

        Args:
            file_id (str): ID of the file to retrieve

        Returns:
            Optional[Dict]: File metadata or None if not found

        Reference: https://docs.mistral.ai/api/#tag/files/operation/retrieve_file_v1_files__file_id__get
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

        Reference: https://docs.mistral.ai/api/#tag/files/operation/delete_file_v1_files__file_id__delete
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

    def download_file(self, file_id: str) -> Optional[bytes]:
        """
        Download a file's content.

        Args:
            file_id (str): ID of the file to download

        Returns:
            Optional[bytes]: File content or None if download fails

        Reference: https://docs.mistral.ai/api/#tag/files/operation/download_file_v1_files__file_id__content_get
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

    def get_signed_url(self, file_id: str) -> Optional[str]:
        """
        Get a signed (temporary) download URL for a file.

        Args:
            file_id (str): ID of the file

        Returns:
            Optional[str]: Signed download URL or None if failed

        Reference: https://docs.mistral.ai/api/#tag/files/operation/get_signed_url_v1_files__file_id__download_url_post
        """
        try:
            response = requests.post(
                f"{self.api_url}/files/{file_id}/download_url",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get("download_url")
        except Exception as e:
            print(f"Error getting signed URL: {e}", file=sys.stderr)
            return None

    # For backward compatibility with previous CLI code
    get_file_content = download_file
    get_file_url = get_signed_url

    # --- Classification and OCR Endpoints ---

    def classify(self, input_data: Union[str, List[str]], model: str = "mistral-small-latest") -> Optional[Dict]:
        """
        Classify text input.

        Args:
            input_data (str or List[str]): The text or list of texts to classify.
            model (str): The classification model to use.

        Returns:
            Optional[Dict]: Classification result or None on error.
        """
        payload = {"model": model, "input": input_data}
        try:
            resp = requests.post(f"{self.api_url}/classifications", headers=self.headers, json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error in classify: {e}", file=sys.stderr)
            return None

    def classify_chat(self, messages: List[Dict[str, str]], model: str = "mistral-small-latest") -> Optional[Dict]:
        """
        Classify a sequence of chat messages.

        Args:
            messages (List[Dict[str, str]]): List of chat messages (role/content dicts).
            model (str): The classification model to use.

        Returns:
            Optional[Dict]: Classification result or None on error.
        """
        payload = {"model": model, "input": {"messages": messages}}
        try:
            resp = requests.post(f"{self.api_url}/chat/classifications", headers=self.headers, json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error in classify_chat: {e}", file=sys.stderr)
            return None

    def ocr(
        self,
        model: str,
        document: Dict[str, Any],
        id: Optional[str] = None,
        pages: Optional[List[int]] = None,
        include_image_base64: bool = False,
        image_limit: Optional[int] = None,
        image_min_size: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Run OCR on a document via Mistral's OCR API.

        Args:
            model (str): The OCR model to use (e.g., "mistral-ocr-latest").
            document (Dict[str, Any]): Document descriptor (e.g., {"type": "document_url", "document_url": ...}).
            id (Optional[str]): Optional document ID.
            pages (Optional[List[int]]): Optional list of page numbers to process.
            include_image_base64 (bool): Whether to include base64-encoded images in the response.
            image_limit (Optional[int]): Limit the number of images.
            image_min_size (Optional[int]): Minimum image size.

        Returns:
            Optional[Dict]: OCR result or None on error.
        """
        payload: Dict[str, Any] = {"model": model, "document": document}
        if id:
            payload["id"] = id
        if pages is not None:
            payload["pages"] = pages
        payload["include_image_base64"] = include_image_base64
        if image_limit is not None:
            payload["image_limit"] = image_limit
        if image_min_size is not None:
            payload["image_min_size"] = image_min_size
        try:
            resp = requests.post(f"{self.api_url}/ocr", headers=self.headers, json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error in ocr: {e}", file=sys.stderr)
            return None

    def cite(self,
             text: str,
             model: str = "mistral-cite-latest",
             include_references: bool = True) -> Optional[Dict[str, Any]]:
        """
        Generate in-text citations for the provided text and optionally retrieve reference list.
        """
        payload = {
            "model": model,
            "text": text,
            "include_references": include_references
        }
        try:
            resp = requests.post(f"{self.api_url}/citations", headers=self.headers, json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error generating citations: {e}", file=sys.stderr)
            return None

    def get_references(self,
                       citation_ids: List[str],
                       model: str = "mistral-cite-latest") -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve formatted reference entries for given citation IDs.
        """
        payload = {
            "model": model,
            "citation_ids": citation_ids
        }
        try:
            resp = requests.post(f"{self.api_url}/references", headers=self.headers, json=payload)
            resp.raise_for_status()
            return resp.json().get("references")
        except Exception as e:
            print(f"Error retrieving references: {e}", file=sys.stderr)
            return None

# --- CLI and Display Utilities (unchanged) ---

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
    models_by_category = {}
    for model in models:
        category = model["category"]
        if category not in models_by_category:
            models_by_category[category] = []
        models_by_category[category].append(model)
    idx = 1
    for category in sorted(models_by_category.keys()):
        if not category_filter:
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
    """
    Main CLI interface for MistralChat.
    Includes accessible file management using the full Mistral Files API.
    """
    api_key = os.getenv("MISTRAL_API_KEY") or "n8R347515VqP48oDHwBeL9BS6nW1L8zY"
    if not api_key:
        console.print("Error: MISTRAL_API_KEY environment variable not set", style="bold red")
        sys.exit(1)
    
    # Strip quotes if present
    if isinstance(api_key, str) and api_key.startswith('"') and api_key.endswith('"'):
        api_key = api_key[1:-1]
    
    chat = MistralChat(api_key)
    page = 1
    page_size = 5
    sort_by = "created"
    category_filter = None
    capability_filter = None
    all_models = chat.list_models(
        sort_by=sort_by,
        page=1,
        page_size=1000,
        category_filter=category_filter,
        capability_filter=capability_filter
    )
    total_pages = (len(all_models) + page_size - 1) // page_size
    while True:
        models = chat.list_models(
            sort_by=sort_by,
            page=page,
            page_size=page_size,
            category_filter=category_filter,
            capability_filter=capability_filter
        )
        display_models(models, page, total_pages, sort_by, category_filter, capability_filter)
        console.print("\n[bold cyan]Options:[/bold cyan]")
        console.print("1. Select model")
        console.print("2. Next page")
        console.print("3. Previous page")
        console.print("4. Sort by (created/context_length/id)")
        console.print("5. Filter by category (mistral/mixtral/pixtral/none)")
        console.print("6. Filter by capability (chat/function/vision/none)")
        console.print("7. Change page size")
        console.print("8. File Management")
        console.print("9. OCR Document")
        console.print("10. Generate Citations")
        console.print("11. Get References")
        console.print("12. Quit")
        choice = get_user_input("Select option", "1")
        if choice == "1":
            try:
                selection = int(get_user_input("Select a model number", "1")) - 1
                if 0 <= selection < len(models):
                    selected_model = models[selection]["id"]
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
                "Sort by (created/context_length/id)",
                "created"
            )
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                category_filter=category_filter,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1
        elif choice == "5":
            cat_choice = get_user_input(
                "Filter by category (mistral/mixtral/pixtral/none)",
                "none"
            ).lower()
            category_filter = None if cat_choice == "none" else cat_choice
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                category_filter=category_filter,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1
        elif choice == "6":
            cap_choice = get_user_input(
                "Filter by capability (chat/function/vision/none)",
                "none"
            ).lower()
            capability_filter = None if cap_choice == "none" else cap_choice
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                category_filter=category_filter,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1
        elif choice == "7":
            try:
                new_size = int(get_user_input("Enter page size", str(page_size)))
                if new_size > 0:
                    page_size = new_size
                    total_pages = (len(all_models) + page_size - 1) // page_size
                    page = 1
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "8":
            while True:
                print("\nFile Management:")
                print("1. Upload File")
                print("2. List Files")
                print("3. Download File")
                print("4. Delete File")
                print("5. Get File URL")
                print("6. Retrieve File Metadata")
                print("7. Back to Main Menu")
                file_choice = get_user_input("Select option", "1")
                if file_choice == "1":
                    file_path = get_user_input("Enter file path")
                    if os.path.exists(file_path):
                        # Ask for purpose
                        purpose = get_user_input("Enter file purpose (fine-tune/batch/ocr)", "fine-tune")
                        result = chat.upload_file(file_path, purpose)
                        if result:
                            print(f"File uploaded successfully. ID: {result}")
                        else:
                            print("File upload failed.")
                    else:
                        print("File not found.")
                elif file_choice == "2":
                    purpose = get_user_input("Filter by purpose (fine-tune/assistants/ocr/none)", "none")
                    purpose = None if purpose.lower() == "none" else purpose
                    files = chat.list_files(purpose)
                    if files:
                        print("\nAvailable Files:")
                        for file in files:
                            print(f"ID: {file.get('id')}")
                            print(f"Name: {file.get('filename')}")
                            print(f"Size: {file.get('bytes')} bytes")
                            print(f"Created: {file.get('created_at')}")
                            print("-" * 30)
                    else:
                        print("No files found.")
                elif file_choice == "3":
                    file_id = get_user_input("Enter file ID")
                    content = chat.download_file(file_id)
                    if content:
                        save_path = get_user_input("Enter save path")
                        try:
                            with open(save_path, 'wb') as f:
                                f.write(content)
                            print(f"File saved to {save_path}")
                        except Exception as e:
                            print(f"Error saving file: {e}")
                    else:
                        print("Failed to download file.")
                elif file_choice == "4":
                    file_id = get_user_input("Enter file ID")
                    if chat.delete_file(file_id):
                        print("File deleted successfully.")
                    else:
                        print("Failed to delete file.")
                elif file_choice == "5":
                    file_id = get_user_input("Enter file ID")
                    url = chat.get_signed_url(file_id)
                    if url:
                        print(f"Temporary download URL: {url}")
                    else:
                        print("Failed to get signed URL.")
                elif file_choice == "6":
                    file_id = get_user_input("Enter file ID")
                    metadata = chat.retrieve_file(file_id)
                    if metadata:
                        print(json.dumps(metadata, indent=2))
                    else:
                        print("Failed to retrieve file metadata.")
                elif file_choice == "7":
                    break
                print()
        elif choice == "9":
            # OCR Document
            doc_type = Prompt.ask("Document input type", choices=["url", "file"], default="url")
            if doc_type == "url":
                url = Prompt.ask("Enter document URL")
                document = {"type": "document_url", "document_url": url}
            else:
                file_path = Prompt.ask("Enter local file path")
                file_id = chat.upload_file(file_path, purpose="ocr")
                document = {"type": "file_id", "id": file_id}
            model = Prompt.ask("OCR model", default="mistral-ocr-latest")
            result = chat.ocr(model, document)
            console.print_json(data=result)

        elif choice == "10":
            # Generate Citations
            text = Prompt.ask("Enter text to cite")
            model = Prompt.ask("Citation model", default="mistral-cite-latest")
            result = chat.cite(text, model=model)
            console.print_json(data=result)

        elif choice == "11":
            # Get References
            ids_str = Prompt.ask("Enter citation IDs (comma-separated)")
            citation_ids = [cid.strip() for cid in ids_str.split(",")]
            model = Prompt.ask("Citation model", default="mistral-cite-latest")
            result = chat.get_references(citation_ids, model=model)
            console.print_json(data=result)

        elif choice == "12":
            console.print("Exiting...", style="bold red")
            sys.exit(0)
        print()
    # Start conversation loop
    while True:
        supports_images = "vision" in models[selection]["capabilities"]
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
                file_path = get_user_input("Enter image file path")
                image_data = chat.load_image_from_file(file_path)
                if not image_data:
                    print("Failed to load image. Continuing without image...")
            elif image_choice == "4":
                url = get_user_input("Enter image URL")
                if url:
                    image_data = url
                    is_url = True
            elif image_choice == "5":
                print("\nCreating test image...")
                color = get_user_input("Enter color (e.g., red, blue, green)", "red")
                size_str = get_user_input("Enter size (width,height)", "100,100")
                try:
                    width, height = map(int, size_str.split(","))
                    test_image_data = chat.create_test_image(color=color, size=(width, height))
                    if test_image_data:
                        temp_path = f"temp_test_image_{color}.png"
                        try:
                            with open(temp_path, 'wb') as f:
                                f.write(base64.b64decode(test_image_data))
                            print("Uploading image to Mistral...")
                            # Use "ocr" as purpose for image uploads via File API, or prompt user
                            purpose = get_user_input("Enter file purpose for image upload (fine-tune/batch/ocr)", "ocr")
                            result = chat.upload_file(temp_path, purpose)
                            if result:
                                print(f"Image uploaded successfully. ID: {result}")
                                url = chat.get_signed_url(result)
                                if url:
                                    print("Retrieved file URL for chat.")
                                    image_data = url
                                    is_url = True
                                else:
                                    print("Failed to get signed URL. Continuing without image...")
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
        default_prompt = "What do you see in this image?" if image_data else "Tell me about yourself and your capabilities"
        message = get_user_input(
            "Enter your message",
            default_prompt
        )
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
        if get_user_input("\nContinue conversation? (y/n)", "y").lower() != 'y':
            print("\nClearing conversation history and exiting...")
            chat.clear_conversation()
            break
        print("\nContinuing conversation...\n")

if __name__ == "__main__":
    main()