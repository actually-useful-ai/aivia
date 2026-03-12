#!/bin/bash
# ==============================================================================
# Build and Push Llamaball Models Script
# File Purpose: Automate building and pushing all Llamaball models to Ollama Hub
# Primary Functions: build_model, push_model, cleanup, main
# Inputs: Modelfiles from the Modelfiles directory
# Outputs: Built and pushed models to coolhand/llamaball namespace
# ==============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="coolhand"  # Only use coolhand namespace
MODEL_BASE="llamaball"
MODELFILES_DIR="Modelfiles"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Function to check if Ollama is running
check_ollama() {
    print_status "Checking if Ollama is running..."
    if ! ollama list >/dev/null 2>&1; then
        print_error "Ollama is not running or not accessible"
        print_status "Please start Ollama with: ollama serve"
        exit 1
    fi
    print_success "Ollama is running"
}

# Function to build a model
build_model() {
    local modelfile=$1
    local tag=$2

    print_status "Building model: ${MODEL_BASE}:${tag}"

    if ollama create -f "${MODELFILES_DIR}/${modelfile}" "${MODEL_BASE}:${tag}"; then
        print_success "Built ${MODEL_BASE}:${tag}"
        return 0
    else
        print_error "Failed to build ${MODEL_BASE}:${tag}"
        return 1
    fi
}

# Function to copy model to namespace
copy_model() {
    local source_tag=$1
    local target_tag=$2

    print_status "Copying ${MODEL_BASE}:${source_tag} to ${NAMESPACE}/${MODEL_BASE}:${target_tag}"

    if ollama cp "${MODEL_BASE}:${source_tag}" "${NAMESPACE}/${MODEL_BASE}:${target_tag}"; then
        print_success "Copied to ${NAMESPACE}/${MODEL_BASE}:${target_tag}"
        return 0
    else
        print_error "Failed to copy ${MODEL_BASE}:${source_tag}"
        return 1
    fi
}

# Function to push model
push_model() {
    local tag=$1

    print_status "Pushing ${NAMESPACE}/${MODEL_BASE}:${tag} to Ollama Hub..."

    if ollama push "${NAMESPACE}/${MODEL_BASE}:${tag}"; then
        print_success "Pushed ${NAMESPACE}/${MODEL_BASE}:${tag}"
        return 0
    else
        print_error "Failed to push ${NAMESPACE}/${MODEL_BASE}:${tag}"
        print_warning "You may need to authenticate with Ollama Hub first"
        return 1
    fi
}

# Function to clean up local models (optional)
cleanup_local() {
    local tag=$1
    print_status "Cleaning up local model: ${MODEL_BASE}:${tag}"
    ollama rm "${MODEL_BASE}:${tag}" 2>/dev/null || true
}

# Function to process a single model
process_model() {
    local modelfile=$1
    local tag=$2

    print_header "Processing ${MODEL_BASE}:${tag}"

    # Build the model
    if build_model "$modelfile" "$tag"; then
        # Copy to namespace
        if copy_model "$tag" "$tag"; then
            # Push to hub
            if push_model "$tag"; then
                print_success "Successfully processed ${MODEL_BASE}:${tag}"
                # Optionally clean up local model
                # cleanup_local "$tag"
                return 0
            fi
        fi
    fi

    print_error "Failed to process ${MODEL_BASE}:${tag}"
    return 1
}

# Function to show authentication help
show_auth_help() {
    print_header "Ollama Hub Authentication"
    echo -e "${CYAN}To push models to Ollama Hub, you need to authenticate:${NC}"
    echo -e "${YELLOW}1.${NC} Create an account at https://ollama.com"
    echo -e "${YELLOW}2.${NC} Generate an API key in your account settings"
    echo -e "${YELLOW}3.${NC} Set the OLLAMA_API_KEY environment variable:"
    echo -e "   ${CYAN}export OLLAMA_API_KEY=your_api_key_here${NC}"
    echo -e "${YELLOW}4.${NC} Or authenticate using: ${CYAN}ollama login${NC}"
    echo ""
    echo -e "${CYAN}For SSH authentication:${NC}"
    echo -e "${YELLOW}1.${NC} Add your SSH key to https://ollama.com/settings/keys"
    echo -e "${YELLOW}2.${NC} Your SSH key is:"
    if [ -f ~/.ollama/id_ed25519.pub ]; then
        cat ~/.ollama/id_ed25519.pub
    else
        echo -e "${RED}No SSH key found at ~/.ollama/id_ed25519.pub${NC}"
    fi
    echo ""
}

