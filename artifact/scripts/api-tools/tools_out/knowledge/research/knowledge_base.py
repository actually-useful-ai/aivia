"""
Knowledge base tools with enhanced accessibility and formatting
"""

import json
import requests
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Union, List, Callable
import re
from pathlib import Path
import os
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import wolframalpha
from bs4 import BeautifulSoup
import markdown
import html2text
from langchain_community.document_loaders import YoutubeLoader

class EventEmitter:
    """Event emitter for progress tracking"""
    def __init__(self, event_emitter: Callable[[dict], Any] = None):
        self.event_emitter = event_emitter

    async def progress_update(self, description):
        await self.emit(description)

    async def error_update(self, description):
        await self.emit(description, "error", True)

    async def success_update(self, description):
        await self.emit(description, "success", True)

    async def emit(self, description="Unknown State", status="in_progress", done=False):
        if self.event_emitter:
            await self.event_emitter({
                "type": "status",
                "data": {
                    "status": status,
                    "description": description,
                    "done": done,
                }
            })

class Tools:
    """Tools for knowledge base operations with enhanced accessibility"""
    
    class Valves(BaseModel):
        WIKIDATA_ENDPOINT: str = Field(
            default="https://query.wikidata.org/sparql",
            description="Wikidata SPARQL endpoint"
        )
        WIKIDATA_USER_AGENT: str = Field(
            default="ToolLama Knowledge Base/1.0",
            description="User agent for Wikidata queries"
        )
        WOLFRAM_TIMEOUT: int = Field(
            default=30,
            description="Default timeout for Wolfram Alpha queries"
        )
        PERPLEXITY_MODES: Dict[str, Dict[str, Any]] = Field(
            default={
                "search": {
                    "description": "General web search",
                    "focus_areas": ["general", "news", "tech", "science"]
                },
                "academic": {
                    "description": "Academic research",
                    "focus_areas": ["papers", "journals", "conferences", "books"]
                },
                "writing": {
                    "description": "Writing assistance",
                    "focus_areas": ["grammar", "style", "citations", "references"]
                },
                "analysis": {
                    "description": "Deep analysis",
                    "focus_areas": ["trends", "comparisons", "statistics", "insights"]
                }
            },
            description="Available Perplexity search modes"
        )
        YOUTUBE_LANGUAGES: List[str] = Field(
            default=["en", "en_auto"],
            description="Default YouTube transcript languages"
        )
        
    def __init__(self):
        self.valves = self.Valves()
        self.sparql = SPARQLWrapper(self.valves.WIKIDATA_ENDPOINT)
        self.sparql.agent = self.valves.WIKIDATA_USER_AGENT
        
        # Initialize Wolfram Alpha client if API key is available
        wolfram_key = os.getenv("WOLFRAM_APP_ID")
        if wolfram_key:
            self.wolfram_client = wolframalpha.Client(wolfram_key)
        else:
            self.wolfram_client = None
            print("Warning: WOLFRAM_APP_ID not set", file=sys.stderr)
            
        # Initialize Perplexity client if API key is available
        self.perplexity_key = "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"
        if not self.perplexity_key:
            print("Warning: PERPLEXITY_API_KEY not set", file=sys.stderr)
            
    def _convert_to_sparql(self, query: str) -> str:
        """Convert natural language query to SPARQL"""
        # TODO: Implement natural language to SPARQL conversion
        # For now, return basic SPARQL query template
        return f"""
        SELECT ?item ?itemLabel ?date WHERE {{
            ?item wdt:P31 ?type .
            ?item wdt:P571 ?date .
            ?item rdfs:label ?itemLabel .
            FILTER(CONTAINS(LCASE(?itemLabel), LCASE("{query}")))
            FILTER(LANG(?itemLabel) = "en")
        }}
        LIMIT 10
        """
        
    def query_wikidata(self, query: str, format: str = "simple", limit: int = 10) -> Dict[str, Any]:
        """Query Wikidata for structured information"""
        try:
            # Convert natural language to SPARQL if needed
            if not query.lower().startswith("select "):
                query = self._convert_to_sparql(query)
                
            # Set up query
            self.sparql.setQuery(query)
            self.sparql.setReturnFormat(JSON)
            
            # Execute query
            results = self.sparql.query().convert()
            
            # Process results based on format
            if format == "raw":
                processed_results = results
            else:
                processed_results = []
                for result in results["results"]["bindings"]:
                    if format == "simple":
                        processed_results.append({
                            "label": result.get("itemLabel", {}).get("value"),
                            "value": result.get("item", {}).get("value")
                        })
                    else:  # detailed
                        processed_results.append({
                            k: v.get("value") for k, v in result.items()
                        })
                        
                # Limit results
                processed_results = processed_results[:limit]
                
            return {
                "status": "success",
                "data": {
                    "query": query,
                    "format": format,
                    "results": processed_results,
                    "count": len(processed_results)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error querying Wikidata: {str(e)}"
            }
            
    def query_wolfram(self, query: str, options: dict = {}) -> Dict[str, Any]:
        """Query Wolfram Alpha for computational knowledge"""
        try:
            if not self.wolfram_client:
                raise ValueError("Wolfram Alpha API key not configured")
                
            # Process options
            format_type = options.get("format", "plain")
            timeout = options.get("timeout", self.valves.WOLFRAM_TIMEOUT)
            show_steps = options.get("show_steps", False)
            units = options.get("units", "metric")
            
            # Add units preference to query if specified
            if units == "imperial":
                query = f"{query} (using imperial units)"
                
            # Add step-by-step request if needed
            if show_steps:
                query = f"step-by-step {query}"
                
            # Make API request
            result = self.wolfram_client.query(query, timeout=timeout)
            
            # Process results based on format
            if format_type == "math":
                # Extract mathematical notation
                pods = [pod for pod in result.pods if hasattr(pod, 'text') and pod.text]
                processed_result = {
                    "input": next((pod.text for pod in pods if pod.title == 'Input'), query),
                    "steps": [pod.text for pod in pods if 'step' in pod.title.lower()],
                    "solution": next((pod.text for pod in pods if pod.title in ['Solution', 'Result']), None)
                }
            elif format_type == "image":
                # Extract image URLs
                pods = [pod for pod in result.pods if hasattr(pod, 'img') and pod.img]
                processed_result = {
                    "images": [{"title": pod.title, "url": pod.img.src} for pod in pods]
                }
            else:  # plain
                # Extract plain text
                pods = [pod for pod in result.pods if hasattr(pod, 'text') and pod.text]
                processed_result = {
                    "pods": [{"title": pod.title, "text": pod.text} for pod in pods]
                }
                
            return {
                "status": "success",
                "data": {
                    "query": query,
                    "format": format_type,
                    "result": processed_result,
                    "options": options
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error querying Wolfram Alpha: {str(e)}"
            }
            
    def search_perplexity(self, query: str, mode: str = "search", options: dict = {}) -> Dict[str, Any]:
        """Search using Perplexity AI"""
        try:
            if not self.perplexity_key:
                raise ValueError("Perplexity API key not configured")
                
            # Validate mode
            if mode not in self.valves.PERPLEXITY_MODES:
                raise ValueError(f"Invalid mode: {mode}")
                
            # Process options
            focus = options.get("focus")
            max_results = options.get("max_results", 5)
            include_citations = options.get("include_citations", False)
            recent_only = options.get("recent_only", False)
            
            # Validate focus area if specified
            if focus and focus not in self.valves.PERPLEXITY_MODES[mode]["focus_areas"]:
                raise ValueError(f"Invalid focus area for mode {mode}: {focus}")
                
            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.perplexity_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "query": query,
                "mode": mode,
                "max_results": max_results
            }
            
            if focus:
                data["focus"] = focus
            if recent_only:
                data["time_range"] = "recent"
                
            # Make API request
            response = requests.post(
                "https://api.perplexity.ai/search",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            # Process response
            results = response.json()
            
            # Format results
            processed_results = []
            for result in results.get("results", []):
                processed_result = {
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "snippet": result.get("snippet")
                }
                
                if include_citations and "citations" in result:
                    processed_result["citations"] = result["citations"]
                    
                processed_results.append(processed_result)
                
            return {
                "status": "success",
                "data": {
                    "query": query,
                    "mode": mode,
                    "focus": focus,
                    "results": processed_results,
                    "count": len(processed_results)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error searching Perplexity: {str(e)}"
            }
            
    async def get_youtube_transcript(self, url: str, options: dict = {}, __event_emitter__: Callable[[dict], Any] = None) -> Dict[str, Any]:
        """Get transcript from YouTube videos with enhanced options"""
        emitter = EventEmitter(__event_emitter__)
        
        try:
            await emitter.progress_update(f"Getting transcript for {url}")
            
            # Validate URL
            if not url or url == "" or "dQw4w9WgXcQ" in url:  # Block Rick Roll
                raise ValueError(f"Invalid YouTube URL: {url}")
                
            # Process options
            languages = options.get("language", self.valves.YOUTUBE_LANGUAGES)
            translate_to = options.get("translate_to", "en")
            include_metadata = options.get("include_metadata", False)
            
            # Initialize loader with options
            loader = YoutubeLoader.from_youtube_url(
                url,
                add_video_info=True,
                language=languages,
                translation=translate_to
            )
            
            # Load transcript
            transcript = loader.load()
            
            if len(transcript) == 0:
                raise ValueError(f"Failed to find transcript for {url}")
                
            # Extract metadata and transcript
            metadata = transcript[0].metadata
            text = "\n".join(doc.page_content for doc in transcript)
            
            # Prepare result
            result = {
                "transcript": text,
                "url": url
            }
            
            if include_metadata:
                result["metadata"] = {
                    "title": metadata.get("title"),
                    "author": metadata.get("author"),
                    "description": metadata.get("description"),
                    "view_count": metadata.get("view_count"),
                    "publish_date": str(metadata.get("publish_date"))
                }
                
            await emitter.success_update(f"Successfully retrieved transcript for {metadata.get('title', url)}")
            
            return {
                "status": "success",
                "data": result
            }
            
        except Exception as e:
            error_message = f"Error getting YouTube transcript: {str(e)}"
            await emitter.error_update(error_message)
            return {
                "status": "error",
                "message": error_message
            } 