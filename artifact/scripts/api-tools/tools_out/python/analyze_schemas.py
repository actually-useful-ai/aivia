#!/usr/bin/env python3
"""
Script to analyze and categorize OpenAPI schemas.
"""

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml
from schema_utils import SchemaValidator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SchemaAnalyzer:
    """Analyzer for OpenAPI schemas."""
    
    # Schema categories and their keywords
    CATEGORIES = {
        'api_integration': {
            'keywords': ['api', 'endpoint', 'service', 'integration'],
            'paths': True  # Has API paths
        },
        'data_model': {
            'keywords': ['model', 'schema', 'type', 'object'],
            'components': True  # Has reusable components
        },
        'utility': {
            'keywords': ['util', 'helper', 'common', 'shared'],
            'generic': True  # Generic/utility schemas
        }
    }
    
    def __init__(self, schema_dir: Path):
        """Initialize the analyzer.
        
        Args:
            schema_dir: Directory containing schemas to analyze
        """
        self.schema_dir = Path(schema_dir)
        self.validator = SchemaValidator(schema_dir)
        
    def analyze_schema(self, schema_path: Path) -> Tuple[str, Dict]:
        """Analyze a single schema file.
        
        Args:
            schema_path: Path to schema file
            
        Returns:
            Tuple of (category, analysis_results)
        """
        with open(schema_path) as f:
            if schema_path.suffix in ['.yaml', '.yml']:
                schema = yaml.safe_load(f)
            else:
                schema = json.load(f)
                
        # Analyze schema structure
        has_paths = 'paths' in schema
        has_components = 'components' in schema
        
        # Extract keywords from schema content
        content_str = json.dumps(schema).lower()
        
        # Determine category
        scores = defaultdict(int)
        for category, criteria in self.CATEGORIES.items():
            # Check structural criteria
            if criteria.get('paths') and has_paths:
                scores[category] += 2
            if criteria.get('components') and has_components:
                scores[category] += 2
                
            # Check keywords
            for keyword in criteria['keywords']:
                if keyword in content_str:
                    scores[category] += 1
                    
        # Get category with highest score
        category = max(scores.items(), key=lambda x: x[1])[0] if scores else 'unknown'
        
        # Collect analysis results
        results = {
            'category': category,
            'has_paths': has_paths,
            'has_components': has_components,
            'component_types': list(schema.get('components', {}).keys()),
            'endpoint_count': len(schema.get('paths', {})),
            'size_bytes': schema_path.stat().st_size
        }
        
        return category, results
        
    def analyze_all(self) -> Dict[str, List[Dict]]:
        """Analyze all schemas in the directory.
        
        Returns:
            Dict mapping categories to lists of schema analysis results
        """
        results = defaultdict(list)
        
        for schema_file in self.schema_dir.glob('**/*.{yaml,yml,json}'):
            try:
                category, analysis = self.analyze_schema(schema_file)
                results[category].append({
                    'file': str(schema_file),
                    **analysis
                })
            except Exception as e:
                logger.error(f"Error analyzing {schema_file}: {e}")
                
        return dict(results)
        
    def suggest_organization(self) -> Dict[str, Set[Path]]:
        """Suggest how to organize schemas based on analysis.
        
        Returns:
            Dict mapping target directories to sets of schema files
        """
        organization = defaultdict(set)
        
        # Analyze all schemas
        analysis_results = self.analyze_all()
        
        for category, schemas in analysis_results.items():
            for schema in schemas:
                schema_path = Path(schema['file'])
                
                if category == 'api_integration':
                    organization['schemas'].add(schema_path)
                elif category == 'data_model':
                    if schema['has_components']:
                        organization['components/models'].add(schema_path)
                    else:
                        organization['schemas'].add(schema_path)
                elif category == 'utility':
                    if 'responses' in schema['component_types']:
                        organization['components/responses'].add(schema_path)
                    else:
                        organization['components'].add(schema_path)
                else:
                    organization['schemas'].add(schema_path)
                    
        return dict(organization)
        
    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """Generate a markdown report of the analysis.
        
        Args:
            output_path: Optional path to write report
            
        Returns:
            Report content as string
        """
        analysis = self.analyze_all()
        
        # Build report
        lines = ['# Schema Analysis Report\n']
        
        # Summary
        total_schemas = sum(len(schemas) for schemas in analysis.values())
        lines.append(f"## Summary\n")
        lines.append(f"Total schemas analyzed: {total_schemas}\n")
        
        # Categories
        lines.append(f"## Categories\n")
        for category, schemas in analysis.items():
            lines.append(f"### {category.replace('_', ' ').title()}\n")
            lines.append(f"Total: {len(schemas)}\n")
            lines.append("| File | Endpoints | Component Types | Size |\n")
            lines.append("|------|-----------|-----------------|------|\n")
            
            for schema in schemas:
                components = ', '.join(schema['component_types']) or 'None'
                size_kb = schema['size_bytes'] / 1024
                lines.append(
                    f"| {schema['file']} | "
                    f"{schema['endpoint_count']} | "
                    f"{components} | "
                    f"{size_kb:.1f}KB |"
                )
            lines.append("\n")
            
        report = '\n'.join(lines)
        
        if output_path:
            output_path.write_text(report)
            
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze OpenAPI schemas')
    parser.add_argument('schema_dir', type=Path, help='Directory containing schemas')
    parser.add_argument('--report', type=Path, help='Path to write analysis report')
    
    args = parser.parse_args()
    
    try:
        analyzer = SchemaAnalyzer(args.schema_dir)
        report = analyzer.generate_report(args.report)
        print(report)
        
        # Print organization suggestions
        print("\nSuggested Organization:")
        for target_dir, schemas in analyzer.suggest_organization().items():
            print(f"\n{target_dir}:")
            for schema in schemas:
                print(f"  {schema}")
                
    except Exception as e:
        logger.error(f"Error analyzing schemas: {e}")
        raise

if __name__ == '__main__':
    main() 