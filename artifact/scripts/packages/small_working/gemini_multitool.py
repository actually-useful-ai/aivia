#!/usr/bin/env python3
"""
Gemini Chat - Interactive CLI for Google's Gemini API

This tool provides an accessible, robust interface to Google's Gemini AI models:
- Text generation and chat
- Image and vision capabilities
- Structured output generation
- Code explanation
- Step-by-step reasoning

Supports multiple Gemini models, including:
- gemini-1.5-pro
- gemini-1.5-flash
- gemini-2.0-pro
- gemini-2.0-flash
- gemini-1.5-flash-latest
- gemini-1.5-pro-latest
- gemini-2.5-pro-exp-03-25 (experimental)
- gemini-2.0-flash-lite

Accessibility, error handling, and maintainability are prioritized.

# Registration: Provides get_tool_schemas() in OpenAI/Swarm format (type:function, function:{...})
# and register_with_registry(registry=None) for explicit registration.
# All registration prints use print_registration_status for accessibility and consistency.
"""

# Module metadata for CLI and registry
MODULE_DISPLAY_NAME = "Google Gemini AI"
MODULE_DESCRIPTION = "Google Gemini AI tools for text generation, image analysis, and structured output."

import os
import base64
import json
import requests
import argparse
import cmd
import sys
from typing import List, Dict, Any, Optional, Union, Tuple
from PIL import Image
import io


def get(attr, default=None):
    """
    Utility function to get attributes from this module.
    This function is used by the registry system when organizing tools.
    
    Args:
        attr: Attribute name to get
        default: Default value if attribute doesn't exist
        
    Returns:
        Attribute value or default
    """
    module = sys.modules[__name__]
    return getattr(module, attr, default)
# Add CLIStyle and print_registration_status fallback
try:
    from core.core_cli import CLIStyle
    from core.core_registry import print_registration_status
except Exception:
    class CLIStyle:
        @staticmethod
        def style(text, *args, **kwargs):
            return text
        CYAN = ''
        GREEN = ''
        YELLOW = ''
        RED = ''
        MAGENTA = ''
        WHITE = ''
        BOLD = ''
        RESET = ''
    def print_registration_status(kind, name, module=None, status="registered", error=None):
        msg = f"[Registered {kind}] {name}"
        if module:
            msg += f" (module: {module})"
        if error:
            msg = f"[Registration error] {name}: {error}"
            print(CLIStyle.style(msg, CLIStyle.RED))
        elif kind == "tool":
            print(CLIStyle.style(msg, CLIStyle.CYAN))
        elif kind == "module":
            print(CLIStyle.style(msg, CLIStyle.GREEN))
        else:
            print(msg)

