#!/usr/bin/env python3
"""
Perplexity Multi-Search CLI (v2 - using shared/utils)

Thin CLI wrapper around shared/utils/multi_search.py for comprehensive web research.

Usage:
    python perplexity_multi_v2.py "quantum computing applications"
    python perplexity_multi_v2.py "climate change solutions" --output report.txt
    python perplexity_multi_v2.py --raw "AI safety research"

Author: Luke Steuber
"""

import sys
import argparse
import json
from pathlib import Path

# Add shared library to path
sys.path.insert(0, str(Path.home() / "shared"))

try:
    from utils import multi_search, MultiSearchOrchestrator
except ImportError as e:
    print(f"Missing required package: {e}")
    print("\nInstall required packages with:")
    print("pip install requests")
    sys.exit(1)


def main():
    """CLI interface for multi-search."""
    parser = argparse.ArgumentParser(
        description="Search the web using Perplexity AI with multi-query orchestration (v2 - using shared/utils)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic search with comprehensive report
  %(prog)s "quantum computing applications"

  # Save report to file
  %(prog)s "climate change solutions" --output report.txt

  # Get raw JSON response
  %(prog)s --raw "AI safety research"

  # Specify number of search queries
  %(prog)s "machine learning trends" --num-queries 7

Note: This is a thin wrapper around shared/utils/multi_search.py
Set PERPLEXITY_API_KEY environment variable for authentication.
        """
    )

    parser.add_argument("query", nargs="*", help="The search query")
    parser.add_argument("--api-key", help="Perplexity API key (or set PERPLEXITY_API_KEY env var)")
    parser.add_argument("--output", help="Output file for the report (default: print to console)")
    parser.add_argument("--raw", action="store_true", help="Output raw JSON response")
    parser.add_argument("--num-queries", type=int, default=5, help="Number of search queries to generate (default: 5)")

    args = parser.parse_args()

    # Get query
    if not args.query:
        query = input("Enter search query: ")
    else:
        query = " ".join(args.query)

    if not query.strip():
        print("Error: Query cannot be empty")
        sys.exit(1)

    # Progress callbacks for user feedback
    def on_queries_generated(queries):
        print(f"\nGenerated {len(queries)} search queries:")
        for i, q in enumerate(queries, 1):
            print(f"{i}. {q.text}")
        print()

    def on_search_complete(result):
        print(f"✓ Completed search {result.query.index + 1}/{result.query.total}: {result.query.text}")

    # Perform multi-search
    try:
        print(f"Generating comprehensive research report for: {query}\n")

        result = multi_search(
            topic=query,
            num_queries=args.num_queries,
            api_key=args.api_key,
            on_queries_generated=on_queries_generated,
            on_search_complete=on_search_complete
        )

        if not result.success:
            print(f"\n❌ Error: {result.error}")
            sys.exit(1)

        print("\n" + "="*80)
        print("Generating comprehensive report...")
        print("="*80 + "\n")

        # Format output
        if args.raw:
            output = json.dumps({
                "original_query": result.original_query,
                "generated_queries": [q.text for q in result.generated_queries],
                "search_results": [
                    {
                        "query": sr.query.text,
                        "success": sr.success,
                        "content": sr.content,
                        "citations": sr.citations
                    }
                    for sr in result.search_results
                ],
                "final_report": result.final_report,
                "success": result.success
            }, indent=2)
        else:
            output = result.final_report

        # Output to file or console
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output, encoding="utf-8")
            print(f"✅ Report saved to {args.output}")
        else:
            print("\n" + "="*80 + "\n")
            print(output)
            print("\n" + "="*80 + "\n")

        # Show citations if available
        if not args.raw and result.search_results:
            all_citations = []
            for sr in result.search_results:
                all_citations.extend(sr.citations)

            if all_citations:
                print("\n" + "="*80)
                print(f"Sources ({len(all_citations)} citations):")
                print("="*80)
                for i, citation in enumerate(set(all_citations), 1):
                    print(f"{i}. {citation}")
                print()

        return 0

    except KeyboardInterrupt:
        print("\n\n❌ Search cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
