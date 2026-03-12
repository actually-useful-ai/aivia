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

def extract_prompts(data, output_dir):
    """Extract all prompts from the bot data."""
    prompts_dir = Path(output_dir) / "prompts"
    prompts_dir.mkdir(exist_ok=True, parents=True)
    
    # Create an index file
    index_file = prompts_dir / "index.md"
    
    with open(index_file, 'w') as idx:
        idx.write("# Extracted Prompts Index\n\n")
        idx.write("| Bot Name | Description | Prompt File |\n")
        idx.write("|----------|-------------|-------------|\n")
        
        for bot in data.get('bot_list', []):
            bot_info = bot.get('bot_info', {})
            name = bot_info.get('name', 'Unnamed Bot')
            description = bot_info.get('description', 'No description')
            prompt_text = bot_info.get('prompt_info', '')
            
            if prompt_text:
                filename = sanitize_filename(name) + '.md'
                prompt_file = prompts_dir / filename
                
                with open(prompt_file, 'w') as f:
                    f.write(f"# {name}\n\n")
                    f.write(f"**Description:** {description}\n\n")
                    f.write("## System Prompt\n\n")
                    f.write(f"{prompt_text}\n")
                
                idx.write(f"| {name} | {description} | [{filename}](./prompts/{filename}) |\n")

def extract_tools(data, output_dir):
    """Extract information about tools used in bots."""
    tools_dir = Path(output_dir) / "tools"
    tools_dir.mkdir(exist_ok=True, parents=True)
    
    # Create an index file
    index_file = tools_dir / "index.md"
    tools_dict = {}
    
    with open(index_file, 'w') as idx:
        idx.write("# Extracted Tools Index\n\n")
        idx.write("| Tool ID | Tool Name | Description |\n")
        idx.write("|---------|-----------|-------------|\n")
        
        for bot in data.get('bot_list', []):
            bot_option_data = bot.get('bot_option_data', {})
            plugin_details = bot_option_data.get('plugin_detail_map', {})
            
            for tool_id, tool_info in plugin_details.items():
                if tool_id not in tools_dict:
                    tools_dict[tool_id] = tool_info
                    idx.write(f"| {tool_id} | {tool_info.get('name', 'Unnamed Tool')} | {tool_info.get('description', 'No description')} |\n")
    
    # Save each tool as its own file
    for tool_id, tool_info in tools_dict.items():
        tool_name = tool_info.get('name', 'Unnamed Tool')
        filename = sanitize_filename(tool_name) + '.md'
        tool_file = tools_dir / filename
        
        with open(tool_file, 'w') as f:
            f.write(f"# {tool_name}\n\n")
            f.write(f"**Tool ID:** {tool_id}\n\n")
            f.write(f"**Description:**\n{tool_info.get('description', 'No description')}\n")

def extract_workflows(data, output_dir):
    """Extract all workflows from the bot data."""
    workflows_dir = Path(output_dir) / "workflows"
    workflows_dir.mkdir(exist_ok=True, parents=True)
    
    # Create an index file
    index_file = workflows_dir / "index.md"
    workflows_dict = {}
    
    with open(index_file, 'w') as idx:
        idx.write("# Extracted Workflows Index\n\n")
        idx.write("| Workflow ID | Workflow Name | Description |\n")
        idx.write("|-------------|---------------|-------------|\n")
        
        for bot in data.get('bot_list', []):
            bot_option_data = bot.get('bot_option_data', {})
            workflow_details = bot_option_data.get('workflow_detail_map', {})
            
            for workflow_id, workflow_info in workflow_details.items():
                if workflow_id not in workflows_dict:
                    workflows_dict[workflow_id] = workflow_info
                    idx.write(f"| {workflow_id} | {workflow_info.get('name', 'Unnamed Workflow')} | {workflow_info.get('description', 'No description')} |\n")
    
    # Save each workflow as its own file
    for workflow_id, workflow_info in workflows_dict.items():
        workflow_name = workflow_info.get('name', 'Unnamed Workflow')
        filename = sanitize_filename(workflow_name) + '.md'
        workflow_file = workflows_dir / filename
        
        with open(workflow_file, 'w') as f:
            f.write(f"# {workflow_name}\n\n")
            f.write(f"**Workflow ID:** {workflow_id}\n\n")
            f.write(f"**Description:**\n{workflow_info.get('description', 'No description')}\n")

