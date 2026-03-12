#!/usr/bin/env python3
"""
XAI Agent - Simplified agent that works with X.AI API

This agent directly connects to the X.AI API with hardcoded credentials,
avoiding the environment variable issues in the main Swarm codebase.
"""

import os
import sys
import json
import requests
import argparse
from typing import Dict, List, Any, Optional

# X.AI API key from environment variable
XAI_API_KEY = os.getenv("XAI_API_KEY", "")

# API endpoint for X.AI
XAI_API_ENDPOINT = "https://api.x.ai/v1/chat/completions"

class XAIAgent:
    """
    Simple X.AI agent for direct API access
    """
    
    def __init__(self, api_key=None, model="grok-3", temperature=0.7, max_tokens=1000):
        """Initialize the agent"""
        self.api_key = api_key or XAI_API_KEY
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.conversation = []
        
        # Prepare headers
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def query(self, prompt):
        """Send a query to the X.AI API"""
        # Add to conversation history
        self.conversation.append({"role": "user", "content": prompt})
        
        # Create messages array
        messages = self.conversation.copy()
        
        # Create payload
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        try:
            print(f"Sending request to X.AI API using model: {self.model}...")
            response = requests.post(
                XAI_API_ENDPOINT,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Add to conversation history
                self.conversation.append({"role": "assistant", "content": content})
                
                # Return content
                return content
            else:
                error = f"Error ({response.status_code}): {response.text}"
                print(error)
                return error
        except Exception as e:
            error = f"Error: {str(e)}"
            print(error)
            return error
    
    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation = []
        print("Conversation history cleared.")

def main():
    """Run the X.AI agent CLI"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="X.AI Agent CLI")
    parser.add_argument("--model", default="grok-3", help="Model to use")
    parser.add_argument("--temp", type=float, default=0.7, help="Temperature")
    parser.add_argument("--max-tokens", type=int, default=1000, help="Max tokens")
    parser.add_argument("--query", help="Single query to run (non-interactive mode)")
    args = parser.parse_args()
    
    # Create agent
    agent = XAIAgent(
        model=args.model,
        temperature=args.temp,
        max_tokens=args.max_tokens
    )
    
    # If a query was provided, run it and exit
    if args.query:
        response = agent.query(args.query)
        print(f"\n{response}")
        return
    
    # Otherwise, run interactive CLI
    print("\n===== X.AI Agent CLI =====")
    print("Type 'exit' or 'quit' to end the session.")
    print("Type 'clear' to clear conversation history.")
    print(f"Using model: {args.model}\n")
    
    while True:
        try:
            # Get user query
            query = input("\n> ")
            
            # Check for exit command
            if query.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break
            
            # Check for clear command
            if query.lower() == "clear":
                agent.clear_conversation()
                continue
            
            # Skip empty queries
            if not query.strip():
                continue
            
            # Send the query to the API
            response = agent.query(query)
            
            # Print the response
            print(f"\n{response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 