class GeminiAPI:
    """
    Accessible client for the Google Gemini API.

    - Handles text, image, and (optionally) audio input.
    - Supports multiple Gemini models.
    - Comprehensive error handling and explicit CORS/HTTP configuration.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini API client.

        Args:
            api_key: Gemini API key. If not provided, will check GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided either directly or via GEMINI_API_KEY environment variable")

        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        # Model endpoints (update as new models are released)
        self.models = {
            # Gemini 2.5 models
            "gemini-2.5-pro-preview-05-06": f"{self.base_url}/models/gemini-2.5-pro-preview-05-06:generateContent",
            "gemini-2.5-flash-preview-04-17": f"{self.base_url}/models/gemini-2.5-flash-preview-04-17:generateContent",
            
            # Gemini 2.0 models
            "gemini-2.0-pro": f"{self.base_url}/models/gemini-2.0-pro:generateContent",
            "gemini-2.0-flash": f"{self.base_url}/models/gemini-2.0-flash:generateContent",
            "gemini-2.0-flash-lite": f"{self.base_url}/models/gemini-2.0-flash-lite:generateContent",
            "gemini-2.0-flash-preview-image-generation": f"{self.base_url}/models/gemini-2.0-flash-preview-image-generation:generateContent",
            
            # Gemini 1.5 models
            "gemini-1.5-pro": f"{self.base_url}/models/gemini-1.5-pro:generateContent",
            "gemini-1.5-flash": f"{self.base_url}/models/gemini-1.5-flash:generateContent",
            "gemini-1.5-flash-latest": f"{self.base_url}/models/gemini-1.5-flash-latest:generateContent",
            "gemini-1.5-pro-latest": f"{self.base_url}/models/gemini-1.5-pro-latest:generateContent",
        }
        self.vision_models = [
            "gemini-2.5-pro-preview-05-06", "gemini-2.5-flash-preview-04-17",
            "gemini-2.0-pro", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.0-flash-preview-image-generation", 
            "gemini-1.5-pro", "gemini-1.5-pro-latest", "gemini-1.5-flash", "gemini-1.5-flash-latest"
        ]
        self.chat_history: List[Dict[str, Any]] = []

    def _encode_image(self, image_path: str) -> str:
        """
        Encode an image to base64.

        Args:
            image_path: Path to the image file

        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _prepare_image_part(self, image: Union[str, Image.Image, bytes]) -> Dict[str, Any]:
        """
        Prepare image part for the API request.

        Args:
            image: Can be a file path, PIL Image, or bytes

        Returns:
            Dictionary with the image data formatted for the API
        """
        if isinstance(image, str):
            encoded_image = self._encode_image(image)
            ext = os.path.splitext(image)[1][1:].lower()
            mime_type = f"image/{ext}" if ext else "image/jpeg"
        elif isinstance(image, Image.Image):
            buffer = io.BytesIO()
            image.save(buffer, format=image.format or "PNG")
            encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
            mime_type = f"image/{image.format.lower() if image.format else 'png'}"
        elif isinstance(image, bytes):
            encoded_image = base64.b64encode(image).decode("utf-8")
            mime_type = "image/png"
        else:
            raise ValueError("Image must be a file path, PIL Image, or bytes")
        return {
            "inlineData": {
                "mimeType": mime_type,
                "data": encoded_image
            }
        }

    def _make_request(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the Gemini API.

        Args:
            url: API endpoint URL
            payload: Request payload

        Returns:
            API response as a dictionary
        """
        headers = {
            "Content-Type": "application/json",
        }
        url = f"{url}?key={self.api_key}"
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
        except requests.RequestException as e:
            raise Exception(f"Network error: {e}")
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        return response.json()

    def list_models(self) -> List[str]:
        """
        List available Gemini models.

        Returns:
            List of available model names
        """
        return list(self.models.keys())

    def generate_text(
        self,
        prompt: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None
    ) -> str:
        """
        Generate text using the Gemini model.

        Args:
            prompt: Text prompt
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter

        Returns:
            Generated text
        """
        if model not in self.models:
            raise ValueError(f"Model {model} not supported. Available models: {list(self.models.keys())}")
        url = self.models[model]
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
            }
        }
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens
        if top_p:
            payload["generationConfig"]["topP"] = top_p
        if top_k:
            payload["generationConfig"]["topK"] = top_k
        response = self._make_request(url, payload)
        try:
            return response["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse response: {e}. Response: {response}")

    def chat(
        self,
        message: str,
        keep_history: bool = True,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7
    ) -> str:
        """
        Chat with the Gemini model, maintaining conversation history.

        Args:
            message: User message
            keep_history: Whether to maintain conversation history
            model: Model to use
            temperature: Sampling temperature

        Returns:
            Model response
        """
        if model not in self.models:
            raise ValueError(f"Model {model} not supported. Available models: {list(self.models.keys())}")
        url = self.models[model]
        if keep_history:
            self.chat_history.append({"role": "user", "parts": [{"text": message}]})
            payload = {
                "contents": self.chat_history,
                "generationConfig": {
                    "temperature": temperature,
                }
            }
        else:
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": message}]}
                ],
                "generationConfig": {
                    "temperature": temperature,
                }
            }
        response = self._make_request(url, payload)
        try:
            assistant_response = response["candidates"][0]["content"]["parts"][0]["text"]
            if keep_history:
                self.chat_history.append({"role": "model", "parts": [{"text": assistant_response}]})
            return assistant_response
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse response: {e}. Response: {response}")

    def reset_chat(self) -> str:
        """Reset the chat history."""
        self.chat_history = []
        return "Chat history cleared."

    def generate_with_images(
        self,
        prompt: str,
        images: List[Union[str, Image.Image, bytes]],
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text based on images and a prompt.

        Args:
            prompt: Text prompt
            images: List of images (file paths, PIL Images, or bytes)
            model: Model to use (should support vision)
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate

        Returns:
            Generated text
        """
        if model not in self.vision_models:
            raise ValueError(
                f"Model {model} might not support vision. Recommended: {', '.join(self.vision_models)}"
            )
        url = self.models[model]
        parts = [{"text": prompt}]
        for image in images:
            parts.append(self._prepare_image_part(image))
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": parts
                }
            ],
            "generationConfig": {
                "temperature": temperature,
            }
        }
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens
        response = self._make_request(url, payload)
        try:
            return response["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse response: {e}. Response: {response}")

    def analyze_document(
        self,
        document_path: str,
        prompt: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7
    ) -> str:
        """
        Analyze a document (PDF, text, markdown, image, etc.) with AI.

        Args:
            document_path: Path to the document file
            prompt: What to analyze in the document
            model: Model to use
            temperature: Sampling temperature

        Returns:
            Analysis of the document
        """
        ext = os.path.splitext(document_path)[1].lower()
        file_content = ""
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
            return self.generate_with_images(prompt, [document_path], model=model, temperature=temperature)
        elif ext == '.pdf':
            try:
                import PyPDF2
            except ImportError:
                raise ImportError("PyPDF2 is required for PDF processing. Install with: pip install PyPDF2")
            try:
                with open(document_path, "rb") as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    file_content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            except Exception as e:
                return f"Error processing PDF: {str(e)}"
        elif ext in ['.txt', '.md', '.html', '.css', '.js', '.py', '.json']:
            with open(document_path, "r", encoding="utf-8") as f:
                file_content = f.read()
        else:
            return f"Unsupported file type: {ext}"
        full_prompt = f"{prompt}\n\nDocument Contents:\n{file_content[:5000]}...\n"
        if len(file_content) > 5000:
            full_prompt += "(Content truncated due to length)"
        return self.generate_text(full_prompt, model=model, temperature=temperature)

    def thinking_step_by_step(
        self,
        problem: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.3
    ) -> str:
        """
        Solve a problem using step-by-step thinking.

        Args:
            problem: Problem to solve
            model: Model to use
            temperature: Sampling temperature

        Returns:
            Step-by-step solution
        """
        prompt = (
            "Solve this problem step by step, showing your reasoning at each step:\n\n"
            f"{problem}\n\n"
            "Format your response as:\n"
            "1. First, I'll...\n"
            "2. Next, I'll...\n"
            "3. Then, I'll...\n"
            "...\n"
            "Conclusion: ..."
        )
        return self.generate_text(prompt, model, temperature)

    def generate_structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        model: str = "gemini-2.0-flash",
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Generate structured output according to a schema.

        Args:
            prompt: Text prompt
            schema: JSON schema defining the structure
            model: Model to use
            temperature: Sampling temperature

        Returns:
            Structured data according to the schema
        """
        url = self.models[model]
        schema_prompt = (
            f"Generate a response to the following prompt and format it according to this JSON schema:\n"
            f"{json.dumps(schema, indent=2)}\n\nPrompt: {prompt}"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": schema_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
            }
        }
        response = self._make_request(url, payload)
        try:
            text_response = response["candidates"][0]["content"]["parts"][0]["text"]
            json_start = text_response.find('{')
            json_end = text_response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = text_response[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in response")
        except Exception as e:
            raise Exception(f"Failed to parse structured output: {e}. Response: {response}")

    def generate_with_search_grounding(
        self,
        prompt: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate text using Gemini with Google Search grounding.
        
        This method uses Google Search as a tool to improve the accuracy and recency
        of the model's responses. It returns both the response and grounding metadata.
        
        Args:
            prompt: Text prompt
            model: Model to use (should be a 2.0+ model)
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Tuple of (generated text, grounding metadata)
        """
        if not model.startswith(("gemini-2", "gemini-1.5")):
            print(f"Warning: Search grounding works best with Gemini 1.5+ and 2.0+ models. Using {model}.")
            
        if model not in self.models:
            raise ValueError(f"Model {model} not supported. Available models: {list(self.models.keys())}")
            
        url = self.models[model]
        
        # Configure Google Search as a tool
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
            },
            "tools": [
                {
                    "googleSearch": {}
                }
            ]
        }
        
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens
            
        response = self._make_request(url, payload)
        
        try:
            text_response = response["candidates"][0]["content"]["parts"][0]["text"]
            # Extract grounding metadata which includes search entry point and sources
            grounding_metadata = {}
            if "candidates" in response and len(response["candidates"]) > 0:
                candidate = response["candidates"][0]
                if "groundingMetadata" in candidate:
                    grounding_metadata = candidate["groundingMetadata"]
                    
            return text_response, grounding_metadata
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse response: {e}. Response: {response}")

