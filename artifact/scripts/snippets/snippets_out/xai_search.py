#!/usr/bin/env python3
"""
XAI Web Search CLI Tool

This script uses the XAI API to search the web for information.
The API key is read from environment variables or can be provided directly.
"""

import requests
import os
import sys
import json

# Default API key - will be overridden by environment variable or constructor parameter
DEFAULT_API_KEY = "REDACTED_XAI_KEY"

# XAI API endpoint for web search
XAI_SEARCH_ENDPOINT = "https://api.x.ai/v1/search"


class XaiWebSearcher:
    def __init__(self, api_key=None):
        """
        Initialize the web searcher with API credentials.
        
        Args:
            api_key (str, optional): API key for XAI. If not provided, will check environment variable.
        """
        # Try to get API key from parameter, environment, or default
        self.api_key = api_key or os.environ.get("XAI_API_KEY") or DEFAULT_API_KEY
        self.endpoint = XAI_SEARCH_ENDPOINT
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def search(self, query: str) -> dict:
        """
        Search the web using the XAI API.
        
        Args:
            query (str): The search query provided by the user.
            
        Returns:
            dict: The response from the XAI API as a dictionary.
        """
        payload = {
            "query": query
        }
        try:
            print(f"Searching XAI with query: {query}")
            response = requests.post(self.endpoint, headers=self.headers, json=payload)
            
            # Handle common error scenarios
            if response.status_code == 401:
                print(f"Authentication error (401): Invalid API key. Check your XAI_API_KEY.", file=sys.stderr)
                return {"error": "Authentication failed (401). Check your API key.", "code": 401}
            elif response.status_code != 200:
                print(f"XAI API error: Status code {response.status_code}", file=sys.stderr)
                return {"error": f"Request failed with status code: {response.status_code}", "code": response.status_code}
            
            # Parse JSON response
            try:
                data = response.json()
                return data
            except json.JSONDecodeError:
                print(f"Error: Unable to parse JSON response from XAI API", file=sys.stderr)
                return {"error": "Invalid JSON response", "raw_response": response.text}
            
        except requests.RequestException as e:
            error_msg = f"Request failed: {e}"
            print(f"Error: {error_msg}", file=sys.stderr)
            return {"error": error_msg}


def main():
    """
    Main function to run the interactive CLI.
    """
    # Get API key from environment variable
    api_key = os.environ.get("XAI_API_KEY")
    
    if not api_key:
        print("Warning: XAI_API_KEY environment variable not set. Using default key.", file=sys.stderr)
    
    searcher = XaiWebSearcher(api_key)
    print("XAI Web Search CLI Tool")
    print("Enter your search query, or type 'quit' to exit.\n")
    
    while True:
        user_query = input("Search query: ").strip()
        if user_query.lower() in ['quit', 'exit']:
            print("Exiting XAI Web Search CLI.")
            break
        
        if not user_query:
            continue
            
        print(f"\nSearching for: {user_query}")
        result = searcher.search(user_query)
        
        # Display the results (formatted nicely if JSON)
        print("Results:")
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            try:
                # Pretty-print the returned JSON
                print(json.dumps(result, indent=2))
            except Exception:
                print(result)
        print("\n" + "-"*40 + "\n")


if __name__ == "__main__":
    main()