def extract_models(data, output_dir):
    """Extract information about models used in bots."""
    models_dir = Path(output_dir) / "models"
    models_dir.mkdir(exist_ok=True, parents=True)
    
    # Create an index file
    index_file = models_dir / "index.md"
    models_dict = {}
    
    with open(index_file, 'w') as idx:
        idx.write("# Extracted Models Index\n\n")
        idx.write("| Model ID | Model Name | Model Family |\n")
        idx.write("|----------|------------|-------------|\n")
        
        for bot in data.get('bot_list', []):
            bot_option_data = bot.get('bot_option_data', {})
            model_details = bot_option_data.get('model_detail_map', {})
            
            for model_id, model_info in model_details.items():
                if model_id not in models_dict:
                    models_dict[model_id] = model_info
                    idx.write(f"| {model_id} | {model_info.get('name', 'Unnamed Model')} | {model_info.get('model_family', 'Unknown')} |\n")

def extract_onboarding(data, output_dir):
    """Extract onboarding information from bots."""
    onboarding_dir = Path(output_dir) / "onboarding"
    onboarding_dir.mkdir(exist_ok=True, parents=True)
    
    # Create an index file
    index_file = onboarding_dir / "index.md"
    
    with open(index_file, 'w') as idx:
        idx.write("# Extracted Onboarding Information\n\n")
        idx.write("| Bot Name | Prologue |\n")
        idx.write("|----------|----------|\n")
        
        for bot in data.get('bot_list', []):
            bot_info = bot.get('bot_info', {})
            name = bot_info.get('name', 'Unnamed Bot')
            onboarding_info = bot_info.get('onboarding_info', {})
            prologue = onboarding_info.get('prologue', '')
            
            if prologue:
                filename = sanitize_filename(name) + '_onboarding.md'
                onboarding_file = onboarding_dir / filename
                
                with open(onboarding_file, 'w') as f:
                    f.write(f"# {name} - Onboarding Information\n\n")
                    f.write("## Prologue\n\n")
                    f.write(f"{prologue}\n\n")
                    
                    if 'suggested_questions' in onboarding_info:
                        f.write("## Suggested Questions\n\n")
                        for question in onboarding_info['suggested_questions']:
                            f.write(f"- {question}\n")
                
                idx.write(f"| {name} | {prologue[:50]}... | [{filename}](./onboarding/{filename}) |\n")

def main():
    output_dir = "extracted_data"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        with open("bot_export.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Extract various components
        extract_prompts(data, output_dir)
        extract_tools(data, output_dir)
        extract_workflows(data, output_dir)
        extract_models(data, output_dir)
        extract_onboarding(data, output_dir)
        
        # Create a main index
        with open(os.path.join(output_dir, "index.md"), 'w') as f:
            f.write("# Extracted Coze Data\n\n")
            f.write("This directory contains extracted information from a Coze export file.\n\n")
            f.write("## Contents\n\n")
            f.write("- [Prompts](./prompts/index.md)\n")
            f.write("- [Tools](./tools/index.md)\n")
            f.write("- [Workflows](./workflows/index.md)\n")
            f.write("- [Models](./models/index.md)\n")
            f.write("- [Onboarding Information](./onboarding/index.md)\n")
        
        print("Extraction complete! Data saved to the 'extracted_data' directory.")
    
    except FileNotFoundError:
        print("Error: bot_export.json file not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the bot_export.json file.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 