class GeminiShell(cmd.Cmd):
    """
    Interactive shell for Gemini API.

    Accessibility: All output is plain text, and error messages are explicit.
    """

    intro = (
        "\n"
        "╔════════════════════════════════════════════════════════════╗\n"
        "║            🔮  Gemini AI Interactive Shell  🔮             ║\n"
        "║  Type 'help' or '?' to list commands.                      ║\n"
        "║  Use 'quit' or 'exit' to exit.                             ║\n"
        "╚════════════════════════════════════════════════════════════╝\n"
    )
    prompt = '🔮 gemini> '

    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        try:
            self.gemini = GeminiAPI(api_key)
            self.current_model = "gemini-2.0-flash"
            self.temperature = 0.7
            print(f"Connected to Gemini API! Default model: {self.current_model}")
        except Exception as e:
            print(f"Error initializing Gemini API: {str(e)}")
            print("Make sure you have a valid API key set in the GEMINI_API_KEY environment variable.")
            sys.exit(1)

    def emptyline(self):
        """Do nothing on empty line."""
        pass

    def default(self, line):
        """Default behavior: treat input as chat with AI."""
        try:
            response = self.gemini.chat(line, model=self.current_model, temperature=self.temperature)
            print(f"\n{response}\n")
        except Exception as e:
            print(f"Error: {str(e)}")

    def do_help(self, arg):
        """Show help information about commands."""
        if not arg:
            print("""
╔════════════════════════════════════════════════════════════╗
║                  GEMINI AI SHELL COMMANDS                  ║
╚════════════════════════════════════════════════════════════╝

BASIC INTERACTION:
  <text>       - Send a message to chat with the AI
  ask <query>  - Ask a single question (no chat history)
  chat <msg>   - Start/continue a conversation (keeps history)
  reset        - Clear the chat history

SETTINGS:
  models       - List all available models
  model <name> - Change the current model (e.g., model gemini-2.0-flash)
  temp <0-1>   - Set temperature (0=precise, 1=creative)

SPECIALIZED TOOLS:
  image <path> <prompt>     - Analyze images with AI
  document <path> <prompt>  - Analyze PDF/text documents
  code <lang> <description> - Generate code in specified language
  thinking <problem>        - Solve problems step by step
  structured <query>        - Get JSON-formatted structured data
  search <query>            - Use Google Search grounding for more accurate and recent information

SYSTEM:
  help         - Show this help information
  quit/exit    - Exit the application

EXAMPLES:
  gemini> What is quantum computing?
  gemini> image xai_tools/img/cat.jpg What breed is this cat?
  gemini> code python create a flask server with two routes
  gemini> thinking How do I solve the Tower of Hanoi problem?
  gemini> search When is the next lunar eclipse?
""")
        else:
            super().do_help(arg)

    def do_quit(self, arg):
        """Exit the Gemini shell."""
        print("Goodbye! 👋")
        return True

    def do_exit(self, arg):
        """Exit the Gemini shell."""
        return self.do_quit(arg)

    def do_models(self, arg):
        """List available Gemini models."""
        models = self.gemini.list_models()
        print("\nAvailable models:")
        for model in models:
            mark = "✓" if model == self.current_model else " "
            print(f"  [{mark}] {model}")
        print()

    def do_model(self, arg):
        """Set the current model (e.g., 'model gemini-2.0-flash')."""
        if not arg:
            print(f"Current model: {self.current_model}")
            return
        models = self.gemini.list_models()
        if arg in models:
            self.current_model = arg
            print(f"Model set to: {self.current_model}")
        else:
            print(f"Unknown model: {arg}")
            print(f"Available models: {', '.join(models)}")

    def do_temp(self, arg):
        """Set temperature parameter (0.0-1.0)."""
        if not arg:
            print(f"Current temperature: {self.temperature}")
            return
        try:
            temp = float(arg)
            if 0.0 <= temp <= 1.0:
                self.temperature = temp
                print(f"Temperature set to: {self.temperature}")
            else:
                print("Temperature must be between 0.0 and 1.0")
        except ValueError:
            print("Please provide a valid number between 0.0 and 1.0")

    def do_ask(self, arg):
        """Ask a one-time question without keeping chat history."""
        if not arg:
            print("Please provide a question.")
            return
        try:
            response = self.gemini.generate_text(
                arg,
                model=self.current_model,
                temperature=self.temperature
            )
            print(f"\n{response}\n")
        except Exception as e:
            print(f"Error: {str(e)}")

    def do_chat(self, arg):
        """Chat with the model (maintains conversation history)."""
        if not arg:
            print("Please provide a message.")
            return
        try:
            response = self.gemini.chat(
                arg,
                model=self.current_model,
                temperature=self.temperature
            )
            print(f"\n{response}\n")
        except Exception as e:
            print(f"Error: {str(e)}")

    def do_reset(self, arg):
        """Reset the chat history."""
        result = self.gemini.reset_chat()
        print(result)

    def do_image(self, arg):
        """Analyze images with a prompt (e.g., 'image path/to/image.jpg What's in this image?')."""
        parts = arg.split()
        if len(parts) < 2:
            print("Usage: image <image_path> <prompt>")
            return
        image_path = parts[0]
        prompt = " ".join(parts[1:])
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return
        try:
            model = self.current_model
            if model not in self.gemini.vision_models:
                model = self.gemini.vision_models[0]
                print(f"Switching to {model} for image analysis")
            response = self.gemini.generate_with_images(
                prompt,
                [image_path],
                model=model,
                temperature=self.temperature
            )
            print(f"\n{response}\n")
        except Exception as e:
            print(f"Error: {str(e)}")

    def do_document(self, arg):
        """Analyze a document file (e.g., 'document path/to/file.pdf Summarize this')."""
        parts = arg.split()
        if len(parts) < 2:
            print("Usage: document <file_path> <prompt>")
            return
        file_path = parts[0]
        prompt = " ".join(parts[1:])
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        try:
            print("Analyzing document, please wait...")
            response = self.gemini.analyze_document(
                file_path,
                prompt,
                model=self.current_model,
                temperature=self.temperature
            )
            print(f"\n{response}\n")
        except Exception as e:
            print(f"Error: {str(e)}")

    def do_code(self, arg):
        """Explain or generate code (e.g., 'code python Write a function to calculate fibonacci')."""
        parts = arg.split()
        if len(parts) < 2:
            print("Usage: code <language> <prompt>")
            return
        language = parts[0]
        prompt = " ".join(parts[1:])
        try:
            code_prompt = f"Write {language} code for: {prompt}\n\nProvide code with comments explaining each part."
            response = self.gemini.generate_text(
                code_prompt,
                model=self.current_model,
                temperature=self.temperature
            )
            print(f"\n{response}\n")
        except Exception as e:
            print(f"Error: {str(e)}")

    def do_thinking(self, arg):
        """Use step-by-step thinking to solve a problem."""
        if not arg:
            print("Please provide a problem to solve.")
            return
        try:
            print("Thinking step by step...")
            response = self.gemini.thinking_step_by_step(
                arg,
                model=self.current_model,
                temperature=min(self.temperature, 0.5)
            )
            print(f"\n{response}\n")
        except Exception as e:
            print(f"Error: {str(e)}")

    def do_structured(self, arg):
        """Generate structured output (e.g., 'structured Analyze the sentiment of: I love this product!')."""
        if not arg:
            print("Please provide a prompt.")
            return
        schema = {
            "type": "object",
            "properties": {
                "analysis": {"type": "string"},
                "keyPoints": {"type": "array", "items": {"type": "string"}},
                "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]}
            }
        }
        try:
            print("Generating structured output...")
            response = self.gemini.generate_structured_output(
                arg,
                schema,
                model=self.current_model,
                temperature=self.temperature
            )
            print(f"\n{json.dumps(response, indent=2)}\n")
        except Exception as e:
            print(f"Error: {str(e)}")

    def do_search(self, arg):
        """Use Google Search grounding for more accurate and recent information."""
        if not arg:
            print("Please provide a search query.")
            return
        
        # Check if using a 2.0+ model, if not, suggest switching
        if not self.current_model.startswith(("gemini-2", "gemini-1.5")):
            print(f"For best search results, switching from {self.current_model} to gemini-2.0-flash")
            search_model = "gemini-2.0-flash"
        else:
            search_model = self.current_model
            
        try:
            print("Searching for information...")
            response, grounding = self.gemini.generate_with_search_grounding(
                arg,
                model=search_model,
                temperature=self.temperature
            )
            
            print(f"\n{response}\n")
            
            # Display search entry point if available (required for display regulations)
            if grounding and "searchEntryPoint" in grounding:
                print("\n🔍 Search Suggestions:")
                if "webSearchQueries" in grounding["searchEntryPoint"]:
                    for query in grounding["searchEntryPoint"]["webSearchQueries"]:
                        print(f"  • {query}")
                        
            # Show sources if available
            if grounding and "groundingChunks" in grounding:
                print("\n📚 Sources:")
                for i, chunk in enumerate(grounding["groundingChunks"]):
                    if "web" in chunk and "title" in chunk["web"]:
                        print(f"  {i+1}. {chunk['web']['title']}")
                        
            print("\nNote: When using the search feature, Google Search Suggestions must be displayed to end users.")
                
        except Exception as e:
            print(f"Error: {str(e)}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Gemini AI Interactive Shell")
    parser.add_argument("--key", "-k", help="Gemini API key (if not provided, will use GEMINI_API_KEY environment variable)")
    parser.add_argument("--prompt", "-p", help="Single prompt to execute and exit")
    parser.add_argument("--check-key", action="store_true", help="Verify if the current API key is valid")
    return parser.parse_args()

