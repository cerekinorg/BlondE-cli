# 📢 How Others Can Download and Use BlondE from GitHub

**GitHub Repository:** https://github.com/cerekinorg/BlondE-cli

---

## 🚀 3 Ways to Install

### Option 1: One-Line Quick Install (Easiest)

```bash
curl -fsSL https://raw.githubusercontent.com/cerekinorg/BlondE-cli/main/quick-install.sh | bash
```

**What this does:**
- Clones the repository
- Creates virtual environment
- Installs all dependencies
- Verifies installation works

---

### Option 2: Manual Install (Most Common)

```bash
# Step 1: Clone repository
git clone https://github.com/cerekinorg/BlondE-cli.git
cd BlondE-cli

# Step 2: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Step 3: Install
pip install -e .

# Step 4: Verify
blnd --help
```

---

### Option 3: Download ZIP (No Git)

1. Visit https://github.com/cerekinorg/BlondE-cli
2. Click green "Code" button → "Download ZIP"
3. Extract ZIP file
4. Open terminal in extracted folder
5. Run:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

---

## ⚡ First Steps After Install

### Quick Start (No API Key Required)

```bash
blnd chat --offline
```

**What happens:**
- Interactive menu appears
- Choose from 5 local models
- First download takes 5-10 minutes (~3.8GB)
- Then works 100% offline forever

---

### Using Online Models (Best Quality)

```bash
# 1. Get free API key from https://openrouter.ai
# 2. Set the key
blnd set-key --provider openrouter

# 3. Start chatting
blnd chat
```

---

## 📚 Where to Find Help

### For New Users - Start Here:
1. **GETTING_STARTED.md** - Quick start guide
2. **INSTALL.md** - Complete installation instructions
3. **LOCAL_MODELS_QUICKSTART.md** - Offline setup in 5 minutes

### For All Users:
4. **USER_GUIDE.md** - Full feature documentation
5. **LOCAL_MODELS_GUIDE.md** - Complete offline guide
6. **INTERACTIVE_MODEL_SELECTION.md** - Model selector details

### For Developers:
7. **CONTRIBUTING.md** - How to contribute
8. **README.md** - Project overview

---

## 💻 Basic Commands

```bash
# Interactive chat
blnd chat                    # Online
blnd chat --offline          # Offline

# Generate code
blnd gen "your idea"         # Online
blnd gen "your idea" --offline --save file.py

# Fix bugs
blnd fix myfile.py
blnd fix ./src --preview

# Create files
blnd create "description" filename.py
blnd create "API server" server.py --with-tests

# Generate documentation
blnd doc mycode.py
blnd doc ./project --export DOCS.md
```

---

## 🎯 What Makes BlondE Special

### Works Offline (100% Private)
- No API keys needed with `--offline`
- Models run on your computer
- No data sent externally
- Free unlimited usage

### Works Online (Best Quality)
- Free tier available (OpenRouter)
- Latest AI models
- Faster responses
- Multiple providers

### Smart Features
- **Memory System** - Remembers conversations and patterns
- **Agentic Mode** - AI can use tools with your permission
- **Interactive Selection** - Beautiful menu to choose models
- **Multiple Commands** - Chat, generate, fix, create, document

---

## 🛠️ System Requirements

- **Python:** 3.10 or higher
- **OS:** Linux, macOS, Windows (WSL recommended)
- **RAM:** 8GB minimum (16GB+ for local models)
- **Storage:** 5GB+ free space
- **Internet:** Required for initial setup (optional after that)

---

## ❓ Common Questions

### Q: Do I need an API key?
**A:** No! Use `--offline` flag to run local models without any API keys.

### Q: Is it free?
**A:** Yes! 100% free and open source. Online mode uses your API key (free tier available).

### Q: Does it work offline?
**A:** Yes! After downloading a model, works completely offline.

### Q: Is my code private?
**A:** With `--offline`, 100% private. Online mode sends to AI provider.

### Q: How big is the download?
**A:** ~3.8GB for local model (first time only). Cached for future use.

### Q: Which model should I use?
**A:** CodeLlama-7B recommended for coding (default offline model).

---

## 🎓 Learning Path

### Day 1: Get Started
```bash
# Install
git clone https://github.com/cerekinorg/BlondE-cli.git
cd BlondE-cli && python3 -m venv venv && source venv/bin/activate && pip install -e .

# First chat
blnd chat --offline
```

### Day 2: Explore Features
```bash
# Generate code
blnd gen "quicksort in Python" --save sort.py

# Fix a file
blnd fix myfile.py --suggest

# Create documentation
blnd doc myproject/ --export DOCS.md
```

### Day 3: Advanced
```bash
# With memory
blnd chat --offline --memory

# With tools
blnd chat --agentic

# Iterative creation
blnd create "REST API" api.py --iterative --with-tests
```

---

## 🐛 Troubleshooting

### `blnd: command not found`
```bash
source venv/bin/activate
```

### `No module named 'typer'`
```bash
pip install -r requirements.txt
pip install -e .
```

### Model download fails
```bash
# Check internet
ping huggingface.co

# Check disk space
df -h ~
```

### More Help
- Check `INSTALL.md` for detailed troubleshooting
- Open issue: https://github.com/cerekinorg/BlondE-cli/issues

---

## 🤝 Contributing

Want to contribute?

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

See `CONTRIBUTING.md` for detailed guidelines.

---

## 📞 Get Support

- **Issues:** https://github.com/cerekinorg/BlondE-cli/issues
- **Discussions:** https://github.com/cerekinorg/BlondE-cli/discussions
- **Documentation:** All files in this repository

---

## 🌟 Share BlondE

If you find BlondE useful:
- ⭐ Star the repository
- 🐦 Share on social media
- 📝 Write a blog post
- 🎥 Create a video tutorial
- 🤝 Contribute improvements

---

## ✅ Quick Reference

```
┌──────────────────────────────────────────────────┐
│         BlondE-CLI Quick Reference               │
├──────────────────────────────────────────────────┤
│ Install:  git clone + pip install -e .           │
│ GitHub:   github.com/cerekinorg/BlondE-cli       │
│ Chat:     blnd chat --offline                    │
│ Generate: blnd gen "prompt" --save file.py       │
│ Fix:      blnd fix myfile.py                     │
│ Create:   blnd create "desc" file.py             │
│ Doc:      blnd doc project/                      │
│ Help:     blnd --help                            │
│ Offline:  Add --offline to any command           │
└──────────────────────────────────────────────────┘
```

---

**🎉 Welcome to BlondE-CLI!**

Start with: `blnd chat --offline`
