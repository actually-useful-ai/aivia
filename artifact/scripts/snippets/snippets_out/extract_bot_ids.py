#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path

def sanitize_filename(name):
    """Create a valid filename from a string."""
    # Remove invalid chars and replace spaces with underscores
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '_', name).strip('_')
    return name[:100]  # Limit filename length

def extract_bot_ids(data, output_dir):
    """Extract bot IDs, names, and prompts."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a CSV file for easy viewing/importing
    csv_file = os.path.join(output_dir, "bot_ids_and_prompts.csv")
    
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write("Bot ID,Bot Name,Description\n")
        
        for bot in data.get('bot_list', []):
            bot_info = bot.get('bot_info', {})
            bot_id = bot_info.get('bot_id', 'Unknown ID')
            name = bot_info.get('name', 'Unnamed Bot')
            # Escape quotes in CSV
            safe_name = name.replace('"', '""')
            
            # Write to CSV - just ID and name
            f.write(f"{bot_id},\"{safe_name}\"\n")
    
    # Create a detailed Markdown file with full prompts
    md_file = os.path.join(output_dir, "bot_ids_and_prompts.md")
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# Bot IDs, Names, and Prompts\n\n")
        
        for bot in data.get('bot_list', []):
            bot_info = bot.get('bot_info', {})
            bot_id = bot_info.get('bot_id', 'Unknown ID')
            name = bot_info.get('name', 'Unnamed Bot')
            description = bot_info.get('description', 'No description')
            prompt_text = bot_info.get('prompt_info', 'No prompt')
            
            f.write(f"## {name}\n\n")
            f.write(f"**Bot ID:** `{bot_id}`\n\n")
            f.write(f"**Description:** {description}\n\n")
            f.write("### Prompt\n\n")
            f.write(f"```\n{prompt_text}\n```\n\n")
            f.write("---\n\n")
    
    # Create individual files for each bot prompt
    prompts_dir = os.path.join(output_dir, "individual_prompts")
    os.makedirs(prompts_dir, exist_ok=True)
    
    for bot in data.get('bot_list', []):
        bot_info = bot.get('bot_info', {})
        bot_id = bot_info.get('bot_id', 'Unknown ID')
        name = bot_info.get('name', 'Unnamed Bot')
        description = bot_info.get('description', 'No description')
        prompt_text = bot_info.get('prompt_info', '')
        
        if prompt_text:
            # Use name first, then bot ID in the filename (reversed order)
            filename = f"{sanitize_filename(name)}_{bot_id}.txt"
            file_path = os.path.join(prompts_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                # Include both name and ID at the top of the file
                f.write(f"NAME: {name}\n")
                f.write(f"BOT ID: {bot_id}\n")
                f.write(f"DESCRIPTION: {description}\n\n")
                f.write("PROMPT:\n")
                f.write("-" * 60 + "\n")
                f.write(f"{prompt_text}\n")
                f.write("-" * 60 + "\n")

def main():
    output_dir = "bot_ids_data"
    
    try:
        with open("bot_export.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        extract_bot_ids(data, output_dir)
        
        print(f"Extraction complete! Data saved to the '{output_dir}' directory.")
        print(f"- CSV summary: {output_dir}/bot_ids_and_prompts.csv")
        print(f"- Detailed markdown: {output_dir}/bot_ids_and_prompts.md")
        print(f"- Individual prompt files: {output_dir}/individual_prompts/")
    
    except FileNotFoundError:
        print("Error: bot_export.json file not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the bot_export.json file.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 