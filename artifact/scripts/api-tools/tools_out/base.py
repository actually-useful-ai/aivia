"""Base tool class for the MoE system."""

from typing import Dict, Any, Optional, Callable, Awaitable, List
from pydantic import BaseModel
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseTool:
    """Base class for all tools in the MoE system."""
    
    class UserValves(BaseModel):
        """Base class for tool credentials."""
        pass
        
    def __init__(self, credentials: Dict[str, str] = None):
        """
        Initialize the tool.
        
        Args:
            credentials: Optional dictionary of credentials
        """
        self.credentials = credentials or {}
        self.validate_credentials()
        
    def validate_credentials(self) -> None:
        """
        Validate that all required credentials are present.
        
        Raises:
            ValueError: If required credentials are missing
        """
        required_creds = self.UserValves.__annotations__.keys()
        missing = [cred for cred in required_creds if cred not in self.credentials]
        
        if missing:
            raise ValueError(f"Missing required credentials: {', '.join(missing)}")
            
    async def execute(
        self,
        **kwargs: Any,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None
    ) -> Any:
        """
        Execute the tool's main functionality.
        
        Args:
            **kwargs: Tool-specific arguments
            __user__: User context dictionary
            __event_emitter__: Optional event emitter for progress updates
            
        Returns:
            Tool-specific result
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Tool must implement execute method")
        
    async def emit_event(
        self,
        event_type: str,
        description: str,
        done: bool = False,
        emitter: Optional[Callable[[Any], Awaitable[None]]] = None
    ) -> None:
        """
        Emit a status event if an emitter is available.
        
        Args:
            event_type: Type of event
            description: Event description
            done: Whether this is the final event
            emitter: Optional event emitter function
        """
        if emitter:
            await emitter({
                "type": event_type,
                "data": {
                    "description": description,
                    "done": done
                }
            }) 