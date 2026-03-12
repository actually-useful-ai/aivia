"""
Utility tools for the OpenAPI CLI.
"""
from typing import Dict, Any, Optional, List

class UtilityTool:
    """Base class for utility tools."""
    
    async def execute(self, **kwargs) -> str:
        """Execute the utility tool."""
        raise NotImplementedError

class BaseTool(UtilityTool):
    """Tool for building quick backends with Base API."""
    
    def __init__(self, credentials: Dict[str, str]):
        self.api_key = credentials.get('BASE_API')
    
    async def execute(self, action: str, resource: str, data: Optional[Dict[str, Any]] = None) -> str:
        """Execute Base API operation."""
        data_info = f" with data: {data}" if data else ""
        return f"Base API: {action.upper()} {resource}{data_info}"

class BeeceptorTool(UtilityTool):
    """Tool for building mock REST API endpoints with Beeceptor."""
    
    async def execute(self, endpoint: str, status_code: int = 200, response: Optional[Dict[str, Any]] = None) -> str:
        """Create a mock endpoint with Beeceptor."""
        response_info = f" with response: {response}" if response else ""
        return f"Created mock endpoint at '{endpoint}' returning status {status_code}{response_info}"

class ScrnifyTool(UtilityTool):
    """Tool for capturing screenshots and recordings of webpages with Scrnify."""
    
    def __init__(self, credentials: Dict[str, str]):
        self.api_key = credentials.get('SCRNIFY')
    
    async def execute(self, url: str, capture_type: str = 'screenshot', device: str = 'desktop', wait_for: Optional[int] = None) -> str:
        """Capture a screenshot or recording of a webpage."""
        wait_info = f", waiting {wait_for}ms" if wait_for else ""
        return f"Capturing {capture_type} of {url} on {device}{wait_info}"

class PexelsTool(UtilityTool):
    """Tool for accessing free stock photos and videos with Pexels API."""
    
    def __init__(self, credentials: Dict[str, str]):
        self.api_key = credentials.get('PEXELS')
    
    async def execute(self, query: str, type: str = 'photos', per_page: int = 15) -> str:
        """Search for photos or videos on Pexels."""
        return f"Searching Pexels for {per_page} {type} matching '{query}'"

class StaticallyTool(UtilityTool):
    """Tool for using Statically CDN."""
    
    async def execute(self, url: str, operation: str = 'cdn', options: Optional[Dict[str, Any]] = None) -> str:
        """Generate a Statically URL for the given operation."""
        options_info = f" with options: {options}" if options else ""
        return f"Statically {operation} URL for {url}{options_info}"

class SupportivekoalaTool(UtilityTool):
    """Tool for autogenerating images with templates using Supportivekoala API."""
    
    def __init__(self, credentials: Dict[str, str]):
        self.api_key = credentials.get('SUPPORTIVEKOALA')
    
    async def execute(self, template_id: str, variables: Dict[str, str]) -> str:
        """Generate an image with a template."""
        return f"Generating image with template {template_id} using {len(variables)} variables" 