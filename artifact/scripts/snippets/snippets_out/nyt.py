"""New York Times API tool for the MoE system."""

import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from ..base import BaseTool

class NYTTool(BaseTool):
    """Tool for searching New York Times articles."""
    
    class UserValves(BaseTool.UserValves):
        """Requires NYT API Key"""
        NYT: str
        
    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.api_key = credentials['NYT']
        self.base_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"

    async def execute(
        self,
        query: str,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None
    ) -> str:
        """
        Search for NYT articles.
        
        Args:
            query: Search query
            __user__: User context
            __event_emitter__: Event emitter for progress updates
            
        Returns:
            Formatted article results
        """
        await self.emit_event(
            "status",
            f"Searching NYT articles for '{query}'...",
            False,
            __event_emitter__
        )

        params = {
            "q": query,
            "api-key": self.api_key,
            "sort": "newest",
            "page": 0,
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            articles = response.json().get("response", {}).get("docs", [])

            if not articles:
                await self.emit_event(
                    "status",
                    f"No NYT articles found for '{query}'",
                    True,
                    __event_emitter__
                )
                return f"No NYT articles found for '{query}'."

            results = f"Latest NYT articles on '{query}':\n\n"
            for i, article in enumerate(articles[:5], 1):
                title = article.get("headline", {}).get("main", "No Title")
                pub_date = article.get("pub_date", "Unknown Date")[:10]
                url = article.get("web_url", "No URL")

                results += f"{i}. {title}\n"
                results += f"   Published: {pub_date}\n"
                results += f"   URL: {url}\n\n"

            await self.emit_event(
                "status",
                "Search completed",
                True,
                __event_emitter__
            )

            return results

        except requests.RequestException as e:
            error_msg = f"Error fetching NYT news: {str(e)}"
            await self.emit_event(
                "status",
                error_msg,
                True,
                __event_emitter__
            )
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            await self.emit_event(
                "status",
                error_msg,
                True,
                __event_emitter__
            )
            return error_msg 