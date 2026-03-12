from typing import AsyncIterator, Dict, List, Optional, Union
import aiohttp
import json
from cozepy import Coze, TokenAuth, Message, ChatEventType, MessageObjectString

from .base import BaseProvider
from ..utils.config import Config

class CozeProvider(BaseProvider):
    """Coze AI provider implementation."""
    
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.get_provider_key('coze')
        self.bot_id = self.config.get_default_model('coze')
        
        if not self.api_key:
            raise ValueError("Coze API key not found in configuration")
            
        self.coze = Coze(auth=TokenAuth(token=self.api_key))
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True,
        **kwargs
    ) -> AsyncIterator[Dict[str, str]]:
        """Generate chat completions using Coze's API."""
        
        try:
            # Convert messages to Coze format
            coze_messages = [
                Message(role=msg["role"], content=msg["content"])
                for msg in messages
            ]
            
            # Get bot ID from kwargs or use default
            bot_id = kwargs.get("bot_id", self.bot_id)
            
            # Start chat completion stream
            async for event in self.coze.chat_completion(
                bot_id=bot_id,
                messages=coze_messages,
                stream=stream
            ):
                if event.type == ChatEventType.DELTA:
                    yield {
                        "type": "delta",
                        "content": event.delta.content if event.delta else ""
                    }
                elif event.type == ChatEventType.ERROR:
                    yield {
                        "type": "error",
                        "content": str(event.error) if event.error else "Unknown error"
                    }
                elif event.type == ChatEventType.DONE:
                    yield {
                        "type": "done",
                        "content": ""
                    }
                    
        except Exception as e:
            yield {
                "type": "error",
                "content": str(e)
            }
    
    async def process_file(
        self,
        file_data: bytes,
        file_type: str,
        task_type: str,
        **kwargs
    ) -> AsyncIterator[Dict[str, str]]:
        """Process a file using Coze's API."""
        
        try:
            # Convert file to base64
            import base64
            file_b64 = base64.b64encode(file_data).decode('utf-8')
            
            # Get bot ID from kwargs or use default
            bot_id = kwargs.get("bot_id", self.bot_id)
            
            # Start file processing stream
            async for event in self.coze.process_file(
                bot_id=bot_id,
                file_data=file_b64,
                file_type=file_type,
                task_type=task_type,
                **kwargs
            ):
                if event.type == ChatEventType.DELTA:
                    yield {
                        "type": "delta",
                        "content": event.delta.content if event.delta else ""
                    }
                elif event.type == ChatEventType.ERROR:
                    yield {
                        "type": "error",
                        "content": str(event.error) if event.error else "Unknown error"
                    }
                elif event.type == ChatEventType.DONE:
                    yield {
                        "type": "done",
                        "content": ""
                    }
                    
        except Exception as e:
            yield {
                "type": "error",
                "content": str(e)
            }
    
    async def embeddings(
        self,
        text: Union[str, List[str]],
        **kwargs
    ) -> List[List[float]]:
        """Generate embeddings using Coze's API."""
        
        try:
            # Get bot ID from kwargs or use default
            bot_id = kwargs.get("bot_id", self.bot_id)
            
            # Generate embeddings
            embeddings = await self.coze.embeddings(
                bot_id=bot_id,
                text=text if isinstance(text, list) else [text]
            )
            
            return [embedding.vector for embedding in embeddings]
            
        except Exception as e:
            raise ValueError(f"Failed to generate embeddings: {str(e)}")