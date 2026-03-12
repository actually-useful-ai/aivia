#!/usr/bin/env python3
"""
Simple OpenAI API Ping Tool
Quick utility to test OpenAI API connectivity and list available models.
"""

import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Install with: pip install openai")
    sys.exit(1)


def ping_openai(api_key=None):
    """
    Ping OpenAI API and list available models.
    
    Args:
        api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
    """
    # Get API key
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: No API key provided. Set OPENAI_API_KEY environment variable or pass as argument.")
        return False
    
    try:
        print("🔄 Connecting to OpenAI API...")
        client = OpenAI(api_key=api_key)
        
        # Test API connectivity by listing models
        print("✅ Connection successful!\n")
        print("📋 Available GPT Models:")
        print("-" * 50)
        
        models = client.models.list()
        gpt_models = [m for m in models.data if any(x in m.id.lower() for x in ["gpt-4", "gpt-3.5"])]
        gpt_models.sort(key=lambda x: x.id, reverse=True)
        
        for model in gpt_models:
            print(f"  • {model.id}")
        
        print("\n" + "=" * 50)
        print(f"Total GPT models: {len(gpt_models)}")
        
        # Test a simple completion
        print("\n🧪 Testing with a simple completion...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=20,
            messages=[{"role": "user", "content": "Say 'API test successful!' and nothing else."}]
        )
        
        result = response.choices[0].message.content
        print(f"✅ Response: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test OpenAI API connectivity")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    args = parser.parse_args()
    
    success = ping_openai(api_key=args.api_key)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
