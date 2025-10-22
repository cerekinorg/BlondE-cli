# BlondE-CLI Quick Start Guide

Get started with BlondE-CLI in 5 minutes or less!

---

## 🚀 Installation

### Linux/macOS (Recommended)

```bash
# Clone repository
git clone https://github.com/cerekin/blonde-cli.git
cd blonde-cli

# Run automated installer
bash install.sh

# Activate virtual environment
source venv/bin/activate
```

### Windows

```powershell
# Clone repository
git clone https://github.com/cerekin/blonde-cli.git
cd blonde-cli

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install BlondE-CLI
pip install -e .
```

### With GPU Support

```bash
# NVIDIA GPU (CUDA)
bash install.sh --gpu=nvidia

# Mac M1/M2 (Metal)
bash install.sh --gpu=metal
```

---

## 🔑 Setup API Keys

### Option 1: Using CLI (Recommended)
```bash
blnd set-key openrouter YOUR_API_KEY_HERE
```

### Option 2: Environment Variables
```bash
# Copy example config
cp .env.example .env

# Edit .env and add your keys
nano .env
```

### Get Free API Keys
- **OpenRouter** (Recommended): https://openrouter.ai/keys
  - Free tier: GPT-OSS models
- **OpenAI**: https://platform.openai.com/api-keys
- **HuggingFace**: https://huggingface.co/settings/tokens

---

## 💬 Basic Usage

### 1. Interactive Chat
```bash
blnd chat
```

**In-chat commands:**
- `/help` - Show help
- `/save` - Export chat to Markdown
- `/clear` - Clear history
- `exit` or `quit` - Exit

### 2. Code Generation
```bash
blnd gen "Create a Python function to calculate Fibonacci sequence"
```

### 3. Code Documentation
```bash
# Document a file
blnd doc myfile.py

# Document entire project
blnd doc . --export docs.md
```

### 4. Bug Fixing
```bash
# Fix a single file
blnd fix myfile.py

# Fix entire directory
blnd fix src/

# Export diffs instead of applying
blnd fix src/ --export fixes/
```

### 5. Create New Files
```bash
blnd create "A REST API endpoint for user authentication" api/auth.py
```

---

## 🏠 Offline Mode (Local Models)

### Download and Use Local Models

```bash
# First run downloads model automatically
blnd chat --offline --model "TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf"
```

**Recommended Local Models:**
- **CodeLlama-7B-Q4** (~4GB) - Best for code tasks
- **Mistral-7B-Instruct-Q4** (~4GB) - General purpose
- **Phi-2-Q4** (~1.5GB) - Fast, lightweight

Models are cached in `~/.blonde/models/`

---

## 🧠 Memory System (NEW!)

### Enable Persistent Memory
```bash
blnd chat --memory
```

**What it remembers:**
- Previous conversations (semantic search)
- Active goals and tasks
- Project context variables

### Manage Memory
```bash
# View session state
python memory.py show

# Clear session (keeps history)
python memory.py clear

# Clear everything
python memory.py clear-all

# Export memory
python memory.py export backup.json
```

---

## 🛠️ Advanced Features

### 1. Iterative Code Refinement
```bash
blnd fix myfile.py --iterative
```
*Allows you to provide feedback and refine fixes in multiple iterations*

### 2. Code Suggestions with Explanations
```bash
blnd fix myfile.py --suggest
```
*Shows a table of issues, fixes, and impact before applying*

### 3. Git Integration
```bash
blnd fix src/ --git-commit
```
*Automatically commits fixes to git after approval*

### 4. Batch Preview
```bash
blnd fix src/ --preview
```
*Preview all changes in a table before applying*

### 5. Switch Models On-the-Fly
```bash
# Use OpenAI
blnd chat --model openai

# Use HuggingFace
blnd chat --model hf
```

---

## 📊 Example Workflows

### Workflow 1: Document a New Codebase
```bash
# Clone project
git clone https://github.com/someone/project.git
cd project

# Generate documentation
blnd doc . --export PROJECT_DOCS.md

# Chat about the codebase
blnd chat
> "Explain the authentication flow in this project"
```

### Workflow 2: Fix Bugs in Batch
```bash
# Scan and fix all Python files
blnd fix . --preview --export fixes.diff

# Review the diff, then apply
blnd fix .
```

### Workflow 3: Build a Feature with AI Pair Programming
```bash
# Start chat with memory enabled
blnd chat --memory

# In chat:
> "I want to build a user authentication system with JWT tokens"
> "Create a login endpoint"
> "Add password hashing with bcrypt"
```

### Workflow 4: Offline Development
```bash
# Download model once
blnd chat --offline --model "TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf"

# Now works without internet
blnd gen "Write a function to parse CSV files" --offline
```

---

## 🐛 Troubleshooting

### Issue: `llama-cpp-python` build fails

**Solution:**
```bash
# Use pre-built wheels
pip install llama-cpp-python --prefer-binary

# Or skip local models
pip install -r requirements.txt --no-deps
pip install <all packages except llama-cpp-python>
```

### Issue: `python-magic` not working on Windows

**Solution:**
```bash
pip uninstall python-magic
pip install python-magic-bin
```

### Issue: API rate limits

**Solution:**
- Use local models with `--offline`
- Switch to a different API provider
- Upgrade to paid API tier

### Issue: Out of memory with local models

**Solution:**
- Use smaller quantized models (Q4 instead of Q8)
- Reduce context window (default is 2048 tokens)
- Close other applications

---

## 📚 Additional Resources

- **Full Documentation**: [COMPREHENSIVE_ANALYSIS.md](COMPREHENSIVE_ANALYSIS.md)
- **API Reference**: [README.md](README.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md) *(coming soon)*
- **GitHub Issues**: https://github.com/cerekin/blonde-cli/issues

---

## 💡 Pro Tips

1. **Use memory for long sessions**: `blnd chat --memory` maintains context across conversations
2. **Alias for convenience**: Add `alias blonde='blnd chat --memory'` to your `.bashrc`
3. **Combine with git**: `blnd fix . --git-commit` for automatic version control
4. **Export diffs for review**: Use `--export` to review changes before applying
5. **Local models for privacy**: Use `--offline` for sensitive code

---

## 🎯 What's Next?

- [ ] Try all 5 basic commands (`chat`, `gen`, `fix`, `doc`, `create`)
- [ ] Enable memory system for context-aware AI
- [ ] Download a local model for offline use
- [ ] Document your first project with BlondE
- [ ] Join our Discord community *(link coming soon)*

---

**Happy coding with BlondE-CLI! 🚀**

*Having issues? Open an issue on GitHub or check the comprehensive analysis for advanced troubleshooting.*
