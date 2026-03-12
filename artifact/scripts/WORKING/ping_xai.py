#!/usr/bin/env python3
"""
Simple XAI (Grok) API Ping Tool
Quick utility to test XAI/Grok API connectivity and list available models.
"""

import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Install with: pip install openai")
    sys.exit(1)


def ping_xai(api_key=None):
    """
    Ping XAI API and list available Grok models.
    
    Args:
        api_key: XAI API key (uses XAI_API_KEY env var if not provided)
    """
    # Get API key
    api_key = api_key or os.getenv("XAI_API_KEY")
    if not api_key:
        print("Error: No API key provided. Set XAI_API_KEY environment variable or pass as argument.")
        return False
    
    try:
        print("🔄 Connecting to XAI (Grok) API...")
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        
        # Test API connectivity by listing models
        print("✅ Connection successful!\n")
        print("📋 Available Grok Models:")
        print("-" * 50)
        
        models = client.models.list()
        
        for model in models.data:
            capabilities = []
            if "vision" in model.id.lower():
                capabilities.append("vision")
            if "grok-3" in model.id:
                capabilities.append("web-search")
            capabilities_text = f" [{', '.join(capabilities)}]" if capabilities else ""
            
            print(f"  • {model.id}{capabilities_text}")
        
        print("\n" + "=" * 50)
        print(f"Total models: {len(models.data)}")
        
        # Test a simple completion
        print("\n🧪 Testing with a simple completion...")
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "user", "content": "Say 'API test successful!' and nothing else."}],
            max_tokens=10
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
    
    parser = argparse.ArgumentParser(description="Test XAI Grok API connectivity")
    parser.add_argument("--api-key", help="XAI API key (or set XAI_API_KEY env var)")
    args = parser.parse_args()
    
    success = ping_xai(api_key=args.api_key)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
