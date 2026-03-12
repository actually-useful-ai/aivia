#!/bin/bash
# Ollama Hub Authentication Setup Script
# File Purpose: Help users authenticate with Ollama Hub for model publishing
# Primary Functions: check_auth, setup_auth, test_auth
# Inputs: User credentials and API keys
# Outputs: Authenticated Ollama session

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

# Check if already authenticated
check_auth() {
    print_status "Checking current authentication status..."
    
    # Try to list models from the user's namespace
    if ollama list | grep -q "coolhand/" 2>/dev/null; then
        print_success "You appear to have lukeslp models locally"
        return 0
    fi
    
    # Try a simple push test (this will fail but show auth status)
    if ollama push coolhand/test 2>&1 | grep -q "not authorized"; then
        print_warning "Not authenticated with Ollama Hub"
        return 1
    fi
    
    print_success "Authentication appears to be working"
    return 0
}

# Test authentication by trying to push a small test model
test_auth() {
    print_status "Testing authentication..."
    
    # Create a minimal test model
    cat > /tmp/test_modelfile << EOF
FROM scratch
SYSTEM "This is a test model for authentication verification."
EOF
    
    # Try to create and push a test model
    if ollama create -f /tmp/test_modelfile coolhand/auth-test 2>/dev/null; then
        if ollama push coolhand/auth-test 2>/dev/null; then
            print_success "Authentication test successful!"
            ollama rm coolhand/auth-test 2>/dev/null || true
            rm -f /tmp/test_modelfile
            return 0
        else
            print_error "Authentication test failed - cannot push to lukeslp namespace"
            ollama rm coolhand/auth-test 2>/dev/null || true
            rm -f /tmp/test_modelfile
            return 1
        fi
    else
        print_error "Failed to create test model"
        rm -f /tmp/test_modelfile
        return 1
    fi
}

# Show authentication options
show_auth_options() {
    print_header "🔐 Ollama Hub Authentication Options"
    
    echo -e "${CYAN}Option 1: Environment Variable (Recommended)${NC}"
    echo -e "  ${YELLOW}1.${NC} Get your API key from https://ollama.com/settings"
    echo -e "  ${YELLOW}2.${NC} Export it as an environment variable:"
    echo -e "     ${CYAN}export OLLAMA_API_KEY=your_api_key_here${NC}"
    echo -e "  ${YELLOW}3.${NC} Add to your shell profile for persistence:"
    echo -e "     ${CYAN}echo 'export OLLAMA_API_KEY=your_api_key_here' >> ~/.bashrc${NC}"
    echo ""
    
    echo -e "${CYAN}Option 2: Interactive Login${NC}"
    echo -e "  ${YELLOW}1.${NC} Run: ${CYAN}ollama login${NC}"
    echo -e "  ${YELLOW}2.${NC} Enter your Ollama Hub credentials when prompted"
    echo ""
    
    echo -e "${CYAN}Option 3: SSH Key (Advanced)${NC}"
    echo -e "  ${YELLOW}1.${NC} Generate SSH key: ${CYAN}ssh-keygen -t ed25519 -f ~/.ssh/ollama_hub${NC}"
    echo -e "  ${YELLOW}2.${NC} Add public key to your Ollama Hub account"
    echo -e "  ${YELLOW}3.${NC} Configure SSH agent"
    echo ""
}

# Interactive setup
interactive_setup() {
    print_header "🚀 Interactive Authentication Setup"
    
    echo -e "${CYAN}Choose your authentication method:${NC}"
    echo -e "  ${YELLOW}1)${NC} Set API Key (environment variable)"
    echo -e "  ${YELLOW}2)${NC} Interactive login"
    echo -e "  ${YELLOW}3)${NC} Show all options"
    echo -e "  ${YELLOW}4)${NC} Skip setup"
    echo ""
    
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            echo ""
            echo -e "${CYAN}Please enter your Ollama Hub API key:${NC}"
            echo -e "${YELLOW}(Get it from: https://ollama.com/settings)${NC}"
            read -s -p "API Key: " api_key
            echo ""
            
            if [[ -n "$api_key" ]]; then
                export OLLAMA_API_KEY="$api_key"
                echo -e "${GREEN}API key set for this session${NC}"
                echo ""
                echo -e "${YELLOW}To make this permanent, add this to your ~/.bashrc:${NC}"
                echo -e "${CYAN}export OLLAMA_API_KEY='$api_key'${NC}"
                echo ""
                
                # Test the authentication
                if test_auth; then
                    print_success "Authentication setup complete!"
                    return 0
                else
                    print_error "Authentication test failed. Please check your API key."
                    return 1
                fi
            else
                print_error "No API key provided"
                return 1
            fi
            ;;
        2)
            print_status "Starting interactive login..."
            if ollama login; then
                print_success "Login successful!"
                test_auth
                return $?
            else
                print_error "Login failed"
                return 1
            fi
            ;;
        3)
            show_auth_options
            return 0
            ;;
        4)
            print_warning "Skipping authentication setup"
            print_warning "You'll need to authenticate before pushing models"
            return 1
            ;;
        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
}

# Main function
main() {
    print_header "🦙 Ollama Hub Authentication Setup"
    
    # Check current status
    if check_auth; then
        print_success "You appear to be already authenticated!"
        echo ""
        read -p "Do you want to test authentication? (y/N): " test_choice
        if [[ "$test_choice" =~ ^[Yy]$ ]]; then
            test_auth
        fi
        return 0
    fi
    
    echo ""
    print_warning "Authentication required to push models to Ollama Hub"
    echo ""
    
    # Check if API key is already set
    if [[ -n "$OLLAMA_API_KEY" ]]; then
        print_status "OLLAMA_API_KEY environment variable is set"
        if test_auth; then
            return 0
        else
            print_error "API key appears to be invalid"
        fi
    fi
    
    # Interactive setup
    interactive_setup
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h      Show this help message"
        echo "  --check         Check authentication status only"
        echo "  --test          Test authentication only"
        echo "  --options       Show authentication options"
        echo ""
        echo "This script helps you authenticate with Ollama Hub."
        exit 0
        ;;
    --check)
        check_auth
        exit $?
        ;;
    --test)
        test_auth
        exit $?
        ;;
    --options)
        show_auth_options
        exit 0
        ;;
esac

# Run main function
main "$@" 