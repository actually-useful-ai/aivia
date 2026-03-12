"""
Anthropic API Chat Implementation
This module provides a simple interface to the Anthropic Claude API for streaming chat responses.
Supports both text-only and multimodal (image analysis) conversations with streaming responses.
Requires the 'anthropic' package to be installed (pip install anthropic)
"""

import os
import sys
import anthropic
from typing import Generator, List, Dict, Optional
from datetime import datetime
from base64 import b64encode
from PIL import Image, ImageDraw, ImageFont
import io

MODULE_NAME = "anthropic_chat"
MODULE_TYPE = "Belter"
MODULE_DISPLAY_NAME = "Anthropic Chat"
MODULE_DESCRIPTION = "Chat with Claude, the AI assistant from Anthropic."

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or "REDACTED_ANTHROPIC_KEY"

class AnthropicChat:
    def __init__(self, api_key: str):
        """Initialize the Anthropic client with the provided API key."""
        self.client = anthropic.Client(api_key=api_key)
        self.conversation_history = []
        
    def list_models(
        self,
        sort_by: str = "created",
        reverse: bool = True,
        page: int = 1,
        page_size: int = 5,
        capability_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve available Claude models with pagination.
        
        Args:
            sort_by (str): Field to sort by ('created', 'id', 'capabilities')
            reverse (bool): Whether to reverse sort order
            page (int): Page number (1-based)
            page_size (int): Number of items per page
            capability_filter (Optional[str]): Filter models by capability ('vision', 'text')
            
        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            models = self.client.models.list()
            # Process and enhance model data
            processed_models = []
            for model in models.data:
                if not model.id.startswith("claude") or "claude-3" not in model.id:
                    continue
                
                # Determine capabilities
                capabilities = ["text"]  # All models support text
                if "opus" in model.id.lower():
                    capabilities.extend(["vision", "code", "analysis"])
                elif "sonnet" in model.id.lower():
                    capabilities.extend(["vision", "code"])
                elif "haiku" in model.id.lower():
                    capabilities.append("vision")
                
                # Skip if doesn't match capability filter
                if capability_filter and capability_filter not in capabilities:
                    continue
                
                # Create enhanced model info
                model_info = {
                    "id": model.id,
                    "name": model.id.replace("-", " ").title(),
                    "description": f"Claude 3 {model.id.split('-')[-2].title()} - Advanced AI model",
                    "capabilities": capabilities,
                    "capability_count": len(capabilities),
                    "created": model.created_at,
                    "created_at": format_date(model.created_at),
                    "owned_by": "anthropic"
                }
                processed_models.append(model_info)
            
            # Sort models
            if sort_by == "created":
                processed_models.sort(key=lambda x: x["created"], reverse=reverse)
            elif sort_by == "capabilities":
                processed_models.sort(key=lambda x: x["capability_count"], reverse=reverse)
            else:  # sort by id
                processed_models.sort(key=lambda x: x["id"], reverse=reverse)
            
            # Calculate pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            return processed_models[start_idx:end_idx]
            
        except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            return []

    def create_test_image(self) -> str:
        """
        Create a test image with some shapes and text.
        Returns base64 encoded PNG image.
        """
        # Create a new image with a white background
        width, height = 400, 200
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw some shapes
        draw.rectangle([50, 50, 150, 150], fill='red', outline='black')
        draw.ellipse([200, 50, 300, 150], fill='blue', outline='black')
        
        # Add text
        draw.text((150, 160), "Test Image", fill='black')
        
        # Convert to base64
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return b64encode(img_byte_arr).decode('utf-8')

    def create_test_file(self) -> str:
        """Create a simple test text file and return its base64 encoding."""
        test_content = "This is a test file content.\nIt has multiple lines.\nHello, Claude!"
        return b64encode(test_content.encode('utf-8')).decode('utf-8')

    def process_image(self, image_path: str) -> Optional[Dict]:
        """
        Process an image file and return it in the format required by Claude.
        Supports PNG, JPEG, GIF, and WEBP formats.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Optional[Dict]: Image data formatted for Claude API or None if invalid
        """
        try:
            with Image.open(image_path) as img:
                # Convert format name to mime type
                format_to_mime = {
                    'PNG': 'image/png',
                    'JPEG': 'image/jpeg',
                    'GIF': 'image/gif',
                    'WEBP': 'image/webp'
                }
                
                if img.format not in format_to_mime:
                    print(f"Unsupported image format: {img.format}. Must be PNG, JPEG, GIF, or WEBP.", 
                          file=sys.stderr)
                    return None
                
                # Convert to bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format)
                img_byte_arr = img_byte_arr.getvalue()
                
                return {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": format_to_mime[img.format],
                        "data": b64encode(img_byte_arr).decode('utf-8')
                    }
                }
                
        except Exception as e:
            print(f"Error processing image: {e}", file=sys.stderr)
            return None

    def stream_chat_response(
        self,
        prompt: str,
        max_tokens: int = 1024,
        model: str = "claude-3-opus-20240229",
        image_path: Optional[str] = None,
        use_test_image: bool = False
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from Claude.
        
        Args:
            prompt (str): The user's input message
            max_tokens (int): Maximum number of tokens in the response
            model (str): The Claude model to use
            image_path (Optional[str]): Path to an image file (PNG, JPEG, GIF, or WEBP)
            use_test_image (bool): Whether to use the test image instead of image_path
            
        Yields:
            str: Chunks of the response text as they arrive
        """
        try:
            # Construct the message content
            message_content = [{"type": "text", "text": prompt}]
            
            if use_test_image:
                message_content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": self.create_test_image()
                    }
                })
            elif image_path:
                image_data = self.process_image(image_path)
                if image_data:
                    message_content.append(image_data)

            # Add the new message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message_content
            })

            # Stream the response
            with self.client.messages.stream(
                max_tokens=max_tokens,
                messages=self.conversation_history,
                model=model,
            ) as stream:
                response_text = ""
                for text in stream.text_stream:
                    response_text += text
                    yield text
                
                # Add assistant's response to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response_text
                })
                    
        except anthropic.APIError as e:
            print(f"API Error: {e}", file=sys.stderr)
        except anthropic.APIConnectionError as e:
            print(f"Connection Error: {e}", file=sys.stderr)
        except anthropic.AuthenticationError as e:
            print(f"Authentication Error: Please check your API key", file=sys.stderr)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)

    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []

def format_date(date_str: str) -> str:
    """Format the date string in a human-readable format."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%B %d, %Y")
    except:
        return date_str

