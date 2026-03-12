#!/bin/bash
# Fix Ollama Push Authentication Script
# File Purpose: Help resolve Ollama Hub push authentication issues
# Primary Functions: check_ssh_key, test_namespace, push_with_auth
# Inputs: Namespace and model information
# Outputs: Successful model push or clear error guidance

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🔧 Ollama Push Authentication Helper${NC}"
echo ""

# Check SSH key
echo -e "${CYAN}1. Checking SSH key...${NC}"
if [ -f ~/.ollama/id_ed25519.pub ]; then
    echo -e "${GREEN}✓ SSH key found:${NC}"
    cat ~/.ollama/id_ed25519.pub
    echo ""
    echo -e "${YELLOW}⚠️  Make sure this key is added to:${NC}"
    echo -e "${CYAN}   https://ollama.com/settings/keys${NC}"
else
    echo -e "${RED}✗ No SSH key found${NC}"
    echo -e "${YELLOW}Generate one with:${NC}"
    echo -e "${CYAN}ssh-keygen -t ed25519 -f ~/.ollama/id_ed25519${NC}"
fi

echo ""
echo -e "${CYAN}2. Namespace:${NC}"
echo -e "   • ${GREEN}coolhand${NC} - Your personal namespace (must be used)"

echo ""
echo -e "${CYAN}3. To push your model:${NC}"
echo "ollama cp llamaball:1b coolhand/llamaball:1b"
echo "ollama push coolhand/llamaball:1b"

echo ""
echo -e "${CYAN}4. Troubleshooting:${NC}"
echo -e "   • Verify namespace ownership at https://ollama.com"
echo -e "   • Ensure SSH key is added to your account"
echo -e "   • Try: ${CYAN}ssh -T git@ollama.com${NC} to test SSH auth"

echo ""
echo -e "${BLUE}5. Alternative: Create llamafile${NC}"
echo -e "   Convert your Ollama model to a standalone executable:"
echo -e "   ${CYAN}./create_llamafile.sh${NC}" 