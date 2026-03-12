#!/usr/bin/env python
import sys
import os
import base64
import io
from datetime import datetime
from typing import Generator, List, Dict, Optional, Union
from PIL import Image
import tempfile

# -------------------------------------------------------------------
# OpenAI Chat Implementation
# -------------------------------------------------------------------

from openai import OpenAI

class OpenAIChat:
    # Default models in case API fetch fails
    DEFAULT_MODELS = {
        "gpt-4o-2024-11-20": {
            "id": "gpt-4o-2024-11-20",
            "context_length": 128000,
            "description": "GPT-4 Omega model",
            "capabilities": ["text", "function"]
        },
        "gpt-4-vision-preview": {
            "id": "gpt-4-vision-preview",
            "context_length": 128000,
            "description": "GPT-4 model with vision capabilities",
            "capabilities": ["text", "vision", "function"]
        },
        "gpt-4-0125-preview": {
            "id": "gpt-4-0125-preview",
            "context_length": 128000,
            "description": "GPT-4 preview model",
            "capabilities": ["text", "function"]
        },
        "gpt-4": {
            "id": "gpt-4",
            "context_length": 8192,
            "description": "GPT-4 base model",
            "capabilities": ["text", "function"]
        },
        "gpt-3.5-turbo-0125": {
            "id": "gpt-3.5-turbo-0125",
            "context_length": 16385,
            "description": "GPT-3.5 Turbo model",
            "capabilities": ["text", "function"]
        }
    }

    def __init__(self, api_key: str):
        """Initialize the OpenAI client with the provided API key."""
        # Patch OpenAI to disable proxies if not already done.
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
                    description = f"GPT {model_id}"
                    if "vision" in model_id:
                        description += " with vision capabilities"
                    elif "32k" in model_id:
                        description += " with 32k context"
                    elif "16k" in model_id:
                        description += " with 16k context"
                    
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
        
        if sort_by == "created":
            models_list.sort(key=lambda x: x["created"], reverse=reverse)
        elif sort_by == "context_length":
            models_list.sort(key=lambda x: x["context_length"], reverse=reverse)
        elif sort_by == "capabilities":
            models_list.sort(key=lambda x: (
                x["capability_count"],
                "images" in x["capabilities"],
                "text" in x["capabilities"]
            ), reverse=reverse)
        else:
            models_list.sort(key=lambda x: x["id"], reverse=reverse)
        
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
        
        if image_data:
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
            content = self.format_message_with_attachments(message, image_data, file_data, is_url)
            
            self.chat_history.append({
                "role": "user",
                "content": content
            })
            
            messages = []
            for msg in self.chat_history:
                if isinstance(msg["content"], list):
                    messages.append(msg)
                else:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
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
            
            self.chat_history.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            print(f"Error in stream_chat_response: {e}", file=sys.stderr)
            if self.chat_history:
                self.chat_history.pop()
            yield f"Error: {str(e)}"

    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on providing accurate and detailed responses."
        }]

# -------------------------------------------------------------------
# CLI Helper Functions (for testing in terminal)
# -------------------------------------------------------------------

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

def main_cli():
    """Main CLI interface."""
    api_key = "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"
    chat = OpenAIChat(api_key)
    
    page = 1
    page_size = 5
    sort_by = "created"
    generation = None
    capability_filter = None
    
    while True:
        all_models = chat.list_models(sort_by=sort_by, page=1, page_size=1000, generation=generation)
        if capability_filter:
            all_models = [model for model in all_models if capability_filter in model["capabilities"]]
        
        total_pages = (len(all_models) + page_size - 1) // page_size
        
        models = chat.list_models(sort_by=sort_by, page=page, page_size=page_size, generation=generation)
        if capability_filter:
            models = [model for model in models if capability_filter in model["capabilities"]]
        
        display_models(models, page, total_pages, sort_by, generation)
        
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
            try:
                selection = int(get_user_input("Select a model number", "1")) - 1
                if 0 <= selection < len(models):
                    selected_model = models[selection]["name"]
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
            sort_by = get_user_input("Sort by (created/context_length/id/capabilities)", "created")
            page = 1
        elif choice == "5":
            gen = get_user_input("Filter by generation (4/3.5/3/none)", "none")
            generation = None if gen.lower() == "none" else gen
            page = 1
        elif choice == "6":
            cap_choice = get_user_input("Filter by capability (text/function/vision/none)", "none").lower()
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
            print("Exiting...")
            sys.exit(0)
        
        print()
    
    # Conversation loop
    while True:
        supports_images = "vision" in chat.models[selected_model]["capabilities"]
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
            file_path = get_user_input("Enter image file path")
            image_data = chat.encode_image(file_path)
            if not image_data:
                print("Failed to load image. Continuing without image...")
        elif input_choice == "4" and supports_images:
            url = get_user_input("Enter image URL")
            if url:
                image_data = url
                is_url = True
        elif input_choice == "5":
            content = get_user_input("Enter file content (or press Enter for default)")
            file_data = chat.create_test_file(content if content else None)
        elif input_choice == "6":
            file_path = get_user_input("Enter file path")
            file_data = chat.encode_file(file_path)
            if not file_data:
                print("Failed to load file. Continuing without file...")
        
        default_prompt = "What do you see in this image?" if image_data else "Please analyze this file" if file_data else "Hello! How can I help you today?"
        message = get_user_input("Enter your message", default_prompt)
        
        print("\nStreaming response:")
        print("-" * 50)
        for chunk in chat.stream_chat_response(message, selected_model, image_data=image_data, file_data=file_data, is_url=is_url):
            print(chunk, end="", flush=True)
        print("\n" + "-" * 50)
        
        if get_user_input("\nContinue conversation? (y/n)", "y").lower() != 'y':
            print("\nClearing conversation history and exiting...")
            chat.clear_conversation()
            break
        print("\nContinuing conversation...\n")

# -------------------------------------------------------------------
# Flask Web UX Integration for OpenAI
# -------------------------------------------------------------------

from flask import Flask, request, render_template_string, Response

app = Flask(__name__)

# Add this before the Flask routes
DEFAULT_API_KEY = "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"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>OpenAI Chat Interface</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 2rem; }
    #output { white-space: pre-wrap; border: 1px solid #ccc; padding: 1rem; margin-top: 1rem; }
    .model-selector { margin-bottom: 1.5rem; }
    .model-card {
      border: 1px solid #ddd;
      padding: 1rem;
      margin: 0.5rem 0;
      border-radius: 4px;
      cursor: pointer;
    }
    .model-card:hover { background-color: #f5f5f5; }
    .model-card.selected { background-color: #e3f2fd; border-color: #2196f3; }
    .model-capabilities { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
    .capability-tag {
      background: #e0e0e0;
      padding: 0.2rem 0.5rem;
      border-radius: 12px;
      font-size: 0.8rem;
    }
    .controls { display: flex; gap: 1rem; align-items: center; margin-bottom: 1rem; }
    button { 
      padding: 0.5rem 1rem; 
      background: #2196f3; 
      color: white; 
      border: none; 
      border-radius: 4px;
      cursor: pointer;
    }
    button:hover { background: #1976d2; }
    .loading { display: none; margin-left: 1rem; }
    #modelError { color: red; margin: 1rem 0; }
    .model-info {
      display: flex;
      justify-content: space-between;
      margin-top: 0.5rem;
      font-size: 0.9rem;
      color: #666;
    }
  </style>
</head>
<body>
  <h1>OpenAI Chat Interface</h1>
  
  <div class="model-selector">
    <h2>Select Model</h2>
    <div class="controls">
      <select id="sortBy">
        <option value="created">Sort by Created Date</option>
        <option value="context_length">Sort by Context Length</option>
        <option value="capabilities">Sort by Capabilities</option>
        <option value="id">Sort by ID</option>
      </select>
      <select id="generation">
        <option value="none">All Generations</option>
        <option value="4">GPT-4 Only</option>
        <option value="3.5">GPT-3.5 Only</option>
        <option value="3">GPT-3 Only</option>
      </select>
      <select id="capability">
        <option value="none">All Capabilities</option>
        <option value="vision">Vision</option>
        <option value="function">Function Calling</option>
        <option value="text">Text</option>
      </select>
      <button onclick="refreshModels()">Refresh Models</button>
      <div class="loading" id="modelLoading">Loading models...</div>
    </div>
    <div id="modelError"></div>
    <div id="modelList"></div>
  </div>

  <form id="upload-form">
    <label for="image">Select Image (optional):</label>
    <input type="file" id="image" name="image" accept="image/*"><br><br>
    <label for="prompt">Prompt:</label>
    <input type="text" id="prompt" name="prompt" size="80" value="Generate descriptive alt text for the visually impaired for social media"><br><br>
    <button type="submit">Submit</button>
    <div class="loading" id="generateLoading">Generating response...</div>
  </form>
  <h2>Response:</h2>
  <div id="output"></div>

  <script>
    let selectedModel = null;
    
    async function fetchModels() {
      const sortBy = document.getElementById('sortBy').value;
      const generation = document.getElementById('generation').value;
      const capability = document.getElementById('capability').value;
      
      try {
        document.getElementById('modelLoading').style.display = 'block';
        document.getElementById('modelError').textContent = '';
        
        const response = await fetch(`/models?sort_by=${sortBy}&generation=${generation}&capability=${capability}`);
        if (!response.ok) {
          throw new Error(await response.text());
        }
        
        const models = await response.json();
        const modelList = document.getElementById('modelList');
        modelList.innerHTML = '';
        
        models.forEach(model => {
          const modelCard = document.createElement('div');
          modelCard.className = `model-card${selectedModel === model.id ? ' selected' : ''}`;
          modelCard.onclick = () => selectModel(model.id);
          
          modelCard.innerHTML = `
            <strong>${model.name}</strong>
            <div>${model.description}</div>
            <div class="model-capabilities">
              ${model.capabilities.map(cap => 
                `<span class="capability-tag">${cap}</span>`
              ).join('')}
            </div>
            <div class="model-info">
              <span>Context: ${model.context_length.toLocaleString()} tokens</span>
              <span>Released: ${model.created_str}</span>
              ${model.version ? `<span>Version: ${model.version}</span>` : ''}
            </div>
          `;
          
          modelList.appendChild(modelCard);
        });
      } catch (err) {
        document.getElementById('modelError').textContent = `Error loading models: ${err.message}`;
      } finally {
        document.getElementById('modelLoading').style.display = 'none';
      }
    }
    
    function selectModel(modelId) {
      selectedModel = modelId;
      document.querySelectorAll('.model-card').forEach(card => {
        card.classList.toggle('selected', card.querySelector('strong').textContent === modelId);
      });
    }
    
    function refreshModels() {
      fetchModels();
    }
    
    document.getElementById("upload-form").addEventListener("submit", async function(e) {
      e.preventDefault();
      
      if (!selectedModel) {
        alert('Please select a model first');
        return;
      }
      
      document.getElementById("output").textContent = "";
      document.getElementById("generateLoading").style.display = 'block';
      
      const formData = new FormData();
      const imageInput = document.getElementById("image");
      const promptInput = document.getElementById("prompt");
      if (imageInput.files[0]) {
        formData.append("image", imageInput.files[0]);
      }
      formData.append("prompt", promptInput.value);
      formData.append("model", selectedModel);

      try {
        const response = await fetch("/generate", {
          method: "POST",
          body: formData
        });
        if (!response.ok) {
          document.getElementById("output").textContent = "Error: " + await response.text();
          return;
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let done = false;
        while (!done) {
          const {value, done: doneReading} = await reader.read();
          done = doneReading;
          if (value) {
            const chunk = decoder.decode(value);
            document.getElementById("output").textContent += chunk;
          }
        }
      } catch (err) {
        document.getElementById("output").textContent = "Error: " + err;
      } finally {
        document.getElementById("generateLoading").style.display = 'none';
      }
    });
    
    // Initial load
    fetchModels();
  </script>
</body>
</html>
"""

@app.route("/models", methods=["GET"])
def get_models():
    """Endpoint to get available OpenAI models."""
    try:
        sort_by = request.args.get("sort_by", "created")
        generation = request.args.get("generation")
        capability = request.args.get("capability")
        
        if generation == "none":
            generation = None
            
        # Initialize OpenAIChat
        api_key = os.getenv("OPENAI_API_KEY", DEFAULT_API_KEY)
        if not api_key:
            return "API key not set", 500
            
        chat = OpenAIChat(api_key)
        
        # Get models with the specified sorting and filtering
        models = chat.list_models(
            sort_by=sort_by,
            page=1,
            page_size=1000,  # Get all models
            generation=generation
        )
        
        # Additional capability filtering if needed
        if capability and capability != "none":
            models = [model for model in models if capability in model["capabilities"]]
        
        return models
        
    except Exception as e:
        return str(e), 500

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/generate", methods=["POST"])
def generate():
    prompt = request.form.get("prompt", "Generate descriptive alt text for the visually impaired for social media")
    model = request.form.get("model", "gpt-4-vision-preview")  # Get selected model
    image_data = None

    if "image" in request.files and request.files["image"].filename:
        image_file = request.files["image"]
        temp_dir = tempfile.gettempdir()
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".png")
        try:
            image_file.save(temp_file.name)
            temp_file.close()
            # Instantiate OpenAIChat and encode the image
            api_key = os.getenv("OPENAI_API_KEY", DEFAULT_API_KEY)
            chat = OpenAIChat(api_key)
            image_data = chat.encode_image(temp_file.name)
        except Exception as e:
            return f"Error processing image: {str(e)}", 500
        finally:
            try:
                os.remove(temp_file.name)
            except Exception as cleanup_error:
                print(f"Error cleaning up temporary file: {cleanup_error}", file=sys.stderr)
    
    api_key = os.getenv("OPENAI_API_KEY", DEFAULT_API_KEY)
    chat = OpenAIChat(api_key)

    def generate_response():
        try:
            for chunk in chat.stream_chat_response(prompt, model=model, image_data=image_data):
                yield chunk
        except Exception as e:
            yield f"\nError: {str(e)}"

    return Response(generate_response(), mimetype="text/plain")

# -------------------------------------------------------------------
# Entry Point
# -------------------------------------------------------------------

if __name__ == "__main__":
    # To run CLI interface, call main_cli()
    # Uncomment the following line to test in terminal:
    # main_cli()
    # To run the Flask web server, simply run this file:
    app.run(debug=True, port=6003)