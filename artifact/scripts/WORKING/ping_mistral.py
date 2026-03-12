#!/usr/bin/env python3
"""
Simple Mistral AI API Ping Tool
Quick utility to test Mistral AI API connectivity and list available models.
"""

import os
import sys

try:
    import requests
except ImportError:
    print("Error: requests package not installed. Install with: pip install requests")
    sys.exit(1)


def ping_mistral(api_key=None):
    """
    Ping Mistral AI API and list available models.
    
    Args:
        api_key: Mistral AI API key (uses MISTRAL_API_KEY env var if not provided)
    """
    # Get API key
    api_key = api_key or os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("Error: No API key provided. Set MISTRAL_API_KEY environment variable or pass as argument.")
        return False
    
    try:
        print("🔄 Connecting to Mistral AI API...")
        
        # Test API connectivity by listing models
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get("https://api.mistral.ai/v1/models", headers=headers)
        response.raise_for_status()
        
        print("✅ Connection successful!\n")
        print("📋 Available Mistral Models:")
        print("-" * 50)
        
        models = response.json().get("data", [])
        models.sort(key=lambda x: x.get("id", ""), reverse=True)
        
        for model in models:
            model_id = model.get("id", "Unknown")
            print(f"  • {model_id}")
        
        print("\n" + "=" * 50)
        print(f"Total models: {len(models)}")
        
        # Test a simple completion
        print("\n🧪 Testing with a simple completion...")
        chat_response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json={
                "model": "mistral-small-latest",
                "messages": [{"role": "user", "content": "Say 'API test successful!' and nothing else."}],
                "max_tokens": 20
            }
        )
        chat_response.raise_for_status()
        
        result = chat_response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"✅ Response: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Mistral AI API connectivity")
    parser.add_argument("--api-key", help="Mistral AI API key (or set MISTRAL_API_KEY env var)")
    args = parser.parse_args()
    
    success = ping_mistral(api_key=args.api_key)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
