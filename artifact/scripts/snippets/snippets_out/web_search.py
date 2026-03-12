#!/usr/bin/env python3
"""Web search tool using xAI's Grok API."""

import json
import asyncio
import requests
from typing import Dict, Any, Optional, List
import argparse

class XAISearchTools:
    def __init__(self, api_key="REDACTED_XAI_KEY", base_url="https://api.x.ai/v1"):
        """Initialize the search tools with API key and base URL."""
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        print("\nInitialized xAI web search tools")

    def normalize_url(self, url: str) -> str:
        """Ensure URL has proper protocol"""
        if not url.startswith(('http://', 'https://')):
            return f"https://{url}"
        return url

    def search_web(self, query: str) -> str:
        """Search the web using Grok's function calling capabilities"""
        endpoint = f"{self.base_url}/chat/completions"
        
        # Define the search function that we want Grok to call
        functions = [
            {
                "name": "web_search",
                "description": "Search the web for information on a specific topic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_query": {
                            "type": "string",
                            "description": "The search query to use for finding information on the web"
                        }
                    },
                    "required": ["search_query"]
                }
            }
        ]
        
        data = {
            "model": "grok-2-latest",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that can search the web for information. When asked to find information, use the web_search function to formulate an appropriate search query."},
                {"role": "user", "content": query}
            ],
            "temperature": 0.2,
            "tools": functions,
            "tool_choice": {"type": "function", "function": {"name": "web_search"}}
        }
        
        try:
            print(f"\nSending search request to xAI API for: {query}")
            response = requests.post(endpoint, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Extract the function call and its arguments
            function_call = result["choices"][0]["message"]["tool_calls"][0]["function"]
            function_args = json.loads(function_call["arguments"])
            search_query = function_args.get("search_query", query)
            
            print(f"Search query formulated: {search_query}")
            
            # Now perform the actual web search with the formulated query
            return self.execute_search(search_query)
        except requests.exceptions.RequestException as e:
            print(f"\nAPI request error: {str(e)}")
            return f"Error making request to xAI API: {str(e)}"
        except Exception as e:
            print(f"\nError processing search: {str(e)}")
            return f"Error processing search: {str(e)}"

    def execute_search(self, search_query: str) -> str:
        """Execute the web search and summarize results"""
        endpoint = f"{self.base_url}/chat/completions"
        
        data = {
            "model": "grok-2-latest",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that searches the web for information. Provide a comprehensive, well-organized summary of the information found for the search query."},
                {"role": "user", "content": f"Search the web for information about: {search_query}\n\nProvide a comprehensive summary of what you find, including key facts, different perspectives, and relevant details. Organize the information clearly."}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        try:
            print(f"\nExecuting search and summarizing results for: {search_query}")
            response = requests.post(endpoint, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Extract the assistant's response
            content = result["choices"][0]["message"]["content"]
            return content
        except requests.exceptions.RequestException as e:
            print(f"\nAPI request error: {str(e)}")
            return f"Error making request to xAI API: {str(e)}"
        except Exception as e:
            print(f"\nError processing search results: {str(e)}")
            return f"Error processing search results: {str(e)}"

async def main():
    """Main function to run the web search CLI tool."""
    parser = argparse.ArgumentParser(description="Search the web using xAI's Grok API")
    parser.add_argument('query', nargs='*', help='The search query')
    parser.add_argument('--api-key', dest='api_key', help='xAI API key (overrides the default)')
    args = parser.parse_args()
    
    # Initialize the search tools
    api_key = args.api_key if args.api_key else "REDACTED_XAI_KEY"
    searcher = XAISearchTools(api_key=api_key)
    
    print("\nxAI Web Search Tool")
    print("-------------------")
    
    if args.query:
        # If query provided as command line argument
        query = ' '.join(args.query)
        result = searcher.search_web(query)
        print(f"\nSearch Results for '{query}':\n")
        print(result)
    else:
        # Interactive mode
        print("Enter a search query or 'quit' to exit\n")
        
        while True:
            try:
                query = input("\nEnter search query: ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if query:
                    result = searcher.search_web(query)
                    print(f"\nSearch Results:\n")
                    print(result)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 