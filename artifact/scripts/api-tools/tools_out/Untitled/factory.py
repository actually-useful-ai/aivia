from typing import Dict, Optional, Type
from .base import BaseProvider
from .coze import CozeProvider
from .mistral import MistralProvider
from ..utils.config import Config

class ProviderFactory:
    """Factory class for creating and managing AI providers."""
    
    _instance = None
    _providers: Dict[str, Type[BaseProvider]] = {
        'coze': CozeProvider,
        'mistral': MistralProvider
    }
    _instances: Dict[str, BaseProvider] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.config = Config()
        self._initialized = True
    
    def register_provider(self, name: str, provider_class: Type[BaseProvider]) -> None:
        """Register a new provider class.
        
        Args:
            name: Provider name
            provider_class: Provider class implementing BaseProvider
        """
        self._providers[name] = provider_class
    
    def get_provider(self, name: str) -> Optional[BaseProvider]:
        """Get or create a provider instance.
        
        Args:
            name: Provider name
            
        Returns:
            Provider instance or None if provider not found/available
        """
        if name not in self._instances:
            if name not in self._providers:
                return None
                
            # Check if provider is configured
            if not self.config.get_provider_key(name):
                return None
                
            try:
                self._instances[name] = self._providers[name]()
            except Exception:
                return None
                
        return self._instances[name]
    
    @property
    def available_providers(self) -> Dict[str, bool]:
        """Get dictionary of available providers."""
        return self.config.active_providers
    
    def clear_instances(self) -> None:
        """Clear all provider instances."""
        self._instances.clear() 