"""News API tool for the MoE system."""

import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from ..base import BaseTool

class NewsAPITool(BaseTool):
    """Tool for searching news articles."""
    
    class UserValves(BaseTool.UserValves):
        """Requires NEWSAPI key"""
        NEWSAPI: str
        
    def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.api_key = credentials['NEWSAPI']
        self.base_url = "https://newsapi.org/v2/everything"

    async def execute(
        self,
        query: str,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None
    ) -> str:
        """
        Search for news articles.
        
        Args:
            query: Search query
            __user__: User context
            __event_emitter__: Event emitter for progress updates
            
        Returns:
            Formatted article results
        """
        await self.emit_event(
            "status",
            f"Searching news articles for '{query}'...",
            False,
            __event_emitter__
        )

        params = {
            "q": query,
            "apiKey": self.api_key,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 5
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            articles = response.json().get("articles", [])

            if not articles:
                await self.emit_event(
                    "status",
                    f"No news articles found for '{query}'",
                    True,
                    __event_emitter__
                )
                return f"No news articles found for '{query}'."

            results = f"Latest news on '{query}':\n\n"
            for i, article in enumerate(articles, 1):
                title = article.get("title", "No Title")
                source = article["source"].get("name", "Unknown Source")
                published = article.get("publishedAt", "Unknown Date")[:10]
                url = article.get("url", "No URL")

                results += f"{i}. {title}\n"
                results += f"   Source: {source}\n"
                results += f"   Published: {published}\n"
                results += f"   URL: {url}\n\n"

            await self.emit_event(
                "status",
                "Search completed",
                True,
                __event_emitter__
            )

            return results

        except requests.RequestException as e:
            error_msg = f"Error fetching news: {str(e)}"
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