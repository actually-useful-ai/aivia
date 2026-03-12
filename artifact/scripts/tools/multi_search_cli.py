#!/usr/bin/env python3
"""
Multi-Provider Web Search CLI Tool

This script provides a command-line interface for testing the
multi-provider web search functionality.
"""

import os
import sys
import json
import argparse
from multi_search import MultiSearcher, LlmAssistantFormatter

def main():
    """Command-line interface for MultiSearcher."""
    parser = argparse.ArgumentParser(
        description='Search the web using multiple providers in parallel.'
    )
    
    # Required arguments
    parser.add_argument('query', nargs='?', help='The search query')
    
    # Optional arguments
    parser.add_argument(
        '--providers', 
        help='Comma-separated list of providers to use (duckduckgo,websearchtools,openai,searxng,xai,serp)'
    )
    parser.add_argument(
        '--api-key', 
        help='API key for search services (will use env vars if not provided)'
    )
    parser.add_argument(
        '--timeout', 
        type=int, 
        default=30, 
        help='Timeout in seconds for search requests'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed success/failure information for each provider'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode (prompt for queries)'
    )
    parser.add_argument(
        '--llm-format', '-l',
        action='store_true',
        help='Format output specifically for LLM assistants'
    )
    parser.add_argument(
        '--raw',
        action='store_true',
        help='Return raw results without any guidance for assistants'
    )
    
    args = parser.parse_args()
    
    # Handle special commands
    if len(sys.argv) == 2 and sys.argv[1] == "--example":
        demonstrate_llm_usage()
        return 0
    
    # Handle interactive mode
    if args.interactive:
        return run_interactive_mode(args)
        
    # Check if a query was provided
    if not args.query:
        parser.print_help()
        print("\nError: A search query is required unless using interactive mode.")
        return 1
    
    # Parse providers if provided
    providers = None
    if args.providers:
        providers = [p.strip() for p in args.providers.split(',')]
    
    # Create the searcher
    searcher = MultiSearcher(api_key=args.api_key, timeout=args.timeout)
    
    # Use asyncio to run the search
    import asyncio
    
    async def run_search():
        try:
            return await searcher.search(query=args.query, providers=providers, for_assistant=not args.raw)
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
    
    # Run the async function using asyncio.run()
    try:
        results = asyncio.run(run_search())
        
        if not results:
            return 1
            
        # Output results
        if args.json:
            # Output raw JSON format
            print(json.dumps(results, indent=2))
        elif args.llm_format:
            # Format specifically for LLM assistants
            formatted_text = LlmAssistantFormatter.format_results_for_llm(results, args.query)
            print(formatted_text)
        else:
            # Output formatted results
            if results["success"]:
                print(f"Search results for: {args.query}\n")
                
                if args.verbose:
                    # Show provider summary
                    print("Provider summary:")
                    for provider, result in results["provider_results"].items():
                        status = "✓ Success" if result.get("success") else "✗ Failed"
                        if not result.get("success"):
                            status += f" ({result.get('error')})"
                        print(f"  {provider}: {status}")
                    print("\n" + "-" * 50 + "\n")
                
                print(results["combined_text"])
            else:
                print(f"All search methods failed for query: {args.query}")
                if args.verbose or True:  # Always show errors if all providers failed
                    for provider, result in results["provider_results"].items():
                        print(f"  {provider}: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

def run_interactive_mode(args):
    """Run the tool in interactive mode, prompting for queries."""
    import asyncio
    
    print("Multi-Provider Web Search Interactive Mode")
    print("Enter your search queries below, or type 'exit' to quit.")
    print("Type 'providers' to see or change active providers.")
    print("Type 'format' to toggle LLM formatting.")
    print("-" * 50)
    
    # Parse initial providers if provided
    providers = None
    if args.providers:
        providers = [p.strip() for p in args.providers.split(',')]
    
    # Create the searcher
    searcher = MultiSearcher(api_key=args.api_key, timeout=args.timeout)
    
    # Initial LLM formatting setting
    use_llm_format = args.llm_format
    raw_mode = args.raw
    
    # Define async search function
    async def perform_search(query, providers_list):
        return await searcher.search(query, providers=providers_list, for_assistant=not raw_mode)
    
    while True:
        try:
            # Get user input
            user_input = input("\nSearch query: ")
            user_input = user_input.strip()
            
            # Check if user wants to exit
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Exiting web search tool.")
                break
                
            # Check if user wants to manage providers
            if user_input.lower() == 'providers':
                providers = manage_providers(providers)
                continue
                
            # Check if user wants to toggle LLM formatting
            if user_input.lower() == 'format':
                use_llm_format = not use_llm_format
                print(f"LLM formatting is now: {'ON' if use_llm_format else 'OFF'}")
                continue
                
            # Check if user wants to toggle raw mode
            if user_input.lower() == 'raw':
                raw_mode = not raw_mode
                print(f"Raw mode (no guidance) is now: {'ON' if raw_mode else 'OFF'}")
                continue
                
            # Skip empty queries
            if not user_input:
                continue
                
            # Run the search
            print(f"\nSearching for: {user_input}")
            print("-" * 50)
            
            try:
                # Run the async search using asyncio.run()
                results = asyncio.run(perform_search(user_input, providers))
                
                # Output results
                if results["success"]:
                    # Show provider summary
                    print("Provider summary:")
                    for provider, result in results["provider_results"].items():
                        status = "✓ Success" if result.get("success") else "✗ Failed"
                        if not result.get("success") and args.verbose:
                            status += f" ({result.get('error')})"
                        print(f"  {provider}: {status}")
                    print("\n" + "-" * 50 + "\n")
                    
                    if use_llm_format:
                        # Format specifically for LLM assistants
                        formatted_text = LlmAssistantFormatter.format_results_for_llm(results, user_input)
                        print(formatted_text)
                    else:
                        print(results["combined_text"])
                else:
                    print("All search methods failed.")
                    for provider, result in results["provider_results"].items():
                        print(f"  {provider}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"Error during search: {str(e)}")
                    
        except KeyboardInterrupt:
            print("\nSearch interrupted. Type 'exit' to quit.")
            continue
        except Exception as e:
            print(f"Error: {str(e)}")
    
    return 0

def manage_providers(current_providers=None):
    """Allow the user to view and change active providers."""
    all_providers = ["duckduckgo", "websearchtools", "openai", "searxng", "xai", "serp"]
    
    if current_providers is None:
        current_providers = all_providers.copy()
    
    print("\nCurrent active providers:")
    for i, provider in enumerate(all_providers, 1):
        status = "✓ Active" if provider in current_providers else "✗ Inactive"
        print(f"  {i}. {provider} - {status}")
    
    print("\nOptions:")
    print("  a. Enable all providers")
    print("  n. Enable none (must select individually)")
    print("  b. Back to search")
    print("  Or enter provider numbers to toggle (e.g., '1 3' to toggle first and third)")
    
    choice = input("\nEnter your choice: ").strip().lower()
    
    if choice == 'a':
        return all_providers.copy()
    elif choice == 'n':
        return []
    elif choice == 'b':
        return current_providers
    else:
        # Parse numbers and toggle providers
        try:
            selected = [int(num) for num in choice.split() if num.isdigit()]
            
            for num in selected:
                if 1 <= num <= len(all_providers):
                    provider = all_providers[num-1]
                    if provider in current_providers:
                        current_providers.remove(provider)
                    else:
                        current_providers.append(provider)
        except ValueError:
            print("Invalid input. Provider list unchanged.")
    
    # Show the updated list
    print("\nUpdated provider list:")
    for provider in all_providers:
        status = "✓ Active" if provider in current_providers else "✗ Inactive"
        print(f"  {provider} - {status}")
    
    return current_providers

def demonstrate_llm_usage():
    """
    Demonstrate how to use the search results with an LLM assistant.
    
    This is a code example that shows how to properly pass search results to an LLM.
    """
    print("Example code for using search results with an LLM assistant:\n")
    example = '''
# Example of using search results with an LLM assistant
from multi_search import MultiSearcher, LlmAssistantFormatter
from openai import OpenAI  # Or any other LLM client

# 1. Create the searcher and run a search
searcher = MultiSearcher(api_key="your_api_key")
query = "latest developments in AI safety"
search_results = searcher.search(query)

# 2. Format the results for the LLM
formatted_context = LlmAssistantFormatter.format_results_for_llm(search_results, query)

# 3. Create chat messages with the formatted context as system message
messages = [
    {"role": "system", "content": formatted_context},
    {"role": "user", "content": f"Please summarize what you know about: {query}"}
]

# 4. Call the LLM with the prepared messages
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages
)

# 5. Display the LLM response
print(response.choices[0].message.content)
'''
    print(example)
    
if __name__ == "__main__":
    sys.exit(main() or 0) 