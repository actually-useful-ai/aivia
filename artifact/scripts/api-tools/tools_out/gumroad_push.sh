#!/bin/bash

# Your access token
ACCESS_TOKEN="vtw9Ud_ye8OmnEx8BcVgvO7C-U9zo2adLeX8Q1tar8g"

# Base API URL
BASE_API_URL="https://api.gumroad.com/v2"

# Folder containing your text files to be uploaded as products
FILES_DIR="./working/"

# Loop through each file in the directory
for file in "$FILES_DIR"/*
do
  # Extract the filename without the path
  filename=$(basename -- "$file")
  
  # Create a new product with file upload
  response=$(curl -X POST "$BASE_API_URL/products" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -F "name=$filename" \
    -F "price=100" \
    -F "currency=usd" \
    -F "published=true" \
    -F "file=@$file")

  echo "Created product for $filename: $response"
done