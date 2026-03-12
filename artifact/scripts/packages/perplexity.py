"""
Perplexity API Chat Implementation
This module provides a simple interface to the Perplexity API for streaming chat responses.
Supports model selection and multi-turn conversations with streaming responses.
"""

import requests
import json
import sys
from typing import Generator, List, Dict, Optional
from datetime import datetime

class PerplexityChat:
    MODELS = {
        "sonar-reasoning-pro": {
            "id": "sonar-reasoning-pro",
            "context_length": 127000,
            "description": "Advanced reasoning and analysis"
        },
        "sonar-reasoning": {
            "id": "sonar-reasoning",
            "context_length": 127000,
            "description": "Enhanced reasoning capabilities"
        },
        "sonar-pro": {
            "id": "sonar-pro",
            "context_length": 200000,
            "description": "Professional grade completion"
        },
        "sonar": {
            "id": "sonar",
            "context_length": 127000,
            "description": "Standard chat completion"
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
        Stream a chat response from Perplexity.
        
        Args:
            message (str): The user's input message
            model (str): The Perplexity model to use
            temperature (float): Response temperature (0.0 to 1.0)
            
        Yields:
            str: Chunks of the response text as they arrive
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
            for line in response.iter_lines():
                if line:
                    try:
                        line_text = line.decode('utf-8')
                        if line_text.startswith("data: "):
                            line_text = line_text[6:]  # Remove "data: " prefix
                        if line_text == "[DONE]":
                            break
                        
                        data = json.loads(line_text)
                        if data.get("choices") and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                content = delta["content"]
                                full_response += content
                                yield content
                            
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

def main():
    """Main CLI interface."""
    # Initialize with API key
    api_key = "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"
    
    chat = PerplexityChat(api_key)
    
    # Fetch and display available models
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
    
    # Start conversation loop
    while True:
        # Get message
        message = get_user_input(
            "Enter your message",
            "Tell me about yourself and your capabilities"
        )
        
        # Stream response
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