def display_models(
    models: List[Dict],
    current_page: int,
    total_pages: int,
    sort_by: str,
    capability_filter: Optional[str] = None
) -> None:
    """Display available models in a formatted way."""
    print(f"\nAvailable Claude Models (Page {current_page}/{total_pages}):")
    print(f"Sorting by: {sort_by}")
    if capability_filter:
        print(f"Filtering by capability: {capability_filter}")
    print("-" * 50)
    
    for idx, model in enumerate(models, 1):
        print(f"{idx}. {model['name']}")
        print(f"   Model: {model['id']}")
        print(f"   Description: {model['description']}")
        print(f"   Capabilities: {', '.join(model['capabilities'])}")
        print(f"   Released: {model['created_at']}")
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
    api_key = os.getenv("ANTHROPIC_API_KEY") or "REDACTED_ANTHROPIC_KEY"
    
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    chat = AnthropicChat(api_key)
    
    # Model browsing loop
    page = 1
    page_size = 5
    sort_by = "created"
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
        print("Error: Could not fetch models. Please check your API key and connection.")
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
        print("4. Sort by (created/id/capabilities)")
        print("5. Filter by capability (vision/text/code/analysis/none)")
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
                "Sort by (created/id/capabilities)",
                "created"
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
                "Filter by capability (vision/text/code/analysis/none)",
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
        # Ask about including an image
        image_choice = get_user_input("Image options: (1) No image (2) Test image (3) Custom image path", "1")
        
        image_path = None
        use_test_image = False
        
        if image_choice == "2":
            use_test_image = True
        elif image_choice == "3":
            image_path = get_user_input("Enter image path", "")
        
        # Get prompt
        default_prompt = "What do you see in this image?" if (use_test_image or image_path) else "Hello! How can I help you today?"
        prompt = get_user_input("Enter your prompt", default_prompt)
        
        # Stream response
        print("\nStreaming response:")
        print("-" * 50)
        for chunk in chat.stream_chat_response(prompt, 1024, selected_model, image_path, use_test_image):
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