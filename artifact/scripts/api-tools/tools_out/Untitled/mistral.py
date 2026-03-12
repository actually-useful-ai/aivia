from typing import AsyncIterator, Dict, List, Optional, Union
import aiohttp
import json

from .base import BaseProvider
from ..utils.config import Config

class MistralProvider(BaseProvider):
    """Mistral AI provider implementation."""
    
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.get_provider_key('mistral')
        self.api_base = self.config.get_provider_endpoint('mistral')
        self.default_model = self.config.get_default_model('mistral')
        
        if not self.api_key:
            raise ValueError("Mistral API key not found in configuration")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True,
        **kwargs
    ) -> AsyncIterator[Dict[str, str]]:
        """Generate chat completions using Mistral's API."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": messages,
            "stream": stream,
            "model": kwargs.get("model", self.default_model),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if stream:
                    async for line in response.content:
                        if line:
                            try:
                                event_data = json.loads(line.decode('utf-8').split('data: ')[1])
                                if event_data.get("choices"):
                                    content = event_data["choices"][0].get("delta", {}).get("content", "")
                                    yield {
                                        "type": "delta",
                                        "content": content,
                                        "tokens": event_data.get("usage", {}).get("total_tokens", 0)
                                    }
                            except Exception:
                                continue
                else:
                    response_data = await response.json()
                    yield {
                        "type": "complete",
                        "content": response_data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                        "tokens": response_data.get("usage", {}).get("total_tokens", 0)
                    }
    
    async def process_file(
        self,
        file_data: bytes,
        file_type: str,
        task_type: str,
        **kwargs
    ) -> AsyncIterator[Dict[str, str]]:
        """Process a file using Mistral's API."""
        
        # Convert file to base64 for transmission
        import base64
        file_b64 = base64.b64encode(file_data).decode('utf-8')
        
        # Construct a prompt based on the task type
        prompts = {
            "alt_text": "Generate detailed alt text for this image:",
            "analysis": "Analyze this image in detail:",
            "ocr": "Extract and format all text from this image:"
        }
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant skilled in analyzing images."},
            {"role": "user", "content": f"{prompts.get(task_type, 'Analyze this file:')} [image]"}
        ]
        
        # Send as a chat completion with the image
        async for chunk in self.chat_completion(
            messages=messages,
            stream=True,
            model=kwargs.get("model", self.default_model),
            image=file_b64,
            **kwargs
        ):
            yield chunk
    
    async def embeddings(
        self,
        text: Union[str, List[str]],
        **kwargs
    ) -> List[List[float]]:
        """Generate embeddings using Mistral's API."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": kwargs.get("model", "mistral-embed"),
            "input": text if isinstance(text, list) else [text]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/v1/embeddings",
                headers=headers,
                json=data
            ) as response:
                response_data = await response.json()
                return [item["embedding"] for item in response_data.get("data", [])]