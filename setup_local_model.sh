#!/bin/bash
# Quick setup script for local models

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}BlondE-CLI Local Model Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if llama-cpp-python is installed
if ./venv/bin/python -c "import llama_cpp" 2>/dev/null; then
    echo -e "${GREEN}✓ llama-cpp-python is installed${NC}"
else
    echo -e "${YELLOW}Installing llama-cpp-python...${NC}"
    ./venv/bin/pip install llama-cpp-python
    echo -e "${GREEN}✓ llama-cpp-python installed${NC}"
fi

echo ""
echo -e "${BLUE}Available Commands:${NC}"
echo ""
echo -e "${GREEN}# Quick test (will download model on first run):${NC}"
echo "blnd chat --offline"
echo ""
echo -e "${GREEN}# Use specific model:${NC}"
echo "blnd chat --offline --model TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
echo ""
echo -e "${GREEN}# Generate code offline:${NC}"
echo "blnd gen \"create a Python calculator\" --offline"
echo ""
echo -e "${YELLOW}⚠️  First run will download ~3.8GB model (5-10 minutes)${NC}"
echo -e "${YELLOW}⚠️  Subsequent runs will be instant (uses cached model)${NC}"
echo ""
echo -e "${BLUE}Models are cached at: ~/.blonde/models/${NC}"
echo ""
echo -e "${GREEN}✅ Local model support is ready!${NC}"
echo ""