# Main function
main() {
    print_header "🦙 Llamaball Model Builder & Publisher"

    # Check prerequisites
    check_ollama

    # Show configuration
    print_status "Configuration:"
    print_status "  Namespace: ${NAMESPACE}"
    print_status "  Model base: ${MODEL_BASE}"
    echo ""

    # Show current models
    print_status "Current models:"
    ollama list
    echo ""

    # Hardcoded model list: (modelfile, tag)
    # These must match the actual files in Modelfiles/
    MODELS=(
        "Modelfile.gemma3:1b 1b"
        "Modelfile.gemma3:4b 4b"
        "Modelfile.gemma3:27b 27b"
        "Modelfile.llama3.2:1b llama-1b"
        "Modelfile.llama3.2:3b llama-3b"
        "Modelfile.qwen3:0.6b qwen-0.6b"
        "Modelfile.qwen3:1.7b qwen-1.7b"
        "Modelfile.qwen3:4b qwen-4b"
    )

    local success_count=0
    local total_count=${#MODELS[@]}
    local failed_models=()

    # Process each model sequentially
    for entry in "${MODELS[@]}"; do
        # Split entry into modelfile and tag
        modelfile=$(echo "$entry" | awk '{print $1}')
        tag=$(echo "$entry" | awk '{print $2}')

        # Check if modelfile exists in Modelfiles/
        if [[ ! -f "${MODELFILES_DIR}/${modelfile}" ]]; then
            print_error "Modelfile not found: ${MODELFILES_DIR}/${modelfile}"
            failed_models+=("$tag")
            continue
        fi

        if process_model "$modelfile" "$tag"; then
            ((success_count++))
        else
            failed_models+=("$tag")
        fi

        echo ""  # Add spacing between models
    done

    # Summary
    print_header "Build & Push Summary"
    print_success "Successfully processed: ${success_count}/${total_count} models"

    if [ ${#failed_models[@]} -gt 0 ]; then
        print_warning "Failed models:"
        for model in "${failed_models[@]}"; do
            echo -e "  ${RED}✗${NC} ${MODEL_BASE}:${model}"
        done

        if [[ "${failed_models[*]}" =~ "push" ]]; then
            echo ""
            show_auth_help
        fi
    else
        print_success "All models processed successfully! 🎉"
    fi

    # Show final model list
    echo ""
    print_status "Final model list:"
    ollama list
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h         Show this help message"
        echo "  --auth-help        Show authentication help"
        echo "  --dry-run          Show what would be done without executing"
        echo ""
        echo "This script builds and pushes all Llamaball models to the coolhand namespace."
        exit 0
        ;;
    --auth-help)
        show_auth_help
        exit 0
        ;;
    --dry-run)
        echo "DRY RUN MODE - Would process these models to namespace: $NAMESPACE"
        for entry in \
            "Modelfile.gemma3:1b 1b" \
            "Modelfile.gemma3:4b 4b" \
            "Modelfile.gemma3:27b 27b" \
            "Modelfile.llama3.2:1b llama-1b" \
            "Modelfile.llama3.2:3b llama-3b" \
            "Modelfile.qwen3:0.6b qwen-0.6b" \
            "Modelfile.qwen3:1.7b qwen-1.7b" \
            "Modelfile.qwen3:4b qwen-4b"
        do
            modelfile=$(echo "$entry" | awk '{print $1}')
            tag=$(echo "$entry" | awk '{print $2}')
            echo "Would process: ${MODELFILES_DIR}/${modelfile} -> ${NAMESPACE}/${MODEL_BASE}:${tag}"
        done
        exit 0
        ;;
    *)
        # Ignore any other arguments
        ;;
esac

# Run main function
main "$@"