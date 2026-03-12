#!/usr/bin/env python3
"""
This script creates a table of product names and their IDs from filtered_products.json.

Usage:
    python product_id_table.py
"""

import json
from typing import List, Dict, Any

def create_product_table(input_file: str = "filtered_products.json") -> List[Dict[str, str]]:
    """
    Creates a table of product names and IDs from the filtered products JSON file.
    
    Parameters:
        input_file (str): Path to the filtered products JSON file
        
    Returns:
        List[Dict[str, str]]: List of products with their names and IDs
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not isinstance(data, dict) or "products" not in data:
            print("Error: Invalid JSON structure")
            return []
            
        # Extract just the name and ID for each product
        products = []
        for product in data["products"]:
            name = product.get("name", "Unknown")
            product_id = product.get("id", "No ID")
            if name and product_id:  # Only include products with both name and ID
                products.append({
                    "name": name,
                    "id": product_id
                })
                
        return products
        
    except Exception as e:
        print(f"Error reading/processing file: {str(e)}")
        return []

def print_table(products: List[Dict[str, str]]) -> None:
    """
    Prints a formatted table of product names and IDs.
    
    Parameters:
        products (List[Dict[str, str]]): List of products with their names and IDs
    """
    if not products:
        print("No products found.")
        return
        
    # Find the longest name and ID for proper spacing
    max_name_length = max(len(p["name"]) for p in products)
    max_id_length = max(len(p["id"]) for p in products)
    
    # Create the format string for consistent spacing
    format_str = f"{{:<{max_name_length}}} | {{}}"
    
    # Print header
    print("\nProduct Name and ID Table")
    print("-" * (max_name_length + max_id_length + 3))  # +3 for the separator " | "
    print(format_str.format("Product Name", "Product ID"))
    print("-" * (max_name_length + max_id_length + 3))
    
    # Print each product
    for product in sorted(products, key=lambda x: x["name"].lower()):
        print(format_str.format(product["name"], product["id"]))
    
    # Print summary
    print("-" * (max_name_length + max_id_length + 3))
    print(f"\nTotal Products: {len(products)}")

def main():
    # Create the product table
    products = create_product_table()
    
    # Print the formatted table
    print_table(products)
    
    # Optionally save to a text file
    output_file = "product_id_table.txt"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Redirect stdout to file
            import sys
            original_stdout = sys.stdout
            sys.stdout = f
            print_table(products)
            sys.stdout = original_stdout
        print(f"\nTable has been saved to {output_file}")
    except Exception as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    main() 