"""
Tools for generating LLM-friendly prompts from OpenAPI schemas.
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import yaml

from ..validators import load_schema

def generate_endpoint_prompt(path: str, method: str, spec: Dict[str, Any]) -> str:
    """Generate a natural language description of an API endpoint."""
    lines = []
    
    # Add summary and description
    if "summary" in spec:
        lines.append(spec["summary"])
    if "description" in spec:
        lines.append(spec["description"])
    else:
        lines.append("No detailed description provided")
    
    # Add parameters section
    if "parameters" in spec:
        param_sections = {
            "header": [],
            "path": [],
            "query": [],
            "cookie": []
        }
        
        for param in spec["parameters"]:
            required = "(required)" if param.get("required", False) else "(optional)"
            desc = param.get("description", "No description available")
            param_line = f"- {param['name']} {required}: {desc}"
            param_sections[param["in"]].append(param_line)
        
        # Add non-empty parameter sections
        for section_name, params in param_sections.items():
            if params:
                lines.append(f"\n{section_name.title()} Parameters:")
                lines.extend(params)
    
    # Add request body section
    if "requestBody" in spec:
        lines.append("\nRequest Body:")
        body = spec["requestBody"]
        if "content" in body and "application/json" in body["content"]:
            schema = body["content"]["application/json"]["schema"]
            if "properties" in schema:
                for prop_name, prop in schema["properties"].items():
                    required = "(required)" if "required" in schema and prop_name in schema["required"] else "(optional)"
                    desc = prop.get("description", "No description available")
                    lines.append(f"- {prop_name} {required}: {desc} (type: {prop['type']})")
    
    # Add responses section
    if "responses" in spec:
        lines.append("\nResponses:")
        for status, response in spec["responses"].items():
            desc = response.get("description", "No description available")
            lines.append(f"- {status}: {desc}")
    
    return "\n".join(lines)

def generate_schema_prompt(schema: Dict[str, Any]) -> str:
    """Generate a natural language description of an OpenAPI schema."""
    lines = []
    
    # Add title and version
    info = schema.get("info", {})
    title = info.get("title", "Untitled API")
    version = info.get("version", "Unknown")
    description = info.get("description", "No description available")
    
    lines.append(f"# {title}")
    lines.append(f"Version: {version}")
    if description:
        lines.append(description)
    
    # Add base URL if available
    if "servers" in schema and schema["servers"]:
        lines.append(f"\nBase URL: {schema['servers'][0]['url']}")
    
    # Add endpoints overview
    if "paths" in schema:
        lines.append("\nAvailable Endpoints:")
        for path, methods in schema["paths"].items():
            for method, spec in methods.items():
                summary = spec.get("summary", "No summary available")
                lines.append(f"- {method.upper()} {path}: {summary}")
    
    return "\n".join(lines)

def generate_prompts(schema_path: Path) -> Dict[str, Any]:
    """Generate all prompts for an OpenAPI schema."""
    try:
        with open(schema_path) as f:
            schema = json.load(f)
        
        if not isinstance(schema, dict) or "openapi" not in schema:
            raise ValueError("Invalid OpenAPI schema")
        
        prompts = {
            "overview": generate_schema_prompt(schema),
            "endpoints": {}
        }
        
        if "paths" in schema:
            for path, methods in schema["paths"].items():
                for method, spec in methods.items():
                    endpoint_key = f"{method.upper()} {path}"
                    prompts["endpoints"][endpoint_key] = generate_endpoint_prompt(path, method, spec)
        
        return prompts
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Error parsing schema: {str(e)}") 