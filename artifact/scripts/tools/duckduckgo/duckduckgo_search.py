#!/usr/bin/env python3
"""
DuckDuckGo Search API Module
This module provides functionality to search the web using the DuckDuckGo API.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional, Union

class DuckDuckGoSearcher:
    """A class for searching using DuckDuckGo API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the DuckDuckGo searcher with optional API key.
        
        Args:
            api_key: Optional API key (not required for DuckDuckGo)
        """
        self.api_key = api_key or os.environ.get("DUCKDUCKGO_API_KEY")
        
    def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search DuckDuckGo for the given query.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            Dict containing search results
        """
        try:
            # Use DuckDuckGo's search API endpoint
            # Note: This uses the lite version which doesn't require API key
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_redirect': 1,
                'no_html': 1,
                't': 'multi_search_cli'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Extract and format relevant information
            results = {
                "query": query,
                "abstract": data.get("Abstract", ""),
                "abstract_source": data.get("AbstractSource", ""),
                "abstract_url": data.get("AbstractURL", ""),
                "related_topics": [],
                "results": []
            }
            
            # Process related topics
            if "RelatedTopics" in data:
                for topic in data["RelatedTopics"]:
                    if "Text" in topic:
                        # Regular topic
                        topic_data = {
                            "text": topic.get("Text", ""),
                            "url": topic.get("FirstURL", "")
                        }
                        results["related_topics"].append(topic_data)
                    elif "Topics" in topic:
                        # Topic with subtopics
                        for subtopic in topic["Topics"]:
                            subtopic_data = {
                                "text": subtopic.get("Text", ""),
                                "url": subtopic.get("FirstURL", "")
                            }
                            results["related_topics"].append(subtopic_data)
            
            # Process Infobox (if available)
            if "Infobox" in data and data["Infobox"]:
                infobox = []
                for entry in data["Infobox"].get("content", []):
                    infobox.append({
                        "label": entry.get("label", ""),
                        "value": entry.get("value", "")
                    })
                results["infobox"] = infobox
            
            # Process results
            if results["abstract"]:
                results["results"].append({
                    "title": data.get("Heading", query),
                    "snippet": results["abstract"],
                    "url": results["abstract_url"]
                })
            
            # Add related topics as results
            for i, topic in enumerate(results["related_topics"]):
                if i >= max_results - len(results["results"]):
                    break
                    
                results["results"].append({
                    "title": topic["text"].split(" - ")[0] if " - " in topic["text"] else topic["text"],
                    "snippet": topic["text"],
                    "url": topic["url"]
                })
            
            return results
            
        except requests.RequestException as e:
            return {"error": f"Request error: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON parsing error: {str(e)}"}
        except Exception as e:
            return {"error": f"Error: {str(e)}"}

def main():
    """Simple command-line interface for testing."""
    import sys
    if len(sys.argv) < 2:
        print("Usage: python duckduckgo_search.py <query>")
        return
    
    query = " ".join(sys.argv[1:])
    searcher = DuckDuckGoSearcher()
    results = searcher.search(query)
    
    # Print results in a readable format
    print(f"Results for query: {query}\n")
    
    if "error" in results:
        print(f"Error: {results['error']}")
        return
    
    if results["abstract"]:
        print(f"Abstract: {results['abstract']}")
        print(f"Source: {results['abstract_source']} - {results['abstract_url']}\n")
    
    print("Search Results:")
    for i, result in enumerate(results["results"], 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['snippet']}")
        print(f"   URL: {result['url']}\n")
    
    if results["related_topics"]:
        print("Related Topics:")
        for i, topic in enumerate(results["related_topics"], 1):
            print(f"{i}. {topic['text']}")
            print(f"   URL: {topic['url']}")

if __name__ == "__main__":
    main() 