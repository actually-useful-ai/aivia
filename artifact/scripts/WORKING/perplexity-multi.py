import requests
import argparse
import json
import sys
import os
from typing import List, Dict, Any, Optional


def perplexity_search(query: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Perform a comprehensive web search using Perplexity AI, with multiple queries
    to produce a thorough report.
    
    Args:
        query: The initial search query
        api_key: Perplexity API key (optional)
    
    Returns:
        The final search response
    """
    # Get API key from environment or argument
    if not api_key:
        api_key = os.environ.get("PERPLEXITY_API_KEY", "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")
    
    print(f"Generating search queries for: {query}")
    
    # Step 1: Generate multiple search queries using drummer function
    query_gen_prompt = f"Based on the query '{query}', create exactly 5 specific search queries that would help gather comprehensive information about this topic. Format your response as a JSON array of strings."
    query_gen_result = drummer(query_gen_prompt, api_key)
    
    # Extract the generated queries
    generated_queries = []
    if "choices" in query_gen_result and query_gen_result["choices"]:
        content = query_gen_result["choices"][0]["message"]["content"]
        
        # Try to parse JSON directly
        try:
            # Check if response contains a JSON array
            if "[" in content and "]" in content:
                json_str = content[content.find("["):content.rfind("]")+1]
                generated_queries = json.loads(json_str)
            else:
                # Extract queries with basic text parsing
                lines = content.strip().split("\n")
                for line in lines:
                    if line.strip().startswith(("1.", "2.", "3.", "4.", "5.")):
                        query_text = line.split(".", 1)[1].strip()
                        if query_text:
                            generated_queries.append(query_text)
        except json.JSONDecodeError:
            # Fall back to line-by-line parsing
            lines = content.strip().split("\n")
            for line in lines:
                if line.strip() and not line.startswith(("#", "-", "*")):
                    generated_queries.append(line.strip())
    
    # Ensure we have queries, or use original as fallback
    if not generated_queries:
        print("Could not generate multiple queries, using original query")
        generated_queries = [query]
    
    # Limit to 5 queries
    generated_queries = generated_queries[:5]
    
    print(f"Generated {len(generated_queries)} search queries:")
    for i, q in enumerate(generated_queries, 1):
        print(f"{i}. {q}")
    
    # Step 2: Execute each search query
    search_results = []
    for i, sub_query in enumerate(generated_queries, 1):
        print(f"Executing search {i}/{len(generated_queries)}: {sub_query}")
        result = belter(sub_query, api_key)
        search_results.append(result)
    
    # Step 3: Compile results into a comprehensive report
    print("Generating comprehensive report...")
    
    # Extract content from search results
    result_contents = []
    for i, result in enumerate(search_results):
        if "choices" in result and result["choices"]:
            content = result["choices"][0]["message"]["content"]
            result_contents.append(f"SEARCH RESULT #{i+1} (Query: {generated_queries[i]}):\n{content}")
    
    # Generate the report using camina
    combined_results = '\n\n'.join(result_contents)
    report_prompt = f"""
Create a comprehensive report about "{query}" based on the following search results:

{combined_results}

Provide a well-structured report with key findings, details, and conclusions.
"""
    
    final_result = camina(report_prompt, api_key)
    return final_result


### THIS FIRST ASSISTANT MUST BE PROMPTED TO CREATE FIVE POTENTIAL SEARCH QUERIES TO PRODUCE A COMPREHENSIVE REPORT
def drummer(query: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Perform a web search using Perplexity AI API.
    Used to generate multiple query variations for comprehensive research.
    
    Args:
        query: The search query
        api_key: Perplexity API key (optional)
    
    Returns:
        The search response
    """
    url = "https://api.perplexity.ai/chat/completions"
    
    if not api_key:
        api_key = os.environ.get("PERPLEXITY_API_KEY", "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")
    
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant specialized in creating targeted search queries. For any topic, create 5 specific search queries that would help gather comprehensive information."
            },
            {
                "role": "user",
                "content": f"{query}"
            }
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}", file=sys.stderr)
        sys.exit(1)


### FIVE OF THESE SHOULD THEN BE SENT BASED ON THE QUERIES CREATED BY THE FIRST ONE
def belter(query: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Perform a web search using Perplexity AI API.
    Used to execute individual search queries.
    
    Args:
        query: The search query
        api_key: Perplexity API key (optional)
    
    Returns:
        The search response
    """
    url = "https://api.perplexity.ai/chat/completions"
    
    if not api_key:
        api_key = os.environ.get("PERPLEXITY_API_KEY", "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")
    
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that searches the web for information. Be precise, thorough and concise."
            },
            {
                "role": "user",
                "content": f"Search for: {query}"
            }
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}", file=sys.stderr)
        sys.exit(1)


### THIS ASSISTANT THEN MUST RECEIVE ALL FIVE RESPONSES AND CREATE A COMPREHENSIVE REPORT
def camina(query: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Perform a web search using Perplexity AI API.
    Used to compile search results into a comprehensive report.
    
    Args:
        query: The combined search results prompt
        api_key: Perplexity API key (optional)
    
    Returns:
        The search response with the comprehensive report
    """
    url = "https://api.perplexity.ai/chat/completions"
    
    if not api_key:
        api_key = os.environ.get("PERPLEXITY_API_KEY", "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")
    
    payload = {
        "model": "sonar-pro",
        "max_tokens": 10000,
        "return_images": True,
        "web_search_options.search_context_size": "low",
        "stream": True,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant specialized in creating comprehensive research reports. Synthesize information from multiple sources into a well-structured report."
            },
            {
                "role": "user",
                "content": f"{query}"
            }
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Search the web using Perplexity AI")
    parser.add_argument("query", nargs="*", help="The search query")
    parser.add_argument("--api-key", help="Perplexity API key")
    parser.add_argument("--output", help="Output file for the report (default: print to console)")
    parser.add_argument("--raw", action="store_true", help="Output raw JSON response")
    
    args = parser.parse_args()
    
    if not args.query:
        query = input("Enter search query: ")
    else:
        query = " ".join(args.query)
    
    result = perplexity_search(query, args.api_key)
    
    # Format and output the result
    if args.raw:
        output = json.dumps(result, indent=2)
    elif "choices" in result and result["choices"]:
        output = result["choices"][0]["message"]["content"]
    else:
        output = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print("\n" + "="*80 + "\n")
        print(output)
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()