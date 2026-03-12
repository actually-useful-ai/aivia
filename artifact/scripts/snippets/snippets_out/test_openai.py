#!/usr/bin/env python3
"""
Simple test script to check OpenAI import functionality
"""
from openai import OpenAI

print("Successfully imported OpenAI class")

# Create a client instance (without making any API calls)
client = OpenAI(
    api_key="test-api-key",
    base_url="https://api.x.ai/v1",
)

print("Successfully created OpenAI client instance")
print(f"OpenAI client type: {type(client)}") 