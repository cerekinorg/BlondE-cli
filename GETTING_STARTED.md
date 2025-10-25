# 🚀 Getting Started with BlondE-CLI

**Complete guide for new users to download and start using BlondE from GitHub**

---

## 📍 Repository

**GitHub:** https://github.com/cerekinorg/BlondE-cli

---

## ⚡ Quick Install (3 Methods)

### Method 1: One-Line Install (Easiest)

```bash
curl -fsSL https://raw.githubusercontent.com/cerekinorg/BlondE-cli/main/quick-install.sh | bash
```

This will:
- Clone the repository
- Create virtual environment
- Install all dependencies
- Verify installation

---

### Method 2: Manual Install (Most Control)

```bash
# 1. Clone the repository
git clone https://github.com/cerekinorg/BlondE-cli.git
cd BlondE-cli

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install BlondE
pip install -e .

# 4. Verify
blnd --help
```

---

### Method 3: Download ZIP (No Git Required)

1. Go to https://github.com/cerekinorg/BlondE-cli
2. Click green "Code" button → "Download ZIP"
3. Extract the ZIP file
4. Open terminal in extracted folder
5. Run:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

---

## 🎯 First Steps After Installation

### Option A: Start with Offline Mode (No API Key)

```bash
# Activate virtual environment
cd BlondE-cli
source venv/bin/activate

# Start chatting
blnd chat --offline
```

**What happens:**
1. Interactive menu appears
2. Select or download a model (~3.8GB, first time only)
3. Start chatting with AI (100% private, offline)

---

### Option B: Use Online Models (Best Quality)

```bash
# Get free API key from https://openrouter.ai

# Set the key
blnd set-key --provider openrouter

# Start chatting
blnd chat
```

---

## 📚 Documentation Guide

### For First-Time Users

**Start Here:**
1. **INSTALL.md** - Complete installation instructions
2. **LOCAL_MODELS_QUICKSTART.md** - Quick offline setup
3. **USER_GUIDE.md** - Feature overview

### For Advanced Users

4. **LOCAL_MODELS_GUIDE.md** - Complete offline guide
5. **INTERACTIVE_MODEL_SELECTION.md** - Model selector details
6. **CONTRIBUTING.md** - How to contribute

### For Developers