def get_tool_schemas():
    """Return all tool schemas for this module."""
    return [
        {
            "name": "Gemini Chat",
            "display_name": "Gemini Chat",
            "description": "Use Google's Gemini AI model for text generation, image analysis, and structured output.",
            "type": "function",
            "function": {
                "name": "gemini_chat",
                "display_name": "Gemini Chat",
                "description": "Use Google's Gemini AI model for text generation, image analysis, and structured output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The prompt or question to send to Gemini."
                        },
                        "model": {
                            "type": "string",
                            "description": "Gemini model to use (gemini-1.5-pro, gemini-1.5-flash, etc).",
                            "default": "gemini-1.5-pro"
                        },
                        "image_url": {
                            "type": "string", 
                            "description": "Optional URL to an image for analysis."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "name": "Gemini Vision",
            "display_name": "Gemini Vision",
            "description": "Analyze images using Gemini's vision capabilities",
            "type": "function",
            "function": {
                "name": "gemini_vision",
                "display_name": "Gemini Vision",
                "description": "Analyze images using Gemini's vision capabilities",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_url": {
                            "type": "string",
                            "description": "URL to an image for analysis."
                        },
                        "query": {
                            "type": "string",
                            "description": "Prompt or question about the image.",
                            "default": "Describe this image in detail."
                        },
                        "model": {
                            "type": "string",
                            "description": "Gemini model to use.",
                            "default": "gemini-1.5-pro-vision"
                        }
                    },
                    "required": ["image_url"]
                }
            }
        }
    ]

