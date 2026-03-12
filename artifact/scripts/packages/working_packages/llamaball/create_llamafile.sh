#!/bin/bash
# Create Llamafile from Ollama Model Script
# File Purpose: Convert Ollama models to standalone llamafile executables
# Primary Functions: find_model, create_args, build_llamafile
# Inputs: Ollama model name
# Outputs: Standalone .llamafile executable

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🦙 Ollama to Llamafile Converter${NC}"
echo ""

# Check if llamafile binary exists
if ! command -v llamafile &> /dev/null; then
    echo -e "${YELLOW}⚠️  llamafile not found. Installing...${NC}"
    echo "Download from: https://github.com/Mozilla-Ocho/llamafile/releases"
    echo ""
    echo "Quick install:"
    echo "curl -L -o /usr/local/bin/llamafile https://github.com/Mozilla-Ocho/llamafile/releases/latest/download/llamafile"
    echo "chmod +x /usr/local/bin/llamafile"
    exit 1
fi

# Function to find Ollama model
find_ollama_model() {
    local model_name=$1
    local manifest_dir="$HOME/.ollama/models/manifests/registry.ollama.ai/library"
    
    echo -e "${CYAN}Looking for model: $model_name${NC}"
    
    # Parse model name (handle namespace/model:tag format)
    local namespace=""
    local model=""
    local tag="latest"
    
    if [[ "$model_name" == *"/"* ]]; then
        namespace=$(echo "$model_name" | cut -d'/' -f1)
        model_name=$(echo "$model_name" | cut -d'/' -f2)
    fi
    
    if [[ "$model_name" == *":"* ]]; then
        model=$(echo "$model_name" | cut -d':' -f1)
        tag=$(echo "$model_name" | cut -d':' -f2)
    else
        model="$model_name"
    fi
    
    # Find manifest file
    local manifest_file=""
    if [ -n "$namespace" ]; then
        manifest_file="$manifest_dir/$namespace/$model/$tag"
    else
        manifest_file="$manifest_dir/$model/$tag"
    fi
    
    if [ ! -f "$manifest_file" ]; then
        echo -e "${RED}✗ Model manifest not found: $manifest_file${NC}"
        return 1
    fi
    
    # Extract GGUF file digest from manifest
    local gguf_digest=$(grep -A2 'application/vnd.ollama.image.model' "$manifest_file" | grep digest | cut -d'"' -f4)
    
    if [ -z "$gguf_digest" ]; then
        echo -e "${RED}✗ Could not find GGUF digest in manifest${NC}"
        return 1
    fi
    
    local gguf_file="$HOME/.ollama/models/blobs/$gguf_digest"
    
    if [ ! -f "$gguf_file" ]; then
        echo -e "${RED}✗ GGUF file not found: $gguf_file${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ Found GGUF: $gguf_file${NC}"
    echo "$gguf_file"
}

# Main conversion function
convert_to_llamafile() {
    local model_name=$1
    local output_name=${2:-"${model_name//[:\/]/-}.llamafile"}
    
    echo -e "${CYAN}Converting $model_name to $output_name${NC}"
    
    # Find the GGUF file
    local gguf_path=$(find_ollama_model "$model_name")
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # Create .args file for default arguments
    cat > .args << EOF
-m
model.gguf
--host
0.0.0.0
-ngl
9999
...
EOF
    
    echo -e "${CYAN}Creating llamafile...${NC}"
    
    # Copy llamafile binary
    cp /usr/local/bin/llamafile "$output_name"
    
    # Add GGUF weights and args to the executable
    # Using zipalign if available, otherwise fallback to zip
    if command -v zipalign &> /dev/null; then
        # Rename the GGUF file when adding to archive
        zipalign -j0 "$output_name" "$gguf_path>model.gguf" .args
    else
        # Alternative using zip
        echo -e "${YELLOW}Using zip (zipalign not found)${NC}"
        cp "$gguf_path" model.gguf
        zip -j0 "$output_name" model.gguf .args
        rm model.gguf
    fi
    
    # Clean up
    rm -f .args
    
    # Make executable
    chmod +x "$output_name"
    
    echo -e "${GREEN}✅ Successfully created: $output_name${NC}"
    echo -e "${CYAN}Size: $(du -h "$output_name" | cut -f1)${NC}"
    echo ""
    echo -e "${YELLOW}To run:${NC}"
    echo "./$output_name"
    echo ""
    echo -e "${YELLOW}To run with custom arguments:${NC}"
    echo "./$output_name --temp 0.7 -p 'Your prompt here'"
}

# Show usage
if [ $# -eq 0 ]; then
    echo "Usage: $0 <ollama-model-name> [output-filename]"
    echo ""
    echo "Examples:"
    echo "  $0 coolhand/llamaball:1b"
    echo "  $0 coolhand/llamaball:4b my-llamaball.llamafile"
    echo ""
    echo "Available Ollama models:"
    ollama list | tail -n +2 | awk '{print "  • " $1}'
    exit 0
fi

# Run conversion
convert_to_llamafile "$1" "$2" 