# 🚀 BlondE-CLI Installation Guide

Complete installation instructions for **BlondE-CLI** - An AI-powered code assistant with memory and agentic capabilities.

**GitHub Repository:** https://github.com/cerekinorg/BlondE-cli

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Quick Start](#quick-start)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## ⚙️ Prerequisites

### System Requirements
- **Python:** 3.10 or higher
- **OS:** Linux, macOS, or Windows (WSL recommended)
- **RAM:** 8GB minimum (16GB+ for local models)
- **Storage:** 5GB+ free space

### Check Python Version
```bash
python3 --version  # Should show 3.10 or higher
```

---

## 📥 Installation Methods

### Method 1: Install from GitHub (Recommended)

#### Step 1: Clone the Repository
```bash
git clone https://github.com/cerekinorg/BlondE-cli.git
cd BlondE-cli
```

#### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 3: Install BlondE
```bash
pip install -e .
```

This installs all dependencies and creates the `blnd` command.

#### Step 4: Verify Installation
```bash
blnd --help
```

You should see the BlondE-CLI help menu!

---

### Method 2: Quick Install Script (One-Command)

```bash
curl -fsSL https://raw.githubusercontent.com/cerekinorg/BlondE-cli/main/install.sh | bash
```

Or download and run manually:
```bash
wget https://raw.githubusercontent.com/cerekinorg/BlondE-cli/main/install.sh
chmod +x install.sh
./install.sh
```

---

### Method 3: Manual Installation (Advanced)

```bash
# Clone repository
git clone https://github.com/cerekinorg/BlondE-cli.git
cd BlondE-cli

# Install dependencies manually
pip install -r requirements.txt

# Run directly
python cli.py --help
```

---

## 🔑 Configuration

### Option 1: Using Online Models (OpenRouter/OpenAI)

BlondE can use cloud-based AI models for the best performance.

#### Set API Key (Required for online models)
```bash
# OpenRouter (Free tier available)
blnd set-key --provider openrouter
# Enter your API key when prompted

# Or OpenAI
blnd set-key --provider openai
# Enter your API key when prompted
```

#### Get Free API Keys
- **OpenRouter:** https://openrouter.ai/ (Free models available)
- **OpenAI:** https://platform.openai.com/api-keys (Paid)
- **HuggingFace:** https://huggingface.co/settings/tokens (Free)

---

### Option 2: Using Local Models (100% Offline)

BlondE supports local GGUF models for complete privacy and offline use.

**No API key needed!** Just run with `--offline` flag:
```bash
blnd chat --offline
```

First run will show an interactive menu to download a model (~3.8GB, 5-10 minutes).

**See:** `LOCAL_MODELS_GUIDE.md` for complete offline setup.

---

## 🚀 Quick Start

### 1. Interactive Chat
```bash
# With online model (requires API key)
blnd chat

# With local model (offline, no API key)
blnd chat --offline
```

### 2. Generate Code
```bash
# Generate code from description
blnd gen "create a Python REST API with FastAPI"

# Save to file
blnd gen "quicksort algorithm" --save quicksort.py

# Use offline model
blnd gen "binary search tree" --offline
```

### 3. Fix Bugs
```bash
# Fix a single file
blnd fix buggy_code.py

# Fix entire directory
blnd fix ./src --preview

# Use offline model
blnd fix myfile.py --offline
```

### 4. Create Files
```bash
# Create with description
blnd create "user authentication module" auth.py

# With tests
blnd create "calculator class" calc.py --with-tests

# Iterative refinement
blnd create "API server" server.py --iterative
```

### 5. Generate Documentation
```bash
# Document a file
blnd doc mycode.py

# Document entire project
blnd doc ./src --export DOCS.md

# Different styles
blnd doc module.py --style tutorial
```

---

## ✅ Verification

### Test Installation
```bash
# Check version
blnd --version

# Check available commands
blnd --help

# Test online mode (requires API key)
blnd gen "hello world in Python" --save test.py

# Test offline mode (downloads model first time)
blnd chat --offline
```

### Expected Output
```
✓ blnd command works
✓ All dependencies installed
✓ Can generate code
✓ Interactive chat works
```

---

## 🛠️ Troubleshooting

### Issue: `blnd: command not found`

**Solution 1:** Activate virtual environment
```bash
source venv/bin/activate
```

**Solution 2:** Add to PATH (permanent)
```bash
echo 'export PATH="$HOME/BlondE-cli/venv/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Solution 3:** Use full path
```bash
/path/to/BlondE-cli/venv/bin/blnd --help
```

---

### Issue: `ModuleNotFoundError: No module named 'typer'`

**Solution:** Reinstall dependencies
```bash
cd BlondE-cli
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

---

### Issue: `WARNING: Memory system not available`

**Solution:** These warnings are normal and don't affect functionality. They only appear in debug logs, not in normal output.

If you want to enable memory features:
```bash
pip install chromadb
```

---

### Issue: API key not working

**Solution 1:** Check API key is set
```bash
blnd set-key --provider openrouter
```

**Solution 2:** Use offline mode
```bash
blnd chat --offline
```

**Solution 3:** Check `.env` file
```bash
cat .env
# Should contain: OPENROUTER_API_KEY=your-key-here
```

---

### Issue: Local model download fails

**Solution 1:** Check internet connection
```bash
ping huggingface.co
```

**Solution 2:** Use manual download
```bash
pip install huggingface-hub[cli]
huggingface-cli download TheBloke/CodeLlama-7B-GGUF codellama-7b.Q4_K_M.gguf --cache-dir ~/.blonde/models
```

**Solution 3:** Check disk space
```bash
df -h ~
# Need at least 5GB free
```

---

### Issue: Permission denied

**Solution:** Make scripts executable
```bash
chmod +x install.sh
chmod +x venv/bin/blnd
```

---

## 📚 Next Steps

### Learn More
- **User Guide:** `USER_GUIDE.md` - Complete feature documentation
- **Local Models:** `LOCAL_MODELS_GUIDE.md` - Offline model setup
- **Quick Reference:** `LOCAL_MODELS_QUICKSTART.md` - Fast command reference
- **Interactive Selection:** `INTERACTIVE_MODEL_SELECTION.md` - Model selector guide

### Join the Community
- **GitHub Issues:** https://github.com/cerekinorg/BlondE-cli/issues
- **Discussions:** https://github.com/cerekinorg/BlondE-cli/discussions
- **Contributing:** See `CONTRIBUTING.md`

### Get Help
```bash
# Command help
blnd --help
blnd chat --help
blnd gen --help

# Check logs
tail ~/.blonde/debug.log

# Run tests
pytest tests/
```

---

## 🎯 Common Workflows

### For Beginners (Free, Offline)
```bash
# 1. Install
git clone https://github.com/cerekinorg/BlondE-cli.git
cd BlondE-cli
python3 -m venv venv
source venv/bin/activate
pip install -e .

# 2. Start chatting (offline, no API key)
blnd chat --offline
# First run downloads model (5-10 min)

# 3. Start coding!
blnd gen "your idea" --offline
```

### For Developers (Online, Best Quality)
```bash
# 1. Install
git clone https://github.com/cerekinorg/BlondE-cli.git
cd BlondE-cli
python3 -m venv venv
source venv/bin/activate
pip install -e .

# 2. Set API key
blnd set-key --provider openrouter
# Get free key at https://openrouter.ai

# 3. Use with memory and tools
blnd chat --memory --agentic
blnd create "your project" file.py --with-tests
```

---

## 🔐 Security Notes

### API Keys
- Never commit API keys to git
- Store in `.env` file (gitignored)
- Use environment variables for CI/CD

### Local Models
- 100% private - no data sent externally
- Models cached in `~/.blonde/models/`
- Safe for sensitive code

### Permissions
- BlondE only accesses files you specify
- Agentic mode requires confirmation for actions
- All tool usage is logged

---

## 📦 Dependencies

### Core (Auto-installed)
- typer - CLI framework
- rich - Terminal UI
- chromadb - Vector database for memory
- openai - OpenAI API client
- huggingface-hub - Model downloads
- llama-cpp-python - Local model inference

### Optional
- pytest - Testing
- black - Code formatting
- mypy - Type checking

---

## 🚀 You're Ready!

**Start with:**
```bash
blnd chat --offline
```

**Or:**
```bash
blnd gen "your first idea"
```

Welcome to BlondE-CLI! 🎉

---

**Need help?** Open an issue at https://github.com/cerekinorg/BlondE-cli/issues
