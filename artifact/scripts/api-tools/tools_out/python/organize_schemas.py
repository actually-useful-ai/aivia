#!/usr/bin/env python3
"""
Script to organize and validate OpenAPI schemas.
"""

import argparse
import logging
import shutil
from pathlib import Path

from schema_utils import SchemaValidator, deduplicate_schemas, normalize_schema

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_argparse() -> argparse.ArgumentParser:
    """Set up command line argument parsing."""
    parser = argparse.ArgumentParser(
        description='Organize and validate OpenAPI schemas'
    )
    parser.add_argument(
        '--input-dir',
        type=str,
        required=True,
        help='Directory containing input schemas'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        required=True,
        help='Directory to write organized schemas'
    )
    parser.add_argument(
        '--normalize',
        action='store_true',
        help='Normalize schema files'
    )
    parser.add_argument(
        '--deduplicate',
        action='store_true',
        help='Remove duplicate schemas'
    )
    return parser

def organize_schemas(input_dir: Path, output_dir: Path,
                    normalize: bool = False,
                    deduplicate: bool = False) -> None:
    """Organize schemas from input directory to output directory.
    
    Args:
        input_dir: Source directory containing schemas
        output_dir: Destination directory for organized schemas
        normalize: Whether to normalize schemas
        deduplicate: Whether to remove duplicates
    """
    logger.info(f"Organizing schemas from {input_dir} to {output_dir}")
    
    # Create validator
    validator = SchemaValidator(input_dir)
    
    # Create output directory structure
    output_dir.mkdir(parents=True, exist_ok=True)
    schemas_dir = output_dir / 'schemas'
    components_dir = output_dir / 'components'
    models_dir = components_dir / 'models'
    responses_dir = components_dir / 'responses'
    
    for directory in [schemas_dir, components_dir, models_dir, responses_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Process schemas
    if deduplicate:
        logger.info("Finding duplicate schemas...")
        duplicates = deduplicate_schemas(input_dir, schemas_dir)
        for dup in duplicates:
            logger.info(f"Found duplicate: {dup}")
    else:
        # Copy all schemas
        for schema_file in input_dir.glob('**/*.{yaml,yml,json}'):
            dest = schemas_dir / schema_file.name
            if normalize:
                logger.info(f"Normalizing {schema_file}")
                normalize_schema(schema_file, dest)
            else:
                shutil.copy2(schema_file, dest)
                
    # Validate organized schemas
    logger.info("Validating organized schemas...")
    validation_results = validator.validate_all()
    
    for schema_path, result in validation_results.items():
        if result is True:
            logger.info(f"✓ {schema_path} is valid")
        else:
            logger.error(f"✗ {schema_path} validation failed: {result}")

def main():
    parser = setup_argparse()
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    try:
        organize_schemas(
            input_dir=input_dir,
            output_dir=output_dir,
            normalize=args.normalize,
            deduplicate=args.deduplicate
        )
    except Exception as e:
        logger.error(f"Error organizing schemas: {e}")
        raise

if __name__ == '__main__':
    main() 