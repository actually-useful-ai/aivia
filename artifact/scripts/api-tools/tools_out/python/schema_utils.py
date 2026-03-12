"""
Schema validation and utility functions for OpenAPI schemas.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from jsonschema import validate

class SchemaValidator:
    """Validator for OpenAPI schemas."""
    
    def __init__(self, schema_dir: Union[str, Path]):
        """Initialize the validator with a schema directory.
        
        Args:
            schema_dir: Path to the directory containing OpenAPI schemas
        """
        self.schema_dir = Path(schema_dir)
        if not self.schema_dir.exists():
            raise ValueError(f"Schema directory {schema_dir} does not exist")
    
    def validate_schema(self, schema_path: Union[str, Path]) -> bool:
        """Validate a single OpenAPI schema file.
        
        Args:
            schema_path: Path to the schema file
            
        Returns:
            bool: True if valid, raises exception if invalid
        """
        schema_path = Path(schema_path)
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file {schema_path} not found")
            
        with open(schema_path) as f:
            if schema_path.suffix in ['.yaml', '.yml']:
                spec = yaml.safe_load(f)
            else:
                spec = json.load(f)
                
        # Basic validation that it's a valid JSON Schema
        validate(instance={}, schema=spec)
        return True
        
    def validate_all(self) -> Dict[str, bool]:
        """Validate all schema files in the schema directory.
        
        Returns:
            Dict mapping schema paths to validation results
        """
        results = {}
        for schema_file in self.schema_dir.glob('**/*.{yaml,yml,json}'):
            try:
                results[str(schema_file)] = self.validate_schema(schema_file)
            except Exception as e:
                results[str(schema_file)] = str(e)
        return results

def deduplicate_schemas(schema_dir: Union[str, Path], 
                       output_dir: Optional[Union[str, Path]] = None) -> List[Path]:
    """Find and remove duplicate schema files based on content.
    
    Args:
        schema_dir: Directory containing schema files
        output_dir: Optional directory to write unique schemas to
        
    Returns:
        List of paths to duplicate files that were found
    """
    schema_dir = Path(schema_dir)
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
    # Map content hashes to file paths
    content_map = {}
    duplicates = []
    
    for schema_file in schema_dir.glob('**/*.{yaml,yml,json}'):
        with open(schema_file) as f:
            content = f.read()
            content_hash = hash(content)
            
            if content_hash in content_map:
                duplicates.append(schema_file)
            else:
                content_map[content_hash] = schema_file
                if output_dir:
                    dest = output_dir / schema_file.name
                    if not dest.exists():
                        dest.write_text(content)
                        
    return duplicates

def normalize_schema(schema_path: Union[str, Path], 
                    output_path: Optional[Union[str, Path]] = None) -> dict:
    """Normalize a schema file by sorting keys and standardizing format.
    
    Args:
        schema_path: Path to input schema file
        output_path: Optional path to write normalized schema
        
    Returns:
        Normalized schema as dict
    """
    schema_path = Path(schema_path)
    
    with open(schema_path) as f:
        if schema_path.suffix in ['.yaml', '.yml']:
            schema = yaml.safe_load(f)
        else:
            schema = json.load(f)
            
    # Sort keys recursively
    def sort_dict(d: dict) -> dict:
        return {k: sort_dict(v) if isinstance(v, dict) else v 
               for k, v in sorted(d.items())}
               
    normalized = sort_dict(schema)
    
    if output_path:
        output_path = Path(output_path)
        with open(output_path, 'w') as f:
            if output_path.suffix in ['.yaml', '.yml']:
                yaml.dump(normalized, f, sort_keys=True)
            else:
                json.dump(normalized, f, sort_keys=True, indent=2)
                
    return normalized 