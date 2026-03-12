#!/usr/bin/env python3
"""
XAI Code Explainer
Uses the X.AI API to explain code snippets and generate documentation.

Usage:
  python xai_code_explain.py [file_path] [--verbose] [--output OUTPUT]
  
Example:
  python xai_code_explain.py xai_unified.py --output xai_unified_explained.md
"""

import os
import sys
import argparse
from xai_unified import XAIUnified

def read_file(file_path):
    """Read the contents of a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

def split_into_chunks(code, max_chunk_size=6000):
    """Split code into manageable chunks."""
    lines = code.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_size = len(line)
        if current_size + line_size > max_chunk_size and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
            current_size = 0
        
        current_chunk.append(line)
        current_size += line_size
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

def explain_code(xai, code, verbose=False):
    """
    Generate an explanation for a code snippet using X.AI.
    
    Args:
        xai: The XAIUnified instance
        code: The code to explain
        verbose: Whether to print detailed information
        
    Returns:
        The generated explanation
    """
    # Create a custom system prompt
    system_prompt = (
        "You are a helpful coding assistant specializing in explaining code. "
        "When presented with code, you provide clear, detailed explanations that include:"
        "\n1. Overall purpose of the code"
        "\n2. Key functions/classes and their roles"
        "\n3. Flow of execution"
        "\n4. Important design patterns or techniques used"
        "\n5. Potential issues or improvements"
        "\nYour explanations are thorough but concise, focusing on the most important aspects."
    )
    
    # Save the current conversation
    old_conversation = xai.conversation_history.copy()
    
    # Set up a new conversation with our custom prompt
    xai.conversation_history = [{"role": "system", "content": system_prompt}]
    
    # Create the user message
    user_message = f"Please explain this code thoroughly:\n\n```\n{code}\n```"
    
    # Add the user message to conversation
    xai.conversation_history.append({"role": "user", "content": user_message})
    
    if verbose:
        print("Sending code to X.AI for explanation...")
        print(f"Code length: {len(code)} characters")
    
    # Get a non-streaming response
    try:
        response = xai.client.chat.completions.create(
            model="grok-2-latest",
            messages=xai.conversation_history,
            temperature=0.3,
        )
        
        explanation = response.choices[0].message.content
        
        # Restore the previous conversation
        xai.conversation_history = old_conversation
        
        return explanation
        
    except Exception as e:
        print(f"Error explaining code: {e}", file=sys.stderr)
        # Restore the previous conversation
        xai.conversation_history = old_conversation
        return f"Error: {e}"

def explain_file(file_path, verbose=False, output=None):
    """
    Generate an explanation for the code in a file.
    
    Args:
        file_path: Path to the file containing code
        verbose: Whether to print detailed information
        output: Path to output file (if specified)
        
    Returns:
        The generated explanation
    """
    # Initialize X.AI client
    api_key = os.getenv("XAI_API_KEY")
    xai = XAIUnified(api_key=api_key)
    
    # Read the file
    if verbose:
        print(f"Reading file: {file_path}")
    code = read_file(file_path)
    
    # If the code is very long, split it into chunks
    if len(code) > 6000:
        if verbose:
            print(f"Code is large ({len(code)} chars). Splitting into chunks for analysis.")
        
        chunks = split_into_chunks(code)
        explanations = []
        
        for i, chunk in enumerate(chunks):
            if verbose:
                print(f"Processing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
            
            chunk_explanation = explain_code(xai, chunk, verbose)
            explanations.append(chunk_explanation)
        
        # Combine the explanations
        # Add a custom system prompt for summarizing
        system_prompt = (
            "You are a coding expert who can synthesize multiple explanations of code chunks "
            "into a cohesive, comprehensive explanation of the entire codebase. "
            "Eliminate redundancies and create a unified, structured explanation."
        )
        
        xai.conversation_history = [{"role": "system", "content": system_prompt}]
        
        combined_explanations = "\n\n===== CHUNK DIVISION =====\n\n".join(explanations)
        user_message = (
            f"The following text contains explanations of different chunks of the same code file: {file_path}\n"
            f"Please synthesize these explanations into a single, comprehensive explanation "
            f"of the entire file, eliminating redundancies and creating a cohesive structure.\n\n"
            f"{combined_explanations}"
        )
        
        xai.conversation_history.append({"role": "user", "content": user_message})
        
        if verbose:
            print("Synthesizing chunk explanations into a unified explanation...")
        
        response = xai.client.chat.completions.create(
            model="grok-2-latest",
            messages=xai.conversation_history,
            temperature=0.3,
        )
        
        final_explanation = response.choices[0].message.content
    
    else:
        # For shorter code, just explain it directly
        final_explanation = explain_code(xai, code, verbose)
    
    # Format the output
    file_name = os.path.basename(file_path)
    formatted_output = f"# Code Explanation: {file_name}\n\n{final_explanation}"
    
    # Output the explanation
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        if verbose:
            print(f"Explanation written to {output}")
    else:
        print("\n" + "=" * 80)
        print(f"CODE EXPLANATION: {file_name}")
        print("=" * 80 + "\n")
        print(formatted_output)
    
    return formatted_output

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="X.AI Code Explainer")
    parser.add_argument("file", help="Path to the code file to explain")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed information")
    parser.add_argument("--output", "-o", help="Path to output file")
    
    args = parser.parse_args()
    
    explain_file(args.file, args.verbose, args.output)

if __name__ == "__main__":
    main() 