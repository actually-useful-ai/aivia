"""
Perplexity LLM tool for the MoE system.
Provides access to Perplexity's language models.
"""

import os
import logging
import httpx
from typing import Dict, Any, Optional, List
from ...base import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerplexityTool(BaseTool):
    """Tool for interacting with Perplexity's language models"""
    
    API_URL = "https://api.perplexity.ai"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Perplexity tool.
        
        Args:
            api_key: Perplexity API key. If not provided, will look for PERPLEXITY_API_KEY env variable.
        """
        super().__init__()
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("Perplexity API key must be provided")
            
        self.client = httpx.AsyncClient(
            base_url=self.API_URL,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a request to Perplexity's API.
        
        Args:
            parameters: Dictionary containing:
                - messages: List of message dictionaries with 'role' and 'content'
                - model: Model to use (e.g., 'pplx-7b-chat', 'pplx-70b-chat')
                - temperature: Sampling temperature
                - max_tokens: Maximum tokens to generate
                - top_p: Top-p sampling parameter
                - top_k: Top-k sampling parameter
                - presence_penalty: Presence penalty parameter
                - frequency_penalty: Frequency penalty parameter
                - task: Task type ('chat', 'completion')
                
        Returns:
            Dictionary containing the API response
        """
        try:
            # Emit start event
            await self.emit_status_event(
                "status",
                {"message": f"Starting Perplexity {parameters.get('task', 'chat')} task"}
            )
            
            task = parameters.get("task", "chat")
            
            if task == "chat":
                response = await self._chat(parameters)
            elif task == "completion":
                response = await self._completion(parameters)
            else:
                raise ValueError(f"Unknown task type: {task}")
                
            # Emit completion event
            await self.emit_status_event(
                "status",
                {"message": f"Completed Perplexity {task} task"}
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error executing Perplexity task: {str(e)}")
            await self.emit_status_event(
                "error",
                {"message": f"Perplexity task failed: {str(e)}"}
            )
            raise
            
    async def _chat(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat completion tasks"""
        response = await self.client.post(
            "/chat/completions",
            json={
                "model": parameters.get("model", "pplx-7b-chat"),
                "messages": parameters["messages"],
                "temperature": parameters.get("temperature", 0.7),
                "max_tokens": parameters.get("max_tokens", None),
                "top_p": parameters.get("top_p", 1.0),
                "top_k": parameters.get("top_k", None),
                "presence_penalty": parameters.get("presence_penalty", 0.0),
                "frequency_penalty": parameters.get("frequency_penalty", 0.0)
            }
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "message": {
                "role": data["choices"][0]["message"]["role"],
                "content": data["choices"][0]["message"]["content"]
            },
            "usage": data["usage"],
            "finish_reason": data["choices"][0]["finish_reason"]
        }
        
    async def _completion(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text completion tasks"""
        response = await self.client.post(
            "/completions",
            json={
                "model": parameters.get("model", "pplx-7b-chat"),
                "prompt": parameters["prompt"],
                "temperature": parameters.get("temperature", 0.7),
                "max_tokens": parameters.get("max_tokens", None),
                "top_p": parameters.get("top_p", 1.0),
                "top_k": parameters.get("top_k", None),
                "presence_penalty": parameters.get("presence_penalty", 0.0),
                "frequency_penalty": parameters.get("frequency_penalty", 0.0)
            }
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "text": data["choices"][0]["text"],
            "usage": data["usage"],
            "finish_reason": data["choices"][0]["finish_reason"]
        }
        
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose() 