# 🤖 BlondE-CLI

**AI-Powered Code Assistant with Memory and Agentic Capabilities**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/cerekinorg/BlondE-cli.svg)](https://github.com/cerekinorg/BlondE-cli/stargazers)

> Chat with AI, generate code, fix bugs, and document your codebase—all from the terminal. Works online or 100% offline with local models.

---

## ✨ Features

- 🗣️ **Interactive Chat** - Conversation with memory and context awareness
- 🔧 **Code Generation** - Generate code from natural language descriptions
- 🐛 **Bug Fixing** - AI-powered code fixes with memory of past patterns
- 📝 **Documentation** - Auto-generate docs in multiple styles
- 🧠 **Memory System** - Remembers past conversations and learns your patterns
- 🤖 **Agentic Mode** - AI can use tools (files, git, commands) with your permission
- 🏠 **Local Models** - Run 100% offline with GGUF models (no API keys!)
- 🎨 **Interactive Model Selection** - Beautiful menu to choose models

---

## 🚀 Quick Install

```bash
# Clone and install
git clone https://github.com/cerekinorg/BlondE-cli.git
cd BlondE-cli
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

**That's it!** The `blnd` command is now available.

**📖 Full Installation Guide:** [INSTALL.md](INSTALL.md)

---

## 🎯 Quick Start

### Option 1: Offline Mode (No API Key Required)

```bash
# Start chatting with local model
blnd chat --offline
```

First run shows an interactive menu to download a model (~3.8GB).

### Option 2: Online Mode (Best Quality)

```bash
# Set API key (get free key at https://openrouter.ai)
blnd set-key --provider openrouter

# Start chatting
blnd chat
```

---

## 📚 Usage Examples

### Interactive Chat
```bash
# With online model
blnd chat

# With local model (offline)
blnd chat --offline

# With memory enabled
blnd chat --memory

# With agentic capabilities (AI can use tools)
blnd chat --agentic
```

### Generate Code
```bash
# Generate code
blnd gen "create a REST API with FastAPI"

# Save to file
blnd gen "quicksort algorithm" --save quicksort.py

# Use offline model
blnd gen "binary search tree" --offline
```

### Fix Bugs
```bash
# Fix a single file
blnd fix buggy_code.py

# Fix entire directory with preview
blnd fix ./src --preview

# Iterative refinement
blnd fix myfile.py --iterative --suggest
```

### Create Files
```bash
# Create new file
blnd create "user authentication module" auth.py

# With tests
blnd create "calculator class" calc.py --with-tests

# With iterative refinement
blnd create "API server" server.py --iterative
```

### Generate Documentation
```bash
# Document a file
blnd doc mycode.py

# Document entire project
blnd doc ./src --export DOCS.md

# Tutorial style
blnd doc module.py --style tutorial
```

---

## 🎨 Interactive Model Selection

When using `--offline`, BlondE shows a beautiful interactive menu:

```
╔═══════════════════════════════════════╗
║   🤖 BlondE-CLI Local Model Selector  ║
╚═══════════════════════════════════════╝

📦 Cached Local Models
┏━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ #  ┃ Model File        ┃   Size ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ 1  │ codellama...gguf  │ 3.8GB  │
└────┴───────────────────┴────────┘

Choose: [use/download/cancel]
```

**5 Models Available:**
- CodeLlama-7B ⭐ (Best for coding)
- Mistral-7B (Fast general-purpose)
- DeepSeek-Coder (Advanced coding)
- Llama-2-Chat (Conversational)
- Phi-2 (Smaller/faster)

---

## 💡 Why BlondE?

### Online Mode (Cloud AI)
✅ Best quality responses  
✅ Latest AI models  
✅ Fast inference  
✅ Free tier available (OpenRouter)

### Offline Mode (Local AI)
✅ 100% Private - No data sent externally  
✅ Works without internet  
✅ No API costs  
✅ Unlimited usage  
✅ Full control over models

### Memory & Agentic Features
✅ Learns from past conversations  
✅ Remembers code patterns  
✅ Context-aware suggestions  
✅ Can use tools safely (with permission)  
✅ Maintains conversation history

---

## 📖 Documentation

- **[INSTALL.md](INSTALL.md)** - Complete installation guide
- **[USER_GUIDE.md](USER_GUIDE.md)** - Full feature documentation
- **[LOCAL_MODELS_GUIDE.md](LOCAL_MODELS_GUIDE.md)** - Offline model setup
- **[LOCAL_MODELS_QUICKSTART.md](LOCAL_MODELS_QUICKSTART.md)** - Quick reference
- **[INTERACTIVE_MODEL_SELECTION.md](INTERACTIVE_MODEL_SELECTION.md)** - Model selector guide

---

## 🛠️ Requirements

- **Python:** 3.10+
- **OS:** Linux, macOS, Windows (WSL recommended)
- **RAM:** 8GB minimum (16GB+ for local models)
- **Storage:** 5GB+ free space

---

## 🔑 API Keys

### Get Free API Keys

- **OpenRouter** (Recommended): https://openrouter.ai/
  - Free tier available
  - Access to multiple models
  
- **OpenAI**: https://platform.openai.com/api-keys
  - Paid service
  - Best quality

- **HuggingFace**: https://huggingface.co/settings/tokens
  - Free inference API
  - Many models available

### Set API Key
```bash
blnd set-key --provider openrouter
# Or for OpenAI
blnd set-key --provider openai
```

**No API key?** Use offline mode with `--offline` flag!

---

## 🎯 Use Cases

### For Developers
- Generate boilerplate code
- Fix bugs with AI suggestions
- Document codebases automatically
- Create unit tests
- Learn new patterns

### For Students
- Learn programming concepts
- Get code explanations
- Debug assignments
- Practice coding offline

### For Teams
- Maintain consistent code style
- Generate documentation
- Share memory/context
- Collaborative debugging

---

## 🚀 Advanced Features

### Memory System
```bash
# Enable memory (learns from conversations)
blnd chat --memory

# Check memory stats
# In chat, type: /memory
```

### Agentic Mode
```bash
# AI can use tools with permission
blnd chat --agentic

# In chat, AI can:
# - Read/write files
# - Run git commands
# - Execute safe shell commands
# - Search codebase
```

### Iterative Refinement
```bash
# Refine code before saving
blnd create "API server" api.py --iterative

# Fix with multiple iterations
blnd fix buggy.py --iterative
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Start for Contributors
```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/BlondE-cli.git
cd BlondE-cli

# Setup dev environment
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/

# Make changes and submit PR!
```

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal UI
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) - Local model inference
- [OpenRouter](https://openrouter.ai/) - Multi-model API

---

## 📞 Support

- **Issues:** https://github.com/cerekinorg/BlondE-cli/issues
- **Discussions:** https://github.com/cerekinorg/BlondE-cli/discussions
- **Documentation:** See docs in this repository

---

## 🗺️ Roadmap

- [x] Interactive chat
- [x] Code generation
- [x] Bug fixing
- [x] Documentation generation
- [x] Memory system
- [x] Agentic capabilities
- [x] Local model support
- [x] Interactive model selection
- [ ] Web UI
- [ ] Plugin system
- [ ] Team collaboration features
- [ ] Fine-tuning support

---

## ⭐ Star History

If you find BlondE useful, please star the repository!

[![Star History Chart](https://api.star-history.com/svg?repos=cerekinorg/BlondE-cli&type=Date)](https://star-history.com/#cerekinorg/BlondE-cli&Date)

---

**Made with ❤️ by the Cerekin Team**

**Start now:** `blnd chat --offline`