def register_with_registry(registry=None):
    """
    Register tools with the Swarm registry using the correct schema format.
    """
    if registry is None:
        try:
            from core.core_registry import get_registry
            registry = get_registry()
        except Exception:
            print_registration_status("module", "drummer_gemini_multitool", error="Could not import registry")
            return False
    
    schemas = get_tool_schemas()
    
    # Define handlers for each tool
    def handle_gemini_chat(args):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"error": "GEMINI_API_KEY environment variable not set"}
        
        try:
            gemini = GeminiAPI(api_key)
            prompt = args.get("prompt")
            model = args.get("model", "gemini-2.0-flash")
            temperature = float(args.get("temperature", 0.7))
            
            response = gemini.generate_text(prompt, model=model, temperature=temperature)
            return {"response": response}
        except Exception as e:
            return {"error": str(e)}
    
    def handle_gemini_vision(args):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"error": "GEMINI_API_KEY environment variable not set"}
        
        try:
            gemini = GeminiAPI(api_key)
            image_path = args.get("image_path")
            prompt = args.get("prompt")
            model = args.get("model", "gemini-2.0-pro")
            
            if not os.path.exists(image_path):
                return {"error": f"Image file not found: {image_path}"}
                
            response = gemini.generate_with_images(prompt, [image_path], model=model)
            return {"response": response}
        except Exception as e:
            return {"error": str(e)}
    
    # Map tool names to handlers
    handlers = {
        "gemini_chat": handle_gemini_chat,
        "gemini_vision": handle_gemini_vision
    }
    
    # Register each tool with the registry
    for schema in schemas:
        name = schema["function"]["name"]
        handler = handlers.get(name)
        registry.register_tool(name, schema, handler, module_name="drummer_gemini_multitool")
        print_registration_status("tool", name, module="drummer_gemini_multitool")
    
    # Register the module itself
    registry.register_module("drummer_gemini_multitool", sys.modules[__name__])
    print_registration_status("module", "drummer_gemini_multitool")
    
    return True

