#!/usr/bin/env python3
"""
ArXiv Paper Search CLI
Simple tool for searching and retrieving academic papers from ArXiv.
"""

import os
import sys
import argparse
from datetime import datetime

try:
    import arxiv
except ImportError:
    print("Error: arxiv package not installed. Install with: pip install arxiv")
    sys.exit(1)


def format_paper(paper, index=None):
    """Format a paper for display"""
    output = []
    if index:
        output.append(f"\n{'='*70}")
        output.append(f"Paper #{index}")
        output.append('='*70)
    
    output.append(f"Title: {paper.title}")
    output.append(f"Authors: {', '.join(author.name for author in paper.authors)}")
    output.append(f"Published: {paper.published.strftime('%Y-%m-%d')}")
    output.append(f"Updated: {paper.updated.strftime('%Y-%m-%d')}")
    output.append(f"ArXiv ID: {paper.entry_id.split('/')[-1]}")
    output.append(f"PDF: {paper.pdf_url}")
    output.append(f"Categories: {', '.join(paper.categories)}")
    output.append(f"\nAbstract:\n{paper.summary}")
    
    return '\n'.join(output)


def search_arxiv(query, max_results=5, sort_by="relevance"):
    """
    Search ArXiv for papers.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        sort_by: Sort order (relevance or lastUpdatedDate)
    """
    try:
        print(f"🔍 Searching ArXiv for: '{query}'")
        print(f"📊 Max results: {max_results}, Sort by: {sort_by}\n")
        
        # Create search
        sort_criterion = arxiv.SortCriterion.Relevance if sort_by == "relevance" else arxiv.SortCriterion.LastUpdatedDate
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_criterion
        )
        
        # Get results
        client = arxiv.Client()
        papers = list(client.results(search))
        
        if not papers:
            print(f"❌ No papers found for query: '{query}'")
            return False
        
        print(f"✅ Found {len(papers)} paper(s)\n")
        
        # Display results
        for i, paper in enumerate(papers, 1):
            print(format_paper(paper, i))
        
        # Summary
        print(f"\n{'='*70}")
        print(f"📚 Total papers retrieved: {len(papers)}")
        print('='*70)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def get_paper_by_id(paper_id):
    """
    Get a specific paper by its ArXiv ID.
    
    Args:
        paper_id: ArXiv paper ID (e.g., 2301.07041)
    """
    try:
        print(f"🔍 Fetching ArXiv paper: {paper_id}")
        
        # Search for specific paper
        search = arxiv.Search(id_list=[paper_id])
        client = arxiv.Client()
        papers = list(client.results(search))
        
        if not papers:
            print(f"❌ Paper not found: {paper_id}")
            return False
        
        paper = papers[0]
        print(f"✅ Paper found\n")
        print(format_paper(paper))
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def interactive_mode():
    """Interactive ArXiv search mode"""
    print("\n" + "="*70)
    print("ArXiv Paper Search - Interactive Mode")
    print("="*70)
    print("Commands:")
    print("  search <query>  - Search for papers")
    print("  get <id>        - Get paper by ArXiv ID")
    print("  help            - Show this help")
    print("  quit/exit       - Exit interactive mode")
    print("="*70 + "\n")
    
    while True:
        try:
            user_input = input("arxiv> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\nCommands:")
                print("  search <query>  - Search for papers")
                print("  get <id>        - Get paper by ArXiv ID")
                print("  help            - Show this help")
                print("  quit/exit       - Exit interactive mode\n")
                continue
            
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            
            if command == 'search' and len(parts) > 1:
                query = parts[1]
                max_results = input("Max results [5]: ").strip() or "5"
                sort_by = input("Sort by (relevance/date) [relevance]: ").strip() or "relevance"
                print()
                search_arxiv(query, int(max_results), sort_by)
                
            elif command == 'get' and len(parts) > 1:
                paper_id = parts[1]
                print()
                get_paper_by_id(paper_id)
                
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Search and retrieve academic papers from ArXiv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for papers
  %(prog)s --query "machine learning transformers"
  
  # Get specific paper by ID
  %(prog)s --id 2301.07041
  
  # Interactive mode
  %(prog)s --interactive
  
  # Search with more results
  %(prog)s --query "quantum computing" --max-results 10 --sort-by date
        """
    )
    
    parser.add_argument("-q", "--query", help="Search query")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--id", "--paper-id", dest="paper_id", help="Get specific paper by ArXiv ID")
    parser.add_argument("-n", "--max-results", type=int, default=5, help="Maximum number of results (default: 5)")
    parser.add_argument("-s", "--sort-by", choices=["relevance", "date"], default="relevance", 
                        help="Sort results by relevance or date (default: relevance)")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
        sys.exit(0)
    
    if args.paper_id:
        success = get_paper_by_id(args.paper_id)
        sys.exit(0 if success else 1)
    
    if args.query:
        success = search_arxiv(args.query, args.max_results, args.sort_by)
        sys.exit(0 if success else 1)
    
    # No arguments provided
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
