#!/bin/bash

# =============================================================================
# Gumroad API v2 Shell Script
# =============================================================================

# ----------------------------
# Configuration and Credentials
# ----------------------------

# Credentials (Ensure these are kept secure)
APP_ID="HvH02LdnydJ-Jo2UJUDVPCUg2arAfm1zoz3HphqTrVRU"
APP_SECRET="HDfs_P6T-7K9dmMWJoq35Tj55M8w8TY2bL-tavCfzsQ"
ACCESS_TOKEN="vtw9Ud_ye8OmnEx8BcVgvO7C-U9zo2adLeX8Q1tar8g"
REDIRECT_URI="https://ai.assisted.space/oauth/callback"

# Base API URL
BASE_API_URL="https://api.gumroad.com/v2"
LOG_FILE="gumroad_api_log.txt"  # Log file for outputs

# ---------------------------------
# Utility Functions and Error Handling
# ---------------------------------

# Function: make_request
# Updated to output pure JSON and wrap errors in a JSON object
make_request() {
  local endpoint="$1"
  local method="$2"
  local data="$3"
  local url="$BASE_API_URL/$endpoint"
  local response
  if [[ "$method" == "GET" ]]; then
    response=$(curl -s -X "$method" "$url" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      --max-time 120)
  else
    response=$(curl -s -X "$method" "$url" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$data" --max-time 120)
  fi

  local success=$(echo "$response" | jq -r '.success // empty')
  if [[ "$success" != "true" ]]; then
    echo "{\"error\": true, \"message\": \"API request failed\", \"response\": $response}" | tee -a "$LOG_FILE"
    return 1
  fi

  echo "$response" | tee -a "$LOG_FILE"
}

# Function: list_products
list_products() {
  response=$(make_request "products" "GET")
  [ $? -eq 0 ] && echo "$response" | jq '{products: .products}' || return 1
}

# Function: get_product_details
get_product_details() {
  echo -n "Enter Product ID: "
  read product_id
  response=$(make_request "products/$product_id" "GET")
  [ $? -eq 0 ] && echo "$response" | jq . || return 1
}

# Function: create_product
create_product() {
  echo -n "Product Name: "
  read name
  echo -n "Description: "
  read description
  echo -n "Price (in cents): "
  read price
  echo -n "Currency (e.g., usd): "
  read currency

  read -r -d '' data << EOF
{
  "name": "$name",
  "description": "$description",
  "price": $price,
  "currency": "$currency",
  "require_shipping": false
}
EOF

  response=$(make_request "products" "POST" "$data")
  [ $? -eq 0 ] && echo "$response" | jq . || return 1
}

# Function: update_product
update_product() {
  echo -n "Enter Product ID to Update: "
  read product_id
  echo -n "New Product Name (leave blank to skip): "
  read name
  echo -n "New Description (leave blank to skip): "
  read description
  echo -n "New Price (in cents, leave blank to skip): "
  read price
  echo -n "New Currency (e.g., usd, leave blank to skip): "
  read currency
  echo -n "Publish? (yes/no, leave blank to skip): "
  read publish

  data="{"
  [[ -n "$name" ]] && data+="\"name\": \"$name\"," 
  [[ -n "$description" ]] && data+="\"description\": \"$description\"," 
  [[ -n "$price" ]] && data+="\"price\": $price,"
  [[ -n "$currency" ]] && data+="\"currency\": \"$currency\"," 
  if [[ "$publish" == "yes" ]]; then
    data+="\"published\": true,"
  elif [[ "$publish" == "no" ]]; then
    data+="\"published\": false,"
  fi
  data=${data%,}
  data+="}"
  
  response=$(make_request "products/$product_id" "PUT" "$data")
  [ $? -eq 0 ] && echo "$response" | jq . || return 1
}

# Function: delete_product
delete_product() {
  echo -n "Enter Product ID to Delete: "
  read product_id
  echo -n "Are you sure you want to delete this product? (yes/no): "
  read confirm
  if [[ "$confirm" != "yes" ]]; then
    echo "{\"error\": true, \"message\": \"Deletion aborted\"}"
    return
  fi

  response=$(make_request "products/$product_id" "DELETE")
  [ $? -eq 0 ] && echo "$response" | jq . || return 1
}

# Function: list_sales
list_sales() {
  local page_key=""
  while true; do
    if [ -z "$page_key" ]; then
      response=$(make_request "sales" "GET")
    else
      response=$(make_request "sales?page_key=$page_key" "GET")
    fi

    if [ $? -ne 0 ]; then
      return 1
    fi

    # Display current page of sales as JSON
    echo "$response" | jq '.sales'

    page_key=$(echo "$response" | jq -r '.next_page_key')
    if [ "$page_key" == "null" ] || [ -z "$page_key" ]; then
      break
    fi
  done
}

# Function: verify_license
verify_license() {
  echo -n "Product ID: "
  read product_id
  echo -n "License Key: "
  read license_key

  read -r -d '' data << EOF
{
  "product_id": "$product_id",
  "license_key": "$license_key",
  "increment_uses_count": true
}
EOF

  response=$(make_request "licenses/verify" "POST" "$data")
  [ $? -eq 0 ] && echo "$response" | jq . || return 1
}

# Function: enable_license
enable_license() {
  echo -n "Product ID: "
  read product_id
  echo -n "License Key: "
  read license_key

  read -r -d '' data << EOF
{
  "access_token": "$ACCESS_TOKEN",
  "product_id": "$product_id",
  "license_key": "$license_key"
}
EOF

  response=$(make_request "licenses/enable" "PUT" "$data")
  [ $? -eq 0 ] && echo "$response" | jq . || return 1
}

# Function: manage_resource_subscriptions
manage_resource_subscriptions() {
  echo "1) Create/Update Subscription"
  echo "2) List All Subscriptions"
  echo -n "Choose an option: "
  read sub_choice

  if [ "$sub_choice" == "1" ]; then
    echo -n "Resource Name (e.g., sale): "
    read resource_name
    echo -n "Post URL (e.g., https://yourdomain.com/webhook): "
    read post_url

    read -r -d '' data << EOF
{
  "resource_name": "$resource_name",
  "post_url": "$post_url"
}
EOF

    response=$(make_request "resource_subscriptions" "PUT" "$data")
    [ $? -eq 0 ] && echo "$response" | jq . || return 1
  elif [ "$sub_choice" == "2" ]; then
    response=$(make_request "resource_subscriptions" "GET")
    [ $? -eq 0 ] && echo "$response" | jq . || return 1
  else
    echo "{\"error\": true, \"message\": \"Invalid option\"}"
  fi
}

# Main Interactive Loop
while true; do
  echo "Gumroad API Interactive Shell"
  echo "1) List Products"
  echo "2) Get Product Details"
  echo "3) Create Product"
  echo "4) Update Product"
  echo "5) Delete Product"
  echo "6) List Sales"
  echo "7) Verify License"
  echo "8) Enable License"
  echo "9) Manage Resource Subscriptions"
  echo "10) Exit"
  echo -n "Choose an option: "
  read choice

  case $choice in
    1)
      list_products
      ;;
    2)
      get_product_details
      ;;
    3)
      create_product
      ;;
    4)
      update_product
      ;;
    5)
      delete_product
      ;;
    6)
      list_sales
      ;;
    7)
      verify_license
      ;;
    8)
      enable_license
      ;;
    9)
      manage_resource_subscriptions
      ;;
    10)
      echo "{\"message\": \"Exiting...\"}"
      exit 0
      ;;
    *)
      echo "{\"error\": true, \"message\": \"Invalid option, please try again.\"}"
      ;;
  esac

  echo -e "\nPress Enter to continue..."
  read
done