7. **README.md** - Project overview
8. **tests/** - Test suite
9. **CONTRIBUTING.md** - Development guide

---

## 💻 Common Commands

### Chat
```bash
# Online chat
blnd chat

# Offline chat
blnd chat --offline

# With memory
blnd chat --memory

# With tools
blnd chat --agentic
```

### Generate Code
```bash
# Generate code
blnd gen "create a REST API"

# Save to file
blnd gen "quicksort algorithm" --save sort.py

# Offline mode
blnd gen "your prompt" --offline
```

### Fix Bugs
```bash
# Fix a file
blnd fix myfile.py

# Fix directory
blnd fix ./src --preview

# With suggestions
blnd fix file.py --suggest --iterative
```

### Create Files
```bash
# Create new file
blnd create "user auth module" auth.py

# With tests
blnd create "calculator" calc.py --with-tests

# Offline
blnd create "description" file.py --offline
```

### Documentation
```bash
# Document file
blnd doc mycode.py

# Document project
blnd doc ./src --export DOCS.md

# Tutorial style
blnd doc file.py --style tutorial
```

---

## 🔧 Troubleshooting

### Issue: `blnd: command not found`

**Solution:**
```bash
# Make sure virtual environment is activated
cd BlondE-cli
source venv/bin/activate

# Verify installation
which blnd
```

### Issue: `No module named 'typer'`

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
pip install -e .
```

### Issue: API key not working

**Solution:**
```bash
# Use offline mode instead
blnd chat --offline

# Or reset API key
blnd set-key --provider openrouter
```

### Issue: Model download fails

**Solution:**
```bash
# Check internet connection
ping huggingface.co

# Check disk space
df -h ~

# Try manual download (see LOCAL_MODELS_GUIDE.md)
```

---

## 🎓 Learning Path

### Day 1: Get Started
1. Install BlondE
2. Try `blnd chat --offline`
3. Generate simple code

### Day 2: Explore Features
4. Try `blnd fix` on a file
5. Generate documentation
6. Explore memory features

### Day 3: Advanced Usage
7. Enable agentic mode
8. Use iterative refinement
9. Try different models

---

## 🌟 Pro Tips

### Tip 1: Create an Alias
```bash
# Add to ~/.bashrc or ~/.zshrc
alias blonde="cd ~/BlondE-cli && source venv/bin/activate && blnd"

# Usage
blonde chat --offline
```

### Tip 2: Add to PATH
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/BlondE-cli/venv/bin:$PATH"

# Now blnd works from anywhere
blnd chat
```

### Tip 3: Use .env for API Keys
```bash
# Create .env file in BlondE-cli directory
echo "OPENROUTER_API_KEY=your-key-here" > .env

# BlondE will auto-load it
```

### Tip 4: Check Logs for Issues
```bash
# View debug log
tail -f ~/.blonde/debug.log

# Clear cache if needed
rm -rf ~/.blonde/models/*
```

---

## 📦 What Gets Installed

### Core Files
- `cli.py` - Main application
- `memory.py` - Memory system
- `tools.py` - Agentic tools
- `model_selector.py` - Model selector
- `models/` - Model adapters

### Dependencies
- `typer` - CLI framework
- `rich` - Terminal UI
- `chromadb` - Vector database
- `llama-cpp-python` - Local models
- `openai` - API client
- And more (see requirements.txt)

### Data Directories
- `~/.blonde/models/` - Cached models
- `~/.blonde/memory/` - Memory database
- `~/.blonde/tool_logs/` - Tool usage logs
- `~/.blonde/debug.log` - Debug logs

---

## 🔐 Privacy & Security

### Offline Mode
- ✅ 100% private - no data sent externally
- ✅ Works without internet
- ✅ Models cached locally
- ✅ No API keys needed

### Online Mode
- ⚠️ Data sent to AI provider (OpenRouter, OpenAI, etc.)
- ✅ API keys stored securely (keyring)
- ✅ No logging by BlondE
- ✅ Use reputable providers

### Agentic Mode
- ⚠️ AI can access files you specify
- ✅ Requires your confirmation for actions
- ✅ All actions logged
- ✅ Can be disabled anytime

---

## 🤝 Get Help

### Documentation
- Read `INSTALL.md` for detailed setup
- Check `USER_GUIDE.md` for features
- See `LOCAL_MODELS_GUIDE.md` for offline use

### Community
- **Issues:** https://github.com/cerekinorg/BlondE-cli/issues
- **Discussions:** https://github.com/cerekinorg/BlondE-cli/discussions
- **Contributing:** See CONTRIBUTING.md

### Quick Help
```bash
# Command help
blnd --help
blnd chat --help
blnd gen --help

# Version
blnd --version

# Debug mode
blnd chat --debug
```

---

## 🎉 You're Ready!

**Start with:**
```bash
blnd chat --offline
```

**Or:**
```bash
blnd gen "your first idea"
```

Welcome to BlondE-CLI! 🚀

---

## 📋 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│                 BlondE-CLI Quick Ref                │
├─────────────────────────────────────────────────────┤
│ Install:  git clone + pip install -e .              │
│ Chat:     blnd chat --offline                       │
│ Generate: blnd gen "prompt" --save file.py          │
│ Fix:      blnd fix myfile.py                        │
│ Create:   blnd create "desc" file.py --with-tests   │
│ Doc:      blnd doc project/ --export DOCS.md        │
│ Help:     blnd --help                               │
│ Logs:     tail ~/.blonde/debug.log                  │
└─────────────────────────────────────────────────────┘
```

**Repository:** https://github.com/cerekinorg/BlondE-cli
