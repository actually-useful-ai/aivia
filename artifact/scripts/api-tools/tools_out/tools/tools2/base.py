from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, List, Optional, Union

class BaseProvider(ABC):
    """Base class for all AI providers."""
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True,
        **kwargs
    ) -> AsyncIterator[Dict[str, str]]:
        """Generate chat completions from the AI provider.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Dict containing response chunks with 'type' and 'content' keys
        """
        pass
    
    @abstractmethod
    async def process_file(
        self,
        file_data: bytes,
        file_type: str,
        task_type: str,
        **kwargs
    ) -> AsyncIterator[Dict[str, str]]:
        """Process a file using the AI provider.
        
        Args:
            file_data: Raw file bytes
            file_type: MIME type of the file
            task_type: Type of processing (e.g., 'alt_text', 'analysis')
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Dict containing response chunks with 'type' and 'content' keys
        """
        pass
    
    @abstractmethod
    async def embeddings(
        self,
        text: Union[str, List[str]],
        **kwargs
    ) -> List[List[float]]:
        """Generate embeddings for text using the AI provider.
        
        Args:
            text: Single string or list of strings to embed
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of embedding vectors
        """
        pass