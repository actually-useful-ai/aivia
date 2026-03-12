#!/usr/bin/env python3
"""
arXiv API Tool for the MoE System

This tool uses the arXiv Python package to search for academic papers.
No credentials are needed for arXiv. The tool will print out a formatted list of paper results.
"""

import arxiv
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable

# Minimal BaseTool implementation for event handling
class BaseTool:
    def __init__(self, credentials: Dict[str, str] = None):
        pass

    async def emit_event(
        self,
        event: str,
        message: str,
        done: bool,
        emitter: Optional[Callable[[Any], Awaitable[None]]] = None
    ):
        # For CLI usage, simply print the status message
        if emitter:
            await emitter({"event": event, "message": message, "done": done})
        else:
            print(f"[{event.upper()}] {message}")

class ArxivTool(BaseTool):
    """Tool for searching arXiv papers."""
    
    def __init__(self, credentials: Dict[str, str] = None):
        super().__init__(credentials)  # No credentials needed for arXiv
        # The arxiv package doesn't require an explicit client instance
        # but we include one for structure
        self.client = arxiv

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
            __user__: User context (unused)
            __event_emitter__: Optional event emitter for progress updates

        Returns:
            Formatted string of paper results.
        """
        await self.emit_event(
            "status",
            f"Searching arXiv for '{query}'...",
            False,
            __event_emitter__
        )

        try:
            # Create search using the arxiv.Search object
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance if sort_by == "relevance" 
                    else arxiv.SortCriterion.LastUpdatedDate
            )

            # Get results (convert generator to list)
            papers = list(search.results())

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
                # Limit abstract to first 200 characters for brevity
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

async def main():
    """CLI for searching arXiv papers."""
    arxiv_tool = ArxivTool()
    print("arXiv Paper Search CLI Tool")
    print("Enter your search query (or type 'quit' to exit):\n")
    
    while True:
        try:
            user_query = input("Search query: ").strip()
            if user_query.lower() in ['quit', 'exit']:
                print("Exiting arXiv Paper Search CLI.")
                break

            print(f"\nSearching for: {user_query}\n")
            result = await arxiv_tool.execute(user_query)
            print(result)
            print("-" * 40 + "\n")

        except KeyboardInterrupt:
            print("\nExiting arXiv Paper Search CLI.")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())