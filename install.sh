#!/bin/bash
# BlondE-CLI Installation Script for Linux/macOS
# Usage: bash install.sh [--gpu nvidia|metal] [--dev]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════╗"
echo "║       BlondE-CLI Installation Script      ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo -e "${GREEN}✓ Detected: Linux${NC}"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo -e "${GREEN}✓ Detected: macOS${NC}"
else
    echo -e "${RED}✗ Unsupported OS: $OSTYPE${NC}"
    exit 1
fi

# Parse arguments
GPU_SUPPORT=""
DEV_MODE=false

for arg in "$@"; do
    case $arg in
        --gpu=nvidia)
            GPU_SUPPORT="nvidia"
            echo -e "${YELLOW}GPU Support: NVIDIA CUDA${NC}"
            ;;
        --gpu=metal)
            GPU_SUPPORT="metal"
            echo -e "${YELLOW}GPU Support: Apple Metal${NC}"
            ;;
        --dev)
            DEV_MODE=true
            echo -e "${YELLOW}Development mode enabled${NC}"
            ;;
        --help)
            echo "Usage: bash install.sh [OPTIONS]"
            echo "Options:"
            echo "  --gpu=nvidia     Install with NVIDIA GPU support"
            echo "  --gpu=metal      Install with Apple Metal GPU support"
            echo "  --dev            Install development dependencies"
            echo "  --help           Show this help message"
            exit 0
            ;;
    esac
done

# Check Python version
echo -e "\n${CYAN}[1/6] Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
REQUIRED_VERSION="3.10"

if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
    echo -e "${RED}✗ Python $PYTHON_VERSION found, but 3.10+ required${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Install system dependencies
echo -e "\n${CYAN}[2/6] Installing system dependencies...${NC}"

if [[ "$OS" == "linux" ]]; then
    # Check if running as root or with sudo
    if [[ $EUID -ne 0 ]]; then
        SUDO="sudo"
    else
        SUDO=""
    fi
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        echo "Using apt (Debian/Ubuntu)"
        $SUDO apt-get update -qq
        $SUDO apt-get install -y -qq libmagic1 build-essential git
    elif command -v yum &> /dev/null; then
        echo "Using yum (RHEL/CentOS)"
        $SUDO yum install -y file-libs gcc git
    elif command -v pacman &> /dev/null; then
        echo "Using pacman (Arch)"
        $SUDO pacman -S --noconfirm file gcc git
    else
        echo -e "${YELLOW}⚠ Unknown package manager. Please install: libmagic, build-essential, git${NC}"
    fi
    
elif [[ "$OS" == "macos" ]]; then
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}⚠ Homebrew not found. Installing...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    echo "Using Homebrew"
    brew install libmagic 2>/dev/null || echo "libmagic already installed"
fi

echo -e "${GREEN}✓ System dependencies installed${NC}"

# Create virtual environment
echo -e "\n${CYAN}[3/6] Setting up Python virtual environment...${NC}"

if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "\n${CYAN}[4/6] Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel -q
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install llama-cpp-python with GPU support if requested
if [[ -n "$GPU_SUPPORT" ]]; then
    echo -e "\n${CYAN}[5/6] Installing llama-cpp-python with GPU support...${NC}"
    
    if [[ "$GPU_SUPPORT" == "nvidia" ]]; then
        echo "Building with CUDA support (this may take a few minutes)..."
        CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
    elif [[ "$GPU_SUPPORT" == "metal" ]]; then
        echo "Building with Metal support (this may take a few minutes)..."
        CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
    fi
    
    echo -e "${GREEN}✓ llama-cpp-python installed with GPU support${NC}"
fi

# Install BlondE-CLI
echo -e "\n${CYAN}[${GPU_SUPPORT:+6/6}${GPU_SUPPORT:-5/6}] Installing BlondE-CLI...${NC}"

if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt -q
else
    echo -e "${YELLOW}⚠ requirements.txt not found, using pyproject.toml${NC}"
fi

# Install in development mode or production mode
if [[ "$DEV_MODE" == true ]]; then
    pip install -e ".[dev]" -q 2>/dev/null || pip install -e . -q
    echo -e "${GREEN}✓ Installed in development mode${NC}"
else
    pip install -e . -q
    echo -e "${GREEN}✓ Installed in production mode${NC}"
fi

# Create config directory
mkdir -p ~/.blonde/models
mkdir -p ~/.blonde/memory

# Copy example config if not exists
if [[ -f ".env.example" ]] && [[ ! -f ".env" ]]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠ Created .env from .env.example. Please add your API keys.${NC}"
fi

# Test installation
echo -e "\n${CYAN}[Testing installation...]${NC}"
if command -v blnd &> /dev/null; then
    echo -e "${GREEN}✓ blnd command available${NC}"
    blnd --help > /dev/null 2>&1
    echo -e "${GREEN}✓ BlondE-CLI is working!${NC}"
else
    echo -e "${YELLOW}⚠ blnd command not found in PATH. You may need to activate the virtual environment:${NC}"
    echo -e "${CYAN}  source venv/bin/activate${NC}"
fi

# Final instructions
echo -e "\n${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Installation Complete! 🚀              ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo -e "  1. Activate virtual environment: ${YELLOW}source venv/bin/activate${NC}"
echo -e "  2. Set API keys: ${YELLOW}blnd set-key openrouter YOUR_KEY${NC}"
echo -e "  3. Start chatting: ${YELLOW}blnd chat${NC}"
echo ""
echo -e "${CYAN}Optional:${NC}"
echo -e "  • Download local model: ${YELLOW}blnd chat --offline --model TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf${NC}"
echo -e "  • View help: ${YELLOW}blnd --help${NC}"
echo ""
echo -e "${CYAN}Documentation:${NC} https://github.com/cerekin/blonde-cli"
echo ""
