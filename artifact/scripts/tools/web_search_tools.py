#!/usr/bin/env python3
"""
Advanced Web Search Tools
Combines multiple search approaches including:
- OpenAI chat completion for web searches
- X.AI Grok API as a fallback
- Traditional web search via SearXNG
- Direct web scraping via Jina Reader
"""

import json
import requests
import sys
import re
import os
import time
import concurrent.futures
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse

class WebSearchTools:
    """Unified web search tools combining multiple search engines and strategies."""
    
    def __init__(self, api_key=None, openai_api_key=None, verbose=False):
        """
        Initialize the web search tools.
        
        Args:
            api_key: X.AI API key for Grok search
            openai_api_key: OpenAI API key for using OpenAI's models
            verbose: Whether to print detailed logs
        """
        # API keys
        self.api_key = api_key or os.getenv("XAI_API_KEY") or "REDACTED_XAI_KEY"
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY") or None
        
        # API endpoints
        self.xai_base_url = "https://api.x.ai/v1"
        self.openai_base_url = "https://api.openai.com/v1"
        self.reader_api = "https://r.jina.ai/"
        self.searxng_url = "https://paulgo.io/search"
        
        # Options
        self.verbose = verbose
        self.timeout = 45  # General timeout for requests
        
        # Set up API headers
        self.xai_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        if self.openai_api_key:
            self.openai_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
        
        # Default search engine configurations
        self.search_engines = {
            "google": {
                "name": "Google",
                "prefix": "!go",
                "searxng_url": self.searxng_url,
                "selector": "#urls"
            },
            "bing": {
                "name": "Bing",
                "prefix": "!bi",
                "searxng_url": self.searxng_url,
                "selector": "#urls"
            },
            "duckduckgo": {
                "name": "DuckDuckGo",
                "prefix": "!ddg",
                "searxng_url": self.searxng_url,
                "selector": "#urls"
            },
            "baidu": {
                "name": "Baidu",
                "prefix": "",
                "searxng_url": "https://www.baidu.com/s",
                "selector": "#content_left"
            }
        }
        
        if self.verbose:
            self.log(f"Initialized Web Search Tools with multiple search backends")
    
    def log(self, message: str):
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {message}", file=sys.stderr)
    
    def normalize_url(self, url: str) -> str:
        """Normalize a URL to ensure it has a proper protocol."""
        if not url.startswith(('http://', 'https://')):
            return f"https://{url}"
        return url
    
    def search_with_openai(self, query: str) -> Dict[str, Any]:
        """
        Search the web using OpenAI's model with web search capabilities.
        
        Args:
            query: The search query
            
        Returns:
            Dictionary with search results
        """
        if not self.openai_api_key:
            return {
                "status": "error",
                "message": "OpenAI API key not provided",
                "query": query,
                "source": "openai",
                "timestamp": datetime.now().isoformat()
            }
            
        self.log(f"Starting OpenAI search for: {query}")
        endpoint = f"{self.openai_base_url}/chat/completions"
        
        try:
            # Format prompt for web search
            data = {
                "model": "gpt-4o",  # Use a model with web browsing ability
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant with access to real-time web information. Provide accurate, up-to-date information to answer the user's query. Include relevant details, cite your sources, and organize information clearly."},
                    {"role": "user", "content": f"Search the web for information about: {query}\n\nProvide a comprehensive answer with all relevant details."}
                ],
                "temperature": 0.3
            }
            
            self.log(f"Sending search request to OpenAI")
            response = requests.post(
                endpoint, 
                headers=self.openai_headers, 
                json=data, 
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            content = result["choices"][0]["message"]["content"]
            
            return {
                "status": "success",
                "query": query,
                "results": content,
                "source": "openai",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_message = f"Error in OpenAI search: {str(e)}"
            self.log(error_message)
            return {
                "status": "error",
                "message": error_message,
                "query": query,
                "source": "openai",
                "timestamp": datetime.now().isoformat()
            }
    
    def search_with_grok(self, query: str) -> Dict[str, Any]:
        """
        Search the web using X.AI's Grok API.
        
        Args:
            query: The search query
            
        Returns:
            Dictionary with search results
        """
        self.log(f"Starting Grok search for: {query}")
        endpoint = f"{self.xai_base_url}/chat/completions"
        
        try:
            # Direct search approach using Grok without tool calling
            data = {
                "model": "grok-3-mini-latest",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that provides accurate and detailed information. Answer the user's query with facts and relevant information."},
                    {"role": "user", "content": f"I need information about: {query}\n\nProvide a detailed and accurate answer."}
                ],
                "temperature": 0.3
            }
            
            self.log(f"Sending search request to X.AI")
            response = requests.post(
                endpoint, 
                headers=self.xai_headers, 
                json=data, 
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            content = result["choices"][0]["message"]["content"]
            
            return {
                "status": "success",
                "query": query,
                "results": content,
                "source": "grok",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_message = f"Error in Grok search: {str(e)}"
            self.log(error_message)
            return {
                "status": "error",
                "message": error_message,
                "query": query,
                "source": "grok",
                "timestamp": datetime.now().isoformat()
            }
    
    def search_with_searxng(self, query: str, engine: str = "google") -> Dict[str, Any]:
        """
        Search the web using SearXNG metasearch engine.
        
        Args:
            query: Search query
            engine: Search engine to use (google, bing, duckduckgo, etc.)
            
        Returns:
            Dictionary with search results
        """
        self.log(f"Starting SearXNG search with {engine} for: {query}")
        
        try:
            if engine not in self.search_engines:
                raise ValueError(f"Unsupported search engine: {engine}")
            
            engine_config = self.search_engines[engine]
            
            # Prepare the search URL
            if engine == "baidu":
                url = f"{self.reader_api}{engine_config['searxng_url']}?wd={quote_plus(query)}"
            else:
                prefix = engine_config["prefix"]
                url = f"{self.reader_api}{engine_config['searxng_url']}?q={prefix} {quote_plus(query)}"
            
            headers = {"X-Target-Selector": engine_config["selector"]}
            
            self.log(f"Sending request to SearXNG with {engine}")
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Extract search results from HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = []
            
            for result in soup.select('.result'):
                title_elem = result.select_one('.result-title')
                url_elem = result.select_one('.result-url')
                snippet_elem = result.select_one('.result-content')
                
                if title_elem and url_elem:
                    title = title_elem.get_text(strip=True)
                    result_url = url_elem.get('href') or url_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    search_results.append({
                        "title": title,
                        "url": result_url,
                        "snippet": snippet
                    })
            
            # If BeautifulSoup extraction failed, return raw HTML
            if not search_results:
                return {
                    "status": "success",
                    "query": query,
                    "engine": engine,
                    "raw_html": response.text,
                    "results": [],
                    "source": "searxng",
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "status": "success",
                "query": query,
                "engine": engine,
                "results": search_results,
                "source": "searxng",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_message = f"Error in SearXNG search: {str(e)}"
            self.log(error_message)
            return {
                "status": "error",
                "message": error_message,
                "query": query,
                "engine": engine,
                "source": "searxng",
                "timestamp": datetime.now().isoformat()
            }
    
    def scrape_webpage(self, url: str) -> Dict[str, Any]:
        """
        Scrape and extract content from a webpage using Jina Reader.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary with scraped content
        """
        self.log(f"Scraping webpage: {url}")
        
        try:
            # Normalize URL
            url = self.normalize_url(url)
            
            # Use Jina Reader API
            jina_url = f"{self.reader_api}{url}"
            headers = {
                "X-No-Cache": "false",
                "X-With-Generated-Alt": "true"
            }
            
            self.log(f"Sending request to Jina Reader")
            response = requests.get(jina_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            content = response.text
            
            # Extract title from scraped content
            title_match = re.search(r'Title: (.*)\n', content)
            title = title_match.group(1).strip() if title_match else "Unknown Title"
            
            # Get domain name for source attribution
            domain = urlparse(url).netloc
            
            # Clean URLs from content to reduce token count
            cleaned_content = re.sub(r'\((http[^)]+)\)', '', content)
            
            return {
                "status": "success",
                "url": url,
                "domain": domain,
                "title": title,
                "content": cleaned_content,
                "source": "jina_reader",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_message = f"Error scraping webpage: {str(e)}"
            self.log(error_message)
            return {
                "status": "error",
                "message": error_message,
                "url": url,
                "source": "jina_reader",
                "timestamp": datetime.now().isoformat()
            }
    
    def multi_search(self, query: str) -> Dict[str, Any]:
        """
        Perform searches using multiple methods in parallel.
        
        Args:
            query: The search query
            
        Returns:
            Dictionary with combined search results
        """
        self.log(f"Starting multi-search for: {query}")
        search_results = {}
        
        # Define search tasks to run in parallel
        search_tasks = {
            "grok": lambda: self.search_with_grok(query),
            "google": lambda: self.search_with_searxng(query, "google"),
            "bing": lambda: self.search_with_searxng(query, "bing"),
        }
        
        # Add OpenAI search if API key is available
        if self.openai_api_key:
            search_tasks["openai"] = lambda: self.search_with_openai(query)
        
        # Run search tasks in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all tasks
            future_to_source = {
                executor.submit(task): source
                for source, task in search_tasks.items()
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    result = future.result()
                    search_results[source] = result
                    if result["status"] == "success":
                        self.log(f"Successfully completed {source} search")
                    else:
                        self.log(f"Search failed for {source}: {result.get('message', 'Unknown error')}")
                except Exception as e:
                    self.log(f"Error in {source} search: {str(e)}")
                    search_results[source] = {
                        "status": "error",
                        "message": str(e),
                        "source": source,
                        "timestamp": datetime.now().isoformat()
                    }
        
        return {
            "status": "success",
            "query": query,
            "results": search_results,
            "timestamp": datetime.now().isoformat()
        }
    
    def extract_urls_from_search(self, search_results: Dict[str, Any], max_urls: int = 3) -> List[str]:
        """
        Extract URLs from search results for further processing.
        
        Args:
            search_results: Results from multi_search
            max_urls: Maximum number of URLs to extract
            
        Returns:
            List of URLs
        """
        all_urls = []
        
        # Extract URLs from SearXNG results
        for engine in ["google", "bing"]:
            if engine in search_results["results"] and search_results["results"][engine]["status"] == "success":
                engine_results = search_results["results"][engine]
                if "results" in engine_results and isinstance(engine_results["results"], list):
                    for result in engine_results["results"]:
                        if "url" in result and result["url"] not in all_urls:
                            all_urls.append(result["url"])
        
        # Extract URLs from Grok and OpenAI results (looking for URLs in text)
        for source in ["grok", "openai"]:
            if source in search_results["results"] and search_results["results"][source]["status"] == "success":
                content = search_results["results"][source].get("results", "")
                if content:
                    # Find URLs in the text
                    urls = re.findall(r'https?://[^\s)\]]+', content)
                    for url in urls:
                        if url not in all_urls:
                            all_urls.append(url)
        
        # Return top URLs, prioritizing unique domains
        unique_domains = {}
        result_urls = []
        
        for url in all_urls:
            domain = urlparse(url).netloc
            if domain not in unique_domains and len(result_urls) < max_urls:
                unique_domains[domain] = True
                result_urls.append(url)
        
        return result_urls[:max_urls]
    
    def unified_search(self, query: str, strategy: str = "full") -> Dict[str, Any]:
        """
        Perform a unified search using multiple strategies.
        
        Args:
            query: The search query
            strategy: Search strategy ("quick", "basic", "full")
                - quick: Just use one search source (fastest)
                - basic: Use multiple search engines without scraping (moderate)
                - full: Use all search methods + scrape top results (comprehensive)
            
        Returns:
            Dictionary with combined search results
        """
        self.log(f"Starting unified search with {strategy} strategy for: {query}")
        
        try:
            # For quick searches, just use one source
            if strategy == "quick":
                # Try OpenAI first if available, fall back to Grok
                if self.openai_api_key:
                    results = {"openai": self.search_with_openai(query)}
                else:
                    results = {"grok": self.search_with_grok(query)}
                
                return {
                    "status": "success",
                    "query": query,
                    "strategy": strategy,
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                }
            
            # For other strategies, use multi-search
            search_results = self.multi_search(query)
            
            # For full strategy, also scrape top URLs
            if strategy == "full":
                # Extract URLs from search results
                urls_to_scrape = self.extract_urls_from_search(search_results)
                
                # Scrape each URL
                scraped_pages = []
                for url in urls_to_scrape:
                    try:
                        self.log(f"Scraping URL: {url}")
                        scraped_content = self.scrape_webpage(url)
                        if scraped_content["status"] == "success":
                            scraped_pages.append(scraped_content)
                        
                        # Rate limiting
                        time.sleep(1)
                    except Exception as e:
                        self.log(f"Error scraping {url}: {str(e)}")
                
                # Add scraped pages to results
                search_results["scraped_pages"] = scraped_pages
            
            return {
                "status": "success",
                "query": query,
                "strategy": strategy,
                "results": search_results["results"],
                "scraped_pages": search_results.get("scraped_pages", []),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_message = f"Error in unified search: {str(e)}"
            self.log(error_message)
            return {
                "status": "error",
                "message": error_message,
                "query": query,
                "strategy": strategy,
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_combined_response(self, search_results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive response from multiple search results.
        
        Args:
            search_results: Results from unified_search
            
        Returns:
            Combined search response
        """
        self.log("Generating combined response from search results")
        
        if search_results["status"] != "success":
            return f"Error performing search: {search_results.get('message', 'Unknown error')}"
        
        # First check if we have any successful results
        has_successful_results = False
        for source, result in search_results["results"].items():
            if result["status"] == "success":
                has_successful_results = True
                break
        
        if not has_successful_results:
            return f"No successful search results found for: {search_results['query']}"
        
        # Extract the best result - prioritize OpenAI > Grok > Others
        best_content = None
        if "openai" in search_results["results"] and search_results["results"]["openai"]["status"] == "success":
            best_content = search_results["results"]["openai"]["results"]
        elif "grok" in search_results["results"] and search_results["results"]["grok"]["status"] == "success":
            best_content = search_results["results"]["grok"]["results"]
        
        # If no best content yet, try to extract from other sources
        if not best_content:
            for source, result in search_results["results"].items():
                if result["status"] == "success" and "results" in result:
                    if isinstance(result["results"], str):
                        best_content = result["results"]
                        break
        
        # If still no content, return error
        if not best_content:
            return f"Could not extract content from search results for: {search_results['query']}"
        
        # Include metadata about scraped pages if available
        source_info = ""
        if "scraped_pages" in search_results and search_results["scraped_pages"]:
            source_info = "\n\nSources:\n"
            for page in search_results["scraped_pages"]:
                if page["status"] == "success":
                    source_info += f"- {page['title']} ({page['domain']})\n"
        
        return best_content + source_info
    
    def get_search_summary(self, search_results: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary from search results.
        
        Args:
            search_results: Results from unified_search
            
        Returns:
            Formatted summary text
        """
        if search_results["status"] != "success":
            return f"Error performing search: {search_results.get('message', 'Unknown error')}"
        
        summary = f"Search results for: {search_results['query']}\n\n"
        
        # Add results from each search engine
        for source, result in search_results["results"].items():
            if result["status"] == "success":
                summary += f"{source.upper()} SEARCH RESULTS:\n"
                summary += "-" * 40 + "\n"
                
                if source in ["openai", "grok"]:
                    # Direct content from AI models
                    content = result.get("results", "No content available")
                    summary += content + "\n\n"
                elif source in ["google", "bing", "duckduckgo"]:
                    # Structured results from search engines
                    if "results" in result and isinstance(result["results"], list):
                        for item in result["results"][:3]:  # Show top 3 results
                            summary += f"Title: {item['title']}\n"
                            summary += f"URL: {item['url']}\n"
                            summary += f"Snippet: {item['snippet']}\n\n"
                    else:
                        summary += "No structured results available\n\n"
        
        # Add scraped page summaries
        if "scraped_pages" in search_results and search_results["scraped_pages"]:
            summary += "SCRAPED WEBPAGES:\n"
            summary += "-" * 40 + "\n"
            
            for page in search_results["scraped_pages"]:
                if page["status"] == "success":
                    summary += f"Title: {page['title']}\n"
                    summary += f"URL: {page['url']}\n"
                    # Include a brief excerpt (first 200 chars)
                    content_excerpt = page['content'][:200] + "..." if len(page['content']) > 200 else page['content']
                    summary += f"Content excerpt: {content_excerpt}\n\n"
        
        return summary

# Example usage if run directly
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Web Search Tools")
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--xai-key", dest="api_key", help="X.AI API key")
    parser.add_argument("--openai-key", dest="openai_api_key", help="OpenAI API key")
    parser.add_argument("--strategy", choices=["quick", "basic", "full"], 
                        default="full", help="Search strategy")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--format", choices=["summary", "combined"], default="summary",
                        help="Output format (summary or combined response)")
    
    args = parser.parse_args()
    
    search_tools = WebSearchTools(
        api_key=args.api_key,
        openai_api_key=args.openai_api_key,
        verbose=args.verbose
    )
    
    if args.query:
        query = " ".join(args.query)
        print(f"Searching for: {query}")
        results = search_tools.unified_search(query, strategy=args.strategy)
        
        if args.format == "summary":
            output = search_tools.get_search_summary(results)
        else:
            output = search_tools.generate_combined_response(results)
            
        print("\nSEARCH RESULTS:")
        print("=" * 80)
        print(output)
    else:
        # Interactive mode
        print("Advanced Web Search Tools")
        print("=" * 50)
        print("Enter a search query or 'quit' to exit")
        
        while True:
            try:
                query = input("\nSearch query: ").strip()
                if query.lower() in ["quit", "exit", "q"]:
                    break
                
                if query:
                    results = search_tools.unified_search(query, strategy=args.strategy)
                    
                    if args.format == "summary":
                        output = search_tools.get_search_summary(results)
                    else:
                        output = search_tools.generate_combined_response(results)
                        
                    print("\nSEARCH RESULTS:")
                    print("=" * 80)
                    print(output)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {str(e)}") 