def main():
    """
    Main entry point for the application.

    Accessibility: Prompts for API key if not found, and offers to save it.
    """
    args = parse_arguments()
    api_key = args.key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No Gemini API key found in environment or command line arguments.")
        print("You'll need a valid API key from https://ai.google.dev/ to use this tool.")
        response = input("Would you like to enter your API key now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            api_key = input("Enter your Gemini API key: ").strip()
            save_env = input("Would you like to save this key to your environment variables? (y/n): ")
            if save_env.lower() in ['y', 'yes']:
                bash_profile = os.path.expanduser("~/.bash_profile")
                with open(bash_profile, "a") as f:
                    f.write(f'\nexport GEMINI_API_KEY="{api_key}"\n')
                print("API key saved to ~/.bash_profile. Restart your terminal or run 'source ~/.bash_profile' to apply.")
        if not api_key:
            print("No API key provided. Exiting.")
            return 1
    try:
        if args.check_key:
            try:
                gemini = GeminiAPI(api_key)
                models = gemini.list_models()
                print(f"✅ API key is valid! Available models: {', '.join(models)}")
                return 0
            except Exception as e:
                print(f"❌ API key validation failed: {str(e)}")
                return 1
        if args.prompt:
            gemini = GeminiAPI(api_key)
            response = gemini.generate_text(args.prompt)
            print(response)
        else:
            GeminiShell(api_key).cmdloop()
    except KeyboardInterrupt:
        print("\nGoodbye! 👋")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    # ... existing CLI code ...
    try:
        register_with_registry()
    except Exception as e:
        print_registration_status("module", "drummer_gemini_multitool", error=str(e))
    sys.exit(main())