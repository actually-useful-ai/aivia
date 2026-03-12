"""
X.AI API Chat Implementation
This module provides an interface to the X.AI API with support for:
- Interactive model selection
- Response streaming
- Multimodal inputs (text + images)
"""

import os
import sys
from openai import OpenAI
from typing import Generator, List, Dict, Optional
from datetime import datetime
from base64 import b64encode
from PIL import Image
import io
import requests

class XAIChat:
    def __init__(self, api_key: str):
        """Initialize the X.AI client with the provided API key."""
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        self.conversation_history = [
            {
                "role": "system",
                "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
            }
        ]
    
    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.conversation_history = [self.conversation_history[0]]
    
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
                capabilities.extend(["text", "code"])  # All models support text and code
                
                models.append({
                    "id": model.id,
                    "name": model.id.replace("-", " ").title(),
                    "capabilities": capabilities,
                    "context_window": getattr(model, "context_window", 8192),  # Default to 8192 if not specified
                    "created_at": datetime.fromtimestamp(model.created).strftime("%Y-%m-%d")
                })
            
            return sorted(models, key=lambda x: x["created_at"], reverse=True)
            
        except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            # Fallback to basic Grok model if API fails
            return [{
                "id": "grok-2-latest",
                "name": "Grok 2 Latest",
                "capabilities": ["text", "code", "images"],
                "context_window": 8192,
                "created_at": "2024-02-01"
            }]
    
    def create_test_image(self) -> str:
        """Create a simple test image and return its base64 encoding."""
        # Create a 100x100 red square image
        img = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return b64encode(img_byte_arr).decode('utf-8')

    def stream_chat_response(
        self,
        prompt: str,
        model: str,
        image: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from X.AI.
        
        Args:
            prompt (str): The user's input message
            model (str): The X.AI model to use
            image (Optional[str]): Base64 encoded image data
            
        Yields:
            str: Chunks of the response text as they arrive
        """
        # Add image content if provided
        if image:
            message_content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image}"
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
            stream = self.client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                stream=True
            )
            
            response_text = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    response_text += text
                    yield text
            
            # Add assistant's response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
                    
        except Exception as e:
            print(f"Error in stream_chat_response: {e}", file=sys.stderr)

def display_models(models: List[Dict]) -> None:
    """Display available models in a formatted way."""
    print("\nAvailable X.AI Models:")
    print("-" * 50)
    for idx, model in enumerate(models, 1):
        print(f"{idx}. {model['name']} ({model['id']})")
        print(f"   Capabilities: {', '.join(model['capabilities'])}")
        print(f"   Context Window: {model['context_window']} tokens")
        print(f"   Released: {model['created_at']}")
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
    api_key = os.getenv("XAI_API_KEY") or "REDACTED_XAI_KEY"
    
    if not api_key:
        print("Error: XAI_API_KEY environment variable not set")
        sys.exit(1)
    
    chat = XAIChat(api_key)
    
    # Fetch and display available models
    models = chat.list_models()
    display_models(models)
    
    # Get model selection
    while True:
        try:
            selection = int(get_user_input("Select a model number", "1")) - 1
            if 0 <= selection < len(models):
                selected_model = models[selection]["id"]
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Start conversation loop
    while True:
        # Ask about including an image
        include_image = get_user_input("Include test image? (y/n)", "n").lower() == 'y'
        test_image = chat.create_test_image() if include_image else None
        
        # Get prompt
        default_prompt = "What do you see in this image?" if include_image else "Tell me a joke about AI"
        prompt = get_user_input("Enter your prompt", default_prompt)
        
        # Stream response
        print("\nStreaming response:")
        print("-" * 50)
        for chunk in chat.stream_chat_response(prompt, selected_model, test_image):
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