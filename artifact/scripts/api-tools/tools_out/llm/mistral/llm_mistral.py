"""
Mistral LLM tool for the MoE system.
Provides access to Mistral's language models.
"""

import os
import logging
import mistralai
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from typing import Dict, Any, Optional, List
from ...base import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MistralTool(BaseTool):
    """Tool for interacting with Mistral's language models"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Mistral tool.
        
        Args:
            api_key: Mistral API key. If not provided, will look for MISTRAL_API_KEY env variable.
        """
        super().__init__()
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral API key must be provided")
            
        self.client = MistralClient(api_key=self.api_key)
        
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a request to Mistral's API.
        
        Args:
            parameters: Dictionary containing:
                - messages: List of message dictionaries with 'role' and 'content'
                - model: Model to use (e.g., 'mistral-tiny', 'mistral-small', 'mistral-medium')
                - temperature: Sampling temperature
                - max_tokens: Maximum tokens to generate
                - top_p: Top-p sampling parameter
                - safe_mode: Whether to enable safe mode
                - random_seed: Random seed for reproducibility
                - task: Task type ('chat', 'embed')
                
        Returns:
            Dictionary containing the API response
        """
        try:
            # Emit start event
            await self.emit_status_event(
                "status",
                {"message": f"Starting Mistral {parameters.get('task', 'chat')} task"}
            )
            
            task = parameters.get("task", "chat")
            
            if task == "chat":
                response = await self._chat(parameters)
            elif task == "embed":
                response = await self._embed(parameters)
            else:
                raise ValueError(f"Unknown task type: {task}")
                
            # Emit completion event
            await self.emit_status_event(
                "status",
                {"message": f"Completed Mistral {task} task"}
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error executing Mistral task: {str(e)}")
            await self.emit_status_event(
                "error",
                {"message": f"Mistral task failed: {str(e)}"}
            )
            raise
            
    async def _chat(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat completion tasks"""
        messages = [
            ChatMessage(
                role=msg["role"],
                content=msg["content"]
            )
            for msg in parameters["messages"]
        ]
        
        response = self.client.chat(
            model=parameters.get("model", "mistral-small"),
            messages=messages,
            temperature=parameters.get("temperature", 0.7),
            max_tokens=parameters.get("max_tokens", None),
            top_p=parameters.get("top_p", 1.0),
            safe_mode=parameters.get("safe_mode", False),
            random_seed=parameters.get("random_seed", None)
        )
        
        return {
            "message": {
                "role": response.choices[0].message.role,
                "content": response.choices[0].message.content
            },
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "finish_reason": response.choices[0].finish_reason
        }
        
    async def _embed(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text embedding tasks"""
        response = self.client.embeddings(
            model=parameters.get("model", "mistral-embed"),
            input=parameters["input"]
        )
        
        return {
            "embeddings": response.data[0].embedding,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens
            }
        } 