#!/usr/bin/env python3
"""
This script filters a JSON file containing Gumroad sales data to extract only selected keys for data analysis.

Selected keys:
    - email
    - daystamp
    - product_name
    - price
    - product_id
    - is_following
    - is_recurring_billing
    - product_permalink
    - full_name
    - country
    - country_iso2  # Note: Assuming the intended key is 'country_iso2'
    - product_rating
    - reviews_count
    - average_rating
    - quantity

Usage:
    python filter_sales.py [input_file] [output_file]

If no file names are provided, defaults are used:
    input_file: "list_sales.json"
    output_file: "filtered_sales.json"
"""

import json
import sys
import os


def filter_sales_data(sales_data):
    """
    Filters a list of sales dictionaries to only include the selected keys.

    Parameters:
        sales_data (list): List of sales dictionaries.

    Returns:
        list: Filtered list of sales dictionaries containing only the allowed keys.
    """
    allowed_keys = [
        "email",
        "daystamp",
        "product_name",
        "price",
        "product_id",
        "is_following",
        "is_recurring_billing",
        "product_permalink",
        "full_name",
        "country",
        "country_iso2",
        "product_rating",
        "reviews_count",
        "average_rating",
        "quantity"
    ]
    
    filtered_data = []
    for sale in sales_data:
        # Create a new dictionary with only the allowed keys. Missing keys will result in a value of None.
        filtered_sale = {key: sale.get(key) for key in allowed_keys}
        filtered_data.append(filtered_sale)
    return filtered_data


def main():
    # Determine input and output file paths
    input_file = "list_sales.json"
    output_file = "filtered_sales.json"
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    # Verify the input file exists
    if not os.path.isfile(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    # Load JSON data from the input file
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from file '{input_file}': {e}")
        sys.exit(1)

    # Ensure the expected structure exists (a top-level 'sales' key with a list value)
    if "sales" not in data or not isinstance(data["sales"], list):
        print("Error: JSON format is not as expected. Expected a top-level 'sales' key with a list of sales.")
        sys.exit(1)

    # Filter the sales data
    filtered_sales = filter_sales_data(data["sales"])

    # Write the filtered data to the output file
    try:
        with open(output_file, 'w') as f:
            json.dump({"sales": filtered_sales}, f, indent=4)
        print(f"Filtered data successfully written to '{output_file}'.")
    except Exception as e:
        print(f"Error: Could not write to file '{output_file}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 