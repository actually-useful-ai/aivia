#!/usr/bin/env python3
"""
This script processes Gumroad products data, extracting key information for analysis.

Usage:
    python gumroad_product_harvester.py <input_file>
"""

import json
import sys
import os
from typing import List, Dict, Any

def filter_product_data(products_data):
    """
    Filters a list of product dictionaries to include only selected keys.
    """
    allowed_keys = [
        "name",
        "description",
        "price",
        "currency",
        "short_url",
        "id",
        "formatted_price",
        "published",
        "custom_permalink",
        "subscription_duration",
        "sales_count",
        "sales_usd_cents",
        "custom_summary"
    ]
    
    filtered_data = []
    for product in products_data:
        filtered_product = {key: product.get(key) for key in allowed_keys}
        filtered_data.append(filtered_product)
    return filtered_data

def harvest_products(file_path: str) -> List[Dict[str, Any]]:
    """
    Harvest selected product fields from the given JSON file.
    
    Parameters:
        file_path (str): Path to the JSON file.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with the extracted fields.
    """
    try:
        print(f"Opening file: {file_path}")
        print(f"Current working directory: {os.getcwd()}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        # Handle both possible data structures
        if isinstance(data, list):
            products = data
        elif isinstance(data, dict) and "products" in data:
            products = data["products"]
        else:
            print("Error: Unexpected JSON structure")
            return []

        filtered_products = []
        for product in products:
            # Extract only the fields we want
            filtered_product = {
                "name": product.get("name"),
                "description": product.get("description"),
                "price": product.get("price"),
                "currency": product.get("currency"),
                "short_url": product.get("short_url"),
                "id": product.get("id"),
                "formatted_price": product.get("formatted_price"),
                "published": product.get("published"),
                "custom_permalink": product.get("custom_permalink"),
                "subscription_duration": product.get("subscription_duration"),
                "sales_count": product.get("sales_count"),
                "sales_usd_cents": product.get("sales_usd_cents"),
                "custom_summary": product.get("custom_summary")
            }
            filtered_products.append(filtered_product)
            
        return filtered_products
            
    except Exception as e:
        print(f"Error reading/processing file: {str(e)}")
        return []

def main():
    # Get the input file path from command line arguments
    if len(sys.argv) != 2:
        print("Usage: python gumroad_product_harvester.py <products_json_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist")
        sys.exit(1)
        
    # Process the products
    products = harvest_products(file_path)
    if not products:
        print("No products found or error processing the file.")
        sys.exit(1)
        
    print(f"Successfully processed {len(products)} products")
    
    # Write the filtered products to a new JSON file
    output_file = "filtered_products.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"products": products}, f, indent=4, ensure_ascii=False)
        print(f"Filtered data written to '{output_file}'")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 