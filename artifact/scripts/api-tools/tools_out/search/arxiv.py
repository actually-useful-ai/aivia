"""arXiv API tool for the MoE system."""

import arxiv
from typing import Dict, Any, Optional, Callable, Awaitable, List
from ..base import BaseTool

class ArxivTool(BaseTool):
    """Tool for searching arXiv papers."""
    
    def __init__(self, credentials: Dict[str, str] = None):
        super().__init__(credentials)  # No credentials needed for arXiv
        self.client = arxiv.Client()

    async def execute(
        self,
        query: str,
        max_results: int = 5,
        sort_by: str = "relevance",
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None
    ) -> str:
        """
        Search for arXiv papers.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            sort_by: Sort order (relevance or lastUpdatedDate)
            __user__: User context
            __event_emitter__: Event emitter for progress updates
            
        Returns:
            Formatted paper results
        """
        await self.emit_event(
            "status",
            f"Searching arXiv for '{query}'...",
            False,
            __event_emitter__
        )

        try:
            # Create search
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance if sort_by == "relevance" 
                else arxiv.SortCriterion.LastUpdatedDate
            )

            # Get results
            papers = list(self.client.results(search))

            if not papers:
                await self.emit_event(
                    "status",
                    f"No arXiv papers found for '{query}'",
                    True,
                    __event_emitter__
                )
                return f"No arXiv papers found for '{query}'."

            results = f"Latest arXiv papers on '{query}':\n\n"
            for i, paper in enumerate(papers, 1):
                results += f"{i}. {paper.title}\n"
                results += f"   Authors: {', '.join(author.name for author in paper.authors)}\n"
                results += f"   Published: {paper.published.strftime('%Y-%m-%d')}\n"
                results += f"   URL: {paper.pdf_url}\n"
                results += f"   Abstract: {paper.summary[:200]}...\n\n"

            await self.emit_event(
                "status",
                "Search completed",
                True,
                __event_emitter__
            )

            return results

        except Exception as e:
            error_msg = f"Error searching arXiv: {str(e)}"
            await self.emit_event(
                "status",
                error_msg,
                True,
                __event_emitter__
            )
            return error_msg 