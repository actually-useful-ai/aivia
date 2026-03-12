import os
import sys
import io
import json
import base64
import requests
from datetime import datetime
from PIL import Image
from flask import Flask, request, Response, render_template_string, stream_with_context

# -------------------------------
# MistralChat API Client
# -------------------------------
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
        page: int = 1,
        page_size: int = 5,
        capability_filter: str = None,
        category_filter: str = None
    ):
        """
        Retrieve available Mistral models with pagination.
        In case of API failure, fallback models are returned.
        """
        try:
            response = requests.get(f"{self.api_url}/models", headers=self.headers)
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
            if sort_by == "created":
                models.sort(key=lambda x: x["created"], reverse=True)
            elif sort_by == "context_length":
                models.sort(key=lambda x: x["context_length"], reverse=True)
            else:
                models.sort(key=lambda x: x["id"], reverse=True)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return models[start_idx:end_idx]
        except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            # Fallback models
            fallback_models = [{
                "id": "mistral-tiny",
                "name": "Mistral Tiny",
                "description": "Mistral Tiny model",
                "context_length": 32768,
                "created_at": "2024-03-01",
                "created": datetime.now().timestamp(),
                "capabilities": ["chat"],
                "category": "mistral",
                "owned_by": "mistralai"
            }, {
                "id": "mistral-small",
                "name": "Mistral Small",
                "description": "Mistral Small model",
                "context_length": 32768,
                "created_at": "2024-03-01",
                "created": datetime.now().timestamp(),
                "capabilities": ["chat", "functions"],
                "category": "mistral",
                "owned_by": "mistralai"
            }, {
                "id": "mistral-medium",
                "name": "Mistral Medium",
                "description": "Mistral Medium model",
                "context_length": 32768,
                "created_at": "2024-03-01",
                "created": datetime.now().timestamp(),
                "capabilities": ["chat", "functions"],
                "category": "mistral",
                "owned_by": "mistralai"
            }]
            if capability_filter:
                fallback_models = [m for m in fallback_models if capability_filter in m["capabilities"]]
            if category_filter:
                fallback_models = [m for m in fallback_models if category_filter == m["category"]]
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return fallback_models[start_idx:end_idx]

    def create_test_image(self, color: str = 'red', size: tuple = (100, 100)):
        """Create a test image and return its base64 encoding."""
        try:
            img = Image.new('RGB', size, color=color)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error creating test image: {e}", file=sys.stderr)
            return None

    def load_image_from_file(self, file_path: str):
        """Load an image from a file and return its base64 encoding."""
        try:
            with Image.open(file_path) as img:
                if img.format not in ['PNG', 'JPEG', 'WEBP', 'GIF']:
                    print(f"Unsupported image format: {img.format}.", file=sys.stderr)
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
                    new_size = (int(img.size[0]*ratio), int(img.size[1]*ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format)
                return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error loading image: {e}", file=sys.stderr)
            return None

    def format_message_with_image(self, message: str, image_data=None, is_url: bool = False):
        """
        Format a message with optional image data.
        If image_data is provided, returns a list of content objects.
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
                content.append({"type": "image_url", "image_url": img})
            else:
                # For base64 encoded images, use data URI format
                content.append({
                    "type": "image_url", 
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img}",
                        "detail": "high"
                    }
                })
        
        print(f"Formatted message with {len(image_data)} images")
        return content

    def format_message_with_file(self, message: str, file_data=None):
        """
        Format a message with optional file data.
        """
        if not file_data:
            return message
        if isinstance(file_data, str):
            file_data = [file_data]
        content = [{"type": "text", "text": message}]
        for file_id in file_data:
            content.append({"type": "file", "file_id": file_id})
        return content

    def stream_chat_response(
        self,
        message: str,
        model: str = "mistral-tiny",
        temperature: float = 0.7,
        max_tokens: int = None,
        top_p: float = 1.0,
        safe_prompt: bool = True,
        image_data=None,
        is_url: bool = False,
        file_data=None
    ):
        """
        Stream a chat response from Mistral.
        """
        try:
            # Format message content based on whether we have images or files
            content = message
            if image_data:
                print(f"Processing message with image data (is_url={is_url})")
                content = self.format_message_with_image(message, image_data, is_url)
            elif file_data:
                print(f"Processing message with file data")
                content = self.format_message_with_file(message, file_data)
            
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": content})
            
            # Prepare API payload
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
            
            # Print debug info
            print(f"Sending request to Mistral API with model: {model}")
            if image_data:
                print(f"Request includes image data")
            
            # Make API request
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=self.headers,
                json=payload,
                stream=True
            )
            
            # Check for HTTP errors
            if response.status_code != 200:
                error_msg = f"API error: {response.status_code} - {response.text}"
                print(error_msg, file=sys.stderr)
                yield f"Error: {error_msg}"
                self.conversation_history.pop()  # Remove the user message if request failed
                return
                
            response.raise_for_status()
            
            # Process streaming response
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
                        content_chunk = data['choices'][0]['delta'].get('content', '')
                        if content_chunk:
                            full_response += content_chunk
                            yield content_chunk
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error processing chunk: {e}", file=sys.stderr)
                        continue
            
            # Add assistant's response to history
            self.conversation_history.append({"role": "assistant", "content": full_response})
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            self.conversation_history.pop()  # Remove the user message if request failed
            yield f"Error: {str(e)}"
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            self.conversation_history.pop()
            yield f"Error: {str(e)}"

    def clear_conversation(self):
        """Clear conversation history (keeping only the system prompt)."""
        self.conversation_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]

    def upload_file(self, file_path: str):
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

    def list_files(self, purpose: str = None):
        try:
            params = {"purpose": purpose} if purpose else {}
            response = requests.get(f"{self.api_url}/files", headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            print(f"Error listing files: {e}", file=sys.stderr)
            return []

    def retrieve_file(self, file_id: str):
        try:
            response = requests.get(f"{self.api_url}/files/{file_id}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error retrieving file: {e}", file=sys.stderr)
            return None

    def delete_file(self, file_id: str):
        try:
            response = requests.delete(f"{self.api_url}/files/{file_id}", headers=self.headers)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}", file=sys.stderr)
            return False

    def get_file_content(self, file_id: str):
        try:
            response = requests.get(f"{self.api_url}/files/{file_id}/content", headers=self.headers)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading file: {e}", file=sys.stderr)
            return None

    def get_file_url(self, file_id: str):
        try:
            response = requests.post(f"{self.api_url}/files/{file_id}/download_url", headers=self.headers)
            response.raise_for_status()
            return response.json()["download_url"]
        except Exception as e:
            print(f"Error getting file URL: {e}", file=sys.stderr)
            return None

    def encode_image(self, file_path: str):
        """
        Encode an image file to base64 for use with the Mistral API.
        
        Args:
            file_path (str): Path to the image file
            
        Returns:
            str: Base64 encoded image data or None if encoding fails
        """
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if dimensions are too large (max 1024x1024)
                if img.size[0] > 1024 or img.size[1] > 1024:
                    ratio = min(1024/img.size[0], 1024/img.size[1])
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Save as JPEG for consistency
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=95)
                img_byte_arr.seek(0)
                
                # Encode to base64
                encoded = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                print(f"Successfully encoded image, length: {len(encoded)}")
                return encoded
        except Exception as e:
            print(f"Error encoding image: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return None

# -------------------------------
# Flask Frontend Application
# -------------------------------
app = Flask(__name__)

# Use your Mistral API key here or set the environment variable "MISTRAL_API_KEY"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "n8R347515VqP48oDHwBeL9BS6nW1L8zY")
chat_client = MistralChat(MISTRAL_API_KEY)

# HTML template (using render_template_string for self-containment)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Mistral Streaming Chat</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    #chat { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: scroll; }
    .message { margin: 5px 0; }
    .user { color: blue; }
    .assistant { color: green; }
  </style>
</head>
<body>
  <h1>Mistral Streaming Chat</h1>
  <div>
    <label for="model">Select Model:</label>
    <select id="model">
      {% for model in models %}
        <option value="{{ model.id }}">{{ model.name }} ({{ model.id }})</option>
      {% endfor %}
    </select>
  </div>
  <div id="chat"></div>
  <form id="chat-form">
    <textarea id="message" rows="3" cols="60" placeholder="Enter your message"></textarea><br>
    <input type="file" id="image" accept="image/*"><br>
    <button type="submit">Send</button>
    <button type="button" id="clear">Clear Chat</button>
  </form>
  
  <script>
    const chatDiv = document.getElementById("chat");
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message");
    const modelSelect = document.getElementById("model");
    const imageInput = document.getElementById("image");
    const clearButton = document.getElementById("clear");

    function appendMessage(sender, text) {
      const msgDiv = document.createElement("div");
      msgDiv.className = "message " + sender;
      msgDiv.textContent = sender + ": " + text;
      chatDiv.appendChild(msgDiv);
      chatDiv.scrollTop = chatDiv.scrollHeight;
    }

    chatForm.addEventListener("submit", function(e) {
      e.preventDefault();
      const message = messageInput.value;
      if (!message) return;
      
      appendMessage("user", message);
      messageInput.value = "";
      
      const model = modelSelect.value;
      const formData = new FormData();
      formData.append("message", message);
      formData.append("model", model);
      if (imageInput.files[0]) {
        formData.append("image", imageInput.files[0]);
      }
      
      fetch("/chat", { method: "POST", body: formData })
      .then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        function read() {
          reader.read().then(({done, value}) => {
            if (done) return;
            const chunk = decoder.decode(value);
            appendMessage("assistant", chunk);
            read();
          });
        }
        read();
      })
      .catch(error => {
        appendMessage("assistant", "Error: " + error);
      });
    });

    clearButton.addEventListener("click", function() {
      fetch("/clear", { method: "POST" })
      .then(() => { chatDiv.innerHTML = ""; });
    });
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    # Get a list of available models (using a larger page size for convenience)
    models = chat_client.list_models(page=1, page_size=100)
    return render_template_string(HTML_TEMPLATE, models=models)

@app.route("/chat", methods=["POST"])
def chat():
    message = request.form.get("message")
    model = request.form.get("model", "mistral-tiny")
    image_file = request.files.get("image")
    image_data = None
    is_url = False
    if image_file:
        try:
            image_bytes = image_file.read()
            # Process image using Pillow
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != "RGB":
                img = img.convert("RGB")
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="PNG")
            image_data = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
        except Exception as e:
            print(f"Error processing uploaded image: {e}", file=sys.stderr)
    
    def generate():
        for chunk in chat_client.stream_chat_response(message, model=model, image_data=image_data, is_url=is_url):
            yield chunk
    return Response(stream_with_context(generate()), mimetype="text/plain")

@app.route("/clear", methods=["POST"])
def clear():
    chat_client.clear_conversation()
    return ("", 204)

if __name__ == "__main__":
    app.run(debug=True, port=5008)