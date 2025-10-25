# BlondE-CLI Complete User Guide

Your comprehensive guide to using BlondE-CLI's enhanced features including memory, agentic mode, and iterative refinement.

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Memory System](#memory-system)
4. [Agentic Mode](#agentic-mode)
5. [All Commands](#all-commands)
6. [Advanced Features](#advanced-features)
7. [Tips & Tricks](#tips--tricks)
8. [Troubleshooting](#troubleshooting)

---

## Installation

### Option 1: Via pip (Recommended)

```bash
pip install blonde-cli
```

### Option 2: Via Docker

```bash
docker pull cerekin/blonde-cli
docker run -it cerekin/blonde-cli chat
```

### Option 3: From Source

```bash
git clone https://github.com/cerekin/blonde-cli
cd blonde-cli
pip install -e .
```

### Verify Installation

```bash
blnd --help
```

---

## Getting Started

### First-Time Setup

1. **Set API Key** (if using cloud models)

```bash
blnd set-key openrouter YOUR_API_KEY
```

2. **Start Interactive Chat**

```bash
blnd chat
```

3. **Enable Memory** (remembers conversations)

```bash
blnd chat --memory
```

4. **Enable Agentic Mode** (AI can use tools)

```bash
blnd chat --agentic --memory
```

### Quick Examples

```bash
# Generate code
blnd gen "Create a REST API with FastAPI" --save api.py

# Fix a file with iterative refinement
blnd fix myfile.py --iterative --memory

# Create a new file with tests
blnd create "User authentication module" auth.py --with-tests

# Document code
blnd doc myproject/ --style tutorial --export docs.md
```

---

## Memory System

The memory system allows BlondE to remember past conversations and code patterns.

### How It Works

- **Short-term memory**: Current session context
- **Long-term memory**: Semantic search across all past interactions
- **Context injection**: Relevant past information added to prompts

### Using Memory

#### In Chat Mode

```bash
# Enable memory (default)
blnd chat --memory

# Disable memory
blnd chat --no-memory

# View memory stats
/memory

# Show conversation context
/context

# Clear current session
/clear
```

#### In Other Commands

```bash
# Gen with memory
blnd gen "Create a FastAPI endpoint" --memory --save endpoint.py

# Fix with learned patterns
blnd fix buggy.py --memory --iterative

# Doc with consistent style
blnd doc myfile.py --memory --style detailed
```

### Memory Commands in Chat

```
You: How do I write a Python decorator?
Blonde: [Explains decorators]

You: /memory
[Shows: 1 conversations, 0 tasks, Memory DB active]

You: Can you show me another decorator example?
Blonde: [Uses previous context to provide related example]
```

### Benefits

✅ **Consistent coding style** - Learns your preferences  
✅ **Faster responses** - Reuses patterns from similar tasks  
✅ **Context awareness** - Understands project history  
✅ **Progressive learning** - Gets better over time

---

## Agentic Mode

Agentic mode allows BlondE to autonomously use tools to accomplish tasks.

### Available Tools

- File operations (read, write, list)
- Code execution (safe, sandboxed)
- Git operations
- Web search (when configured)
- Custom tools (extensible)

### Using Agentic Mode

#### In Chat

```bash
blnd chat --agentic --memory
```

Example interaction:

```
You: Create a new FastAPI project with proper structure

Blonde: I'll help you set up a FastAPI project. Let me create the necessary files:

[Tool: create_file - main.py]
[Tool: create_file - requirements.txt]
[Tool: create_directory - app/]
[Tool: create_file - app/__init__.py]
[Tool: create_file - app/routes.py]

✅ Project structure created! Run: pip install -r requirements.txt
```

#### In Create Command

```bash
blnd create "A user authentication system" auth.py --agentic
```

BlondE will:
1. Create the main file
2. Suggest related files (tests, config, docs)
3. Optionally create suggested files with your approval

### Safety Features

- ✅ User confirmation required for file operations
- ✅ Sandboxed code execution
- ✅ Whitelisted commands only
- ✅ All actions logged

### Tool Commands in Chat

```
/tools          # List available tools
/tools enable   # Enable agentic mode
/tools disable  # Disable agentic mode
```

---

## All Commands

### 1. Chat Command

Interactive conversation with memory and agentic capabilities.

```bash
blnd chat [OPTIONS]
```

**Options:**

```
--memory/--no-memory     Enable context memory (default: on)
--agentic/--no-agentic   Enable tool usage (default: off)
--stream/--no-stream     Stream responses (default: on)
--offline                Use local GGUF model
--model TEXT             Specific model to use
--debug                  Enable debug logging
```

**In-Chat Commands:**

```
/help         Show help
/memory       Show memory stats
/context      Show conversation context
/tools        List available tools
/save         Export chat to markdown
/clear        Clear chat history
exit/quit     Exit chat
```

**Examples:**

```bash
# Basic chat
blnd chat

# Full-featured chat
blnd chat --memory --agentic --stream

# Offline chat with local model
blnd chat --offline --model "codellama-7b.gguf"
```

### 2. Gen Command

Generate code from natural language description.

```bash
blnd gen PROMPT [OPTIONS]
```

**Options:**

```
--memory/--no-memory   Enable context memory
--save TEXT            Save to file
--lang TEXT            Target language (python, javascript, etc)
--offline              Use offline model
--debug                Enable debug logging
```

**Examples:**

```bash
# Basic generation
blnd gen "Create a binary search function"

# Save to file with memory
blnd gen "REST API with authentication" --save api.py --memory

# Specific language
blnd gen "Sort an array" --lang javascript --save sort.js
```

### 3. Fix Command

Fix bugs in code files with iterative refinement.

```bash
blnd fix PATH [OPTIONS]
```

**Options:**

```
--memory/--no-memory     Use learned fix patterns
--iterative/--no-iterative  Enable iterative refinement
--suggest                Show fix suggestions
--preview                Preview all diffs before applying
--export TEXT            Export diffs to file
--git-commit             Auto-commit fixes
--skip-errors            Continue on errors
```

**Examples:**

```bash
# Basic fix
blnd fix myfile.py

# Iterative refinement with memory
blnd fix buggy.py --iterative --memory

# Fix entire project
blnd fix myproject/ --preview --memory

# Show suggestions first
blnd fix myfile.py --suggest

# Export diffs without applying
blnd fix myproject/ --export fixes.diff
```

### 4. Create Command

Create new code files from descriptions.

```bash
blnd create DESCRIPTION FILE [OPTIONS]
```

**Options:**

```
--memory/--no-memory       Learn from past creations
--agentic/--no-agentic     Suggest related files
--iterative/--no-iterative Refine before saving
--with-tests               Generate unit tests
```

**Examples:**

```bash
# Basic file creation
blnd create "A user model class" models/user.py

# With tests and memory
blnd create "Authentication service" auth.py --with-tests --memory

# Agentic mode (suggests related files)
blnd create "REST API" api.py --agentic --memory

# Iterative refinement
blnd create "Data validator" validator.py --iterative
```

### 5. Doc Command

Generate documentation for code.

```bash
blnd doc PATH [OPTIONS]
```

**Options:**

```
--memory/--no-memory   Consistent documentation style
--style TEXT           Style: concise, detailed, tutorial
--export TEXT          Export to file
--format TEXT          Format: md, txt
```

**Examples:**

```bash
# Document a file
blnd doc myfile.py

# Document entire project
blnd doc myproject/ --style detailed --export docs.md

# Tutorial-style documentation
blnd doc complex_module.py --style tutorial --memory

# Concise documentation
blnd doc utils.py --style concise
```

---

## Advanced Features

### Iterative Refinement

Refine code through multiple iterations before finalizing.

```bash
blnd fix myfile.py --iterative --memory
```

**Workflow:**

1. Initial fix proposed
2. Review the fix
3. Provide feedback
4. Refined fix generated
5. Repeat up to 3 times
6. Apply final version

**Example Session:**

```
Iteration 1/3:
[Shows fixed code]

Feedback: Add type hints and docstrings
done

Iteration 2/3:
[Shows improved code with types and docs]

Feedback: done

Apply changes? (y/n/save-as): y
✅ Changes applied!
```

### Context-Aware Generation

BlondE learns from your codebase and past interactions.

```bash
# First time - creates basic function
blnd gen "Create a user validator" --save validator.py --memory

# Later - remembers your style
blnd gen "Create a product validator" --save product_validator.py --memory
# Result: Uses similar patterns, naming conventions, and style
```

### Repo-Aware Operations

BlondE scans your repository for context.

```bash
# Fix considers entire codebase structure
blnd fix api/routes.py --memory

# Create knows existing patterns
blnd create "New API endpoint" api/users.py --memory --agentic
```

### Streaming Output

See responses as they're generated.

```bash
blnd chat --stream  # Default
blnd chat --no-stream  # Wait for complete response
```

---

## Tips & Tricks

### 1. Maximize Memory Usage

```bash
# Always enable memory for consistent results
alias blnd="blnd --memory"

# Review what BlondE learned
blnd chat --memory
> /memory
> /context
```

### 2. Agentic Workflow

```bash
# Let BlondE handle complete tasks
blnd chat --agentic --memory
> "Set up a new FastAPI project with authentication, testing, and Docker support"
```

### 3. Iterative Development

```bash
# Refine until perfect
blnd create "Complex algorithm" algo.py --iterative --memory --with-tests
```

### 4. Documentation Automation

```bash
# Generate consistent docs for entire project
for file in $(find . -name "*.py"); do
    blnd doc "$file" --memory --style detailed --export "docs/$(basename $file).md"
done
```

### 5. Batch Operations

```bash
# Fix all Python files
find . -name "*.py" -exec blnd fix {} --memory --preview \;
```

### 6. Offline Mode

```bash
# Use local models for privacy
blnd chat --offline --model "codellama-7b.gguf" --memory
```

### 7. Debug Mode

```bash
# See what's happening under the hood
blnd chat --debug --memory
```

---

## Troubleshooting

### Memory System Not Working

**Problem**: Memory features don't work

**Solution**:
```bash
# Install ChromaDB
pip install chromadb

# Verify installation
python -c "import chromadb; print('OK')"

# Clear corrupted memory
rm -rf ~/.blonde/memory_db
```

### API Rate Limits

**Problem**: Too many API requests

**Solution**:
```bash
# Use offline mode
blnd chat --offline

# Or add delays between requests (automatic retry built-in)
```

### Large Repository Performance

**Problem**: Slow on large repos

**Solution**:
```bash
# Fix specific files instead of entire repo
blnd fix src/main.py --memory

# Use --skip-errors for large batches
blnd fix src/ --skip-errors --memory
```

### Docker Issues

**Problem**: Docker container can't access files

**Solution**:
```bash
# Mount your project directory
docker run -it -v $(pwd):/workspace cerekin/blonde-cli chat

# Mount memory directory for persistence
docker run -it \
    -v $(pwd):/workspace \
    -v ~/.blonde:/home/blonde/.blonde \
    cerekin/blonde-cli chat --memory
```

### No Output/Hangs

**Problem**: Command seems stuck

**Solution**:
```bash
# Enable debug mode
blnd chat --debug

# Check API key
blnd set-key openrouter YOUR_KEY

# Verify network connection
curl https://openrouter.ai
```

---

## Configuration Files

### API Keys

Located at `~/.blonde/config.json`:

```json
{
  "OPENROUTER_API_KEY": "your-key",
  "OPENAI_API_KEY": "your-key"
}
```

### Memory Database

Located at `~/.blonde/memory_db/`

### Logs

Located at `~/.blonde/debug.log`

### Tool Call History

Located at `~/.blonde/tool_logs/`

---

## Best Practices

1. **Always use --memory** for consistent results
2. **Enable --agentic** for complex tasks
3. **Use --iterative** for critical code
4. **Generate --with-tests** for production code
5. **Export diffs** before applying bulk fixes
6. **Review suggestions** in --suggest mode
7. **Keep memory clean** - use /clear when switching contexts
8. **Back up** your ~/.blonde directory periodically

---

## Getting Help

- **In-app help**: `blnd COMMAND --help`
- **Documentation**: This file
- **Issues**: [GitHub Issues](https://github.com/cerekin/blonde-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/cerekin/blonde-cli/discussions)

---

**Happy Coding with BlondE-CLI! 🚀**
