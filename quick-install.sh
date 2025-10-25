#!/bin/bash
# BlondE-CLI Quick Install Script
# Usage: curl -fsSL https://raw.githubusercontent.com/cerekinorg/BlondE-cli/main/quick-install.sh | bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║          🤖 BlondE-CLI Installation Script                   ║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo -e "${YELLOW}Please install Python 3.10 or higher${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}"
echo ""

# Clone repository
echo -e "${BLUE}Cloning BlondE-CLI repository...${NC}"
if [ -d "BlondE-cli" ]; then
    echo -e "${YELLOW}⚠ BlondE-cli directory already exists${NC}"
    read -p "Remove and reinstall? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf BlondE-cli
    else
        echo -e "${YELLOW}Installation cancelled${NC}"
        exit 1
    fi
fi

git clone https://github.com/cerekinorg/BlondE-cli.git
cd BlondE-cli
echo -e "${GREEN}✓ Repository cloned${NC}"
echo ""

# Create virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
python3 -m venv venv
echo -e "${GREEN}✓ Virtual environment created${NC}"
echo ""

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install BlondE
echo -e "${BLUE}Installing BlondE-CLI and dependencies...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -e . > /dev/null 2>&1
echo -e "${GREEN}✓ BlondE-CLI installed${NC}"
echo ""

# Verify installation
echo -e "${BLUE}Verifying installation...${NC}"
if command -v blnd &> /dev/null; then
    echo -e "${GREEN}✓ blnd command is available${NC}"
else
    echo -e "${RED}✗ blnd command not found${NC}"
    echo -e "${YELLOW}You may need to activate the virtual environment:${NC}"
    echo -e "  cd BlondE-cli"
    echo -e "  source venv/bin/activate"
    exit 1
fi
echo ""

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║          ✅ Installation Complete!                           ║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}🚀 Quick Start:${NC}"
echo ""
echo -e "${YELLOW}Option 1: Use Offline (No API Key)${NC}"
echo -e "  $ blnd chat --offline"
echo -e "  ${GREEN}(Downloads model on first run, ~3.8GB)${NC}"
echo ""
echo -e "${YELLOW}Option 2: Use Online (Best Quality)${NC}"
echo -e "  $ blnd set-key --provider openrouter"
echo -e "  ${GREEN}(Get free key at https://openrouter.ai)${NC}"
echo -e "  $ blnd chat"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo -e "  INSTALL.md - Complete installation guide"
echo -e "  USER_GUIDE.md - Full feature documentation"
echo -e "  LOCAL_MODELS_GUIDE.md - Offline model setup"
echo ""
echo -e "${BLUE}💡 Need help?${NC} https://github.com/cerekinorg/BlondE-cli/issues"
echo ""
echo -e "${GREEN}Happy coding! 🎉${NC}"
