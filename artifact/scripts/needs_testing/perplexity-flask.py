from flask import Flask, render_template_string, request, Response, stream_with_context
import requests
import json
import sys
import asyncio
from typing import AsyncGenerator, Optional, Dict, Any
import markdown
import logging

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"  # replace with a secure key in production

# --- PerplexityChat implementation ---
class PerplexityChat:
    MODELS = {
        "sonar-reasoning-pro": {
            "id": "sonar-reasoning-pro",
            "context_length": 127000,
            "description": "Sonar model optimized for reasoning tasks"
        },
        "sonar-reasoning": {
            "id": "sonar-reasoning",
            "context_length": 127000,
            "description": "Sonar model with reasoning capabilities"
        },
        "sonar-pro": {
            "id": "sonar-pro",
            "context_length": 200000,
            "description": "Sonar model with extended context"
        },
        "sonar": {
            "id": "sonar",
            "context_length": 127000,
            "description": "Base Sonar model"
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
    
    def list_models(self):
        """Return a list of available models."""
        return [
            {
                "id": model_id,
                "name": model_id,
                "context_length": info["context_length"],
                "description": info["description"]
            }
            for model_id, info in self.MODELS.items()
        ]

    def stream_chat_response(self, message: str, model: str = "sonar", temperature: float = 0.7):
        """
        Stream a chat response from Perplexity.
        
        Yields chunks of response text as they arrive.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Append user message to history
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

        full_response = ""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        line_text = line.decode('utf-8')
                        if line_text.startswith("data: "):
                            line_text = line_text[6:]  # remove "data: " prefix
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
            
            # Append assistant's response to history
            self.chat_history.append({
                "role": "assistant",
                "content": full_response
            })

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            # On error, remove the user message
            self.chat_history.pop()
            yield "Error: Unable to get response from API."
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            self.chat_history.pop()
            yield "Error: An unexpected error occurred."

    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]

# --- Global PerplexityChat instance ---
# NOTE: In a production multi-user environment, you'd want to manage per-user conversation state.
API_KEY = "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"  # replace with your actual API key
chat_client = PerplexityChat(API_KEY)

# --- Flask Routes ---

# HTML template for the chat UX
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Streaming Chat with Perplexity API</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    #chat-container { border: 1px solid #ccc; padding: 10px; height: 400px; overflow-y: auto; }
    .message { margin: 5px 0; }
    .user { color: blue; }
    .assistant { color: green; }
    #controls { margin-top: 10px; }
    select, input[type="text"] { padding: 5px; }
    button { padding: 5px 10px; }
  </style>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
  <h2>Streaming Chat with Perplexity API</h2>
  <div>
    <label for="model">Choose a model:</label>
    <select id="model">
      {% for m in models %}
        <option value="{{ m.id }}">{{ m.name }} - {{ m.description }} ({{ m.context_length }} tokens)</option>
      {% endfor %}
    </select>
  </div>
  <div id="chat-container"></div>
  <div id="controls">
    <form id="chatForm">
      <input type="text" id="message" placeholder="Enter your message" size="60" required>
      <button type="submit">Send</button>
      <button type="button" id="clearBtn">Clear Conversation</button>
    </form>
  </div>
  
  <script>
    const chatContainer = document.getElementById("chat-container");

    function appendMessage(sender, text, newline = true) {
      const msgDiv = document.createElement("div");
      msgDiv.classList.add("message");
      msgDiv.classList.add(sender.toLowerCase());
      msgDiv.innerHTML = "<strong>" + sender + ":</strong> " + text + (newline ? "<br>" : "");
      chatContainer.appendChild(msgDiv);
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    document.getElementById("chatForm").addEventListener("submit", async function(e) {
      e.preventDefault();
      const messageInput = document.getElementById("message");
      const modelSelect = document.getElementById("model");
      const message = messageInput.value.trim();
      if (!message) return;
      appendMessage("You", message);
      messageInput.value = "";
      
      try {
        const response = await fetch("/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            message: message,
            model: modelSelect.value
          })
        });
        
        if (!response.ok) {
          appendMessage("Assistant", "Error: " + response.statusText);
          return;
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let done = false;
        while (!done) {
          const { value, done: doneReading } = await reader.read();
          done = doneReading;
          const chunk = decoder.decode(value);
          if (chunk) {
            appendMessage("Assistant", chunk, false);
          }
        }
      } catch (err) {
        appendMessage("Assistant", "Error: " + err);
      }
    });

    // Clear conversation button (reloads the page)
    document.getElementById("clearBtn").addEventListener("click", function() {
      fetch("/clear", { method: "POST" }).then(() => {
        chatContainer.innerHTML = "";
      });
    });
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
async def index():
    dark_mode_template = INDEX_HTML.replace(
        "<style>",
        """<style>
            :root {
                --bg-color: #1a1a1a;
                --text-color: #e0e0e0;
                --border-color: #333;
                --card-bg: #242424;
                --card-hover: #2a2a2a;
                --selected-bg: #1e3a5f;
                --button-bg: #2196f3;
                --button-hover: #1976d2;
                --tag-bg: #333;
                --error-color: #ff6b6b;
            }
            
            body { 
                background-color: var(--bg-color);
                color: var(--text-color);
            }
            
            .model-card {
                background-color: var(--card-bg);
                border-color: var(--border-color);
            }
            
            .model-card:hover {
                background-color: var(--card-hover);
            }
            
            .model-card.selected {
                background-color: var(--selected-bg);
                border-color: var(--button-bg);
            }
            
            .capability-tag {
                background: var(--tag-bg);
                color: var(--text-color);
            }
            
            button {
                background: var(--button-bg);
            }
            
            button:hover {
                background: var(--button-hover);
            }
            
            select, input, textarea {
                background-color: var(--card-bg);
                color: var(--text-color);
                border: 1px solid var(--border-color);
                padding: 0.5rem;
                border-radius: 4px;
            }
            
            .chat-history {
                background-color: var(--card-bg);
                border-color: var(--border-color);
            }
            
            .chat-message.user {
                background-color: var(--selected-bg);
            }
            
            .chat-message.assistant {
                background-color: var(--card-hover);
            }
            
            #modelError {
                color: var(--error-color);
            }
            
            .provider-selector, .mode-selector {
                background-color: var(--card-bg);
            }
            
            .provider-btn, .mode-btn {
                background-color: var(--card-bg);
                color: var(--text-color);
            }
            
            .provider-btn.active, .mode-btn.active {
                background-color: var(--selected-bg);
                border-color: var(--button-bg);
            }
        """
    )
    models = chat_client.list_models()
    return await render_template_string(dark_mode_template, models=models)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return "No message provided", 400
    message = data["message"]
    model = data.get("model", "sonar")
    
    def generate():
        # Stream the response from the API and yield text chunks
        for chunk in chat_client.stream_chat_response(message, model=model):
            yield chunk

    return Response(stream_with_context(generate()), mimetype="text/plain")

@app.route("/clear", methods=["POST"])
def clear():
    chat_client.clear_conversation()
    return "Conversation cleared", 200

async def stream_response(provider: str, prompt: str, model: str, image_path: Optional[str] = None, image_data: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Stream response from any provider with consistent handling."""
    try:
        response_text = ""
        if provider == "anthropic":
            async for chunk in anthropic_client.stream_chat_response(prompt, model=model, image_path=image_path):
                if isinstance(chunk, dict):
                    content = chunk.get('content', '')
                else:
                    content = str(chunk)
                response_text += content
                yield content
                
        elif provider == "openai":
            for chunk in openai_client.stream_chat_response(prompt, model=model, image_data=image_data):
                if isinstance(chunk, dict):
                    content = chunk.get('content', '')
                else:
                    content = str(chunk)
                response_text += content
                yield content
                await asyncio.sleep(0)
                
        elif provider == "perplexity":
            for chunk in perplexity_client.stream_chat_response(prompt, model=model):
                if isinstance(chunk, dict):
                    content = chunk.get('content', '')
                else:
                    content = str(chunk)
                # Convert markdown to HTML for display
                content = markdown.markdown(content)
                response_text += content
                yield content
                await asyncio.sleep(0)
                
        elif provider == "mistral":
            for chunk in mistral_client.stream_chat_response(prompt, model=model):
                if isinstance(chunk, dict):
                    content = chunk.get('content', '')
                else:
                    content = str(chunk)
                response_text += content
                yield content
                await asyncio.sleep(0)
                
        else:  # ollama
            for chunk in ollama_client.stream_chat_response(prompt, model=model, image_data=image_data):
                if isinstance(chunk, dict):
                    content = chunk.get('response', chunk.get('content', ''))
                else:
                    content = str(chunk)
                response_text += content
                yield content
                await asyncio.sleep(0)
                
    except Exception as e:
        logger.error(f"Error in {provider} stream: {str(e)}")
        yield f"\nError: {str(e)}"

if __name__ == "__main__":
    # Run the Flask app in debug mode.
    app.run(debug=True)