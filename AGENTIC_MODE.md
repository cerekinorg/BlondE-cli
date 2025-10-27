# 🤖 BlondE Enhanced Agentic Mode

## Overview

BlondE now has a **fully autonomous agentic system** that can:
- ✅ Break down complex tasks into steps
- ✅ Execute multiple operations autonomously  
- ✅ Edit files and code
- ✅ Manage git operations
- ✅ Run commands safely
- ✅ Complete multi-step workflows without constant prompting

**Similar to Windsurf/Claude Agentic Mode** but integrated into your CLI!

---

## 🚀 Quick Start

### Basic Usage

```bash
# Start chat with enhanced agentic mode (ON by default)
blnd chat --offline

# Or with specific options
blnd chat --offline --agentic --memory
```

### Autonomous Task Execution

Use the `/agent` command to execute complex tasks autonomously:

```
/agent Fix all Python import errors in this project
/agent Create a REST API endpoint for user authentication
/agent Refactor the cli.py file to use classes instead of functions
/agent Add docstrings to all functions in models/local.py
```

---

## 📋 Available Tools

### File Operations
- **`read_file`** - Read file contents
- **`write_file`** - Create new files
- **`edit_file`** - Edit existing files (find and replace)
- **`delete_file`** - Delete files
- **`rename_file`** - Rename/move files

### Code Operations
- **`replace_in_file`** - Replace text with pattern matching
- **`insert_at_line`** - Insert code at specific line
- **`remove_lines`** - Remove line ranges

### Directory Operations
- **`list_dir`** - List directory contents
- **`create_dir`** - Create directories
- **`search_files`** - Find files by pattern
- **`search_in_files`** - Search text within files

### Git Operations
- **`git_status`** - Check repository status
- **`git_diff`** - View changes
- **`git_add`** - Stage files
- **`git_commit`** - Commit changes

### Analysis
- **`count_lines`** - Count lines of code
- **`run_command`** - Execute shell commands

---

## 💡 Usage Examples

### Example 1: Code Refactoring

```
/agent Refactor the stream_response function in cli.py to be more modular
```

**What happens:**
1. 🔍 AI plans the refactoring steps
2. 📖 Reads the current file
3. ✏️ Creates the refactored code
4. 💾 Edits the file with changes
5. ✅ Shows diff for confirmation

---

### Example 2: Feature Implementation

```
/agent Add error handling to all file operations in agentic_tools.py
```

**What happens:**
1. 📋 Plans: Read file → Identify functions → Add try-catch → Test
2. 🔧 Executes each step autonomously
3. 📝 Shows progress for each step
4. ✅ Completes with summary

---

### Example 3: Bug Fixing

```
/agent Find and fix the bug where cached models fail to load
```

**What happens:**
1. 🔍 Searches codebase for related code
2. 📖 Reads relevant files
3. 🐛 Identifies the issue
4. ✏️ Applies the fix
5. 🧪 Suggests tests

---

### Example 4: Documentation

```
/agent Add comprehensive docstrings to all functions in tools.py
```

**What happens:**
1. 📖 Reads the file
2. 🔍 Identifies functions without docstrings
3. ✍️ Generates appropriate docstrings
4. ✏️ Edits file with additions
5. ✅ Shows before/after

---

## 🎮 Interactive Commands

### `/tools` - List All Tools
```
/tools
```
Shows all available tools organized by category.

### `/plan` - View Current Plan
```
/plan
```
Displays the current execution plan with progress.

### `/agent <task>` - Autonomous Execution
```
/agent Your complex task here
```
Executes the task autonomously with planning and confirmation.

### `/memory` - Memory Stats
```
/memory
```
Shows conversation memory statistics (if enabled).

### `/help` - Show All Commands
```
/help
```
Complete list of available commands.

---

## 🔧 Advanced Usage

### Multi-Step Workflows

The agentic system can handle complex multi-step tasks:

```
/agent Create a new module called 'validators.py' with email and phone validation, add tests, and update the main README
```

**Execution Flow:**
1. **Plan** - Breaks into 4 steps:
   - Create validators.py
   - Implement email validator
   - Implement phone validator
   - Add tests
   - Update README

2. **Execute** - Runs each step with confirmation

3. **Verify** - Shows results and asks for approval

---

### Code Analysis and Refactoring

```
/agent Analyze cli.py and suggest improvements for better modularity
```

The AI will:
1. Read and analyze the code
2. Identify areas for improvement
3. Suggest specific refactorings
4. Optionally apply them with your approval

---

### Git Workflow

```
/agent Review all changed files, add them to git, and create a descriptive commit message
```

Handles the complete git workflow:
1. Runs `git_status`
2. Reviews each changed file
3. Stages appropriate files
4. Generates commit message
5. Commits (with confirmation)

---

## ⚙️ Configuration

### Confirmation Settings

By default, destructive operations require confirmation:
- File edits
- File deletion
- Git commits
- Command execution

### Auto-Confirm Mode (Advanced)

For trusted operations, you can modify the confirmation in code:

```python
# In cli.py, change:
agentic_executor = AgenticExecutor(bot, enhanced_tools, task_planner)

# To:
agentic_executor = AgenticExecutor(bot, enhanced_tools, task_planner)
agentic_executor.tools.require_confirmation = False  # Use with caution!
```

---

## 🛡️ Safety Features

### Confirmation Prompts
All destructive operations ask for confirmation before execution.

### Diff Display
File edits show a unified diff before applying changes.

### Operation Logging
All tool calls are displayed in real-time with parameters.

### Error Handling
If a step fails, the system stops and reports the error.

### Rollback Capability
Use git to revert any unwanted changes.

---

## 🎯 Best Practices

### 1. Be Specific
✅ Good: "Add error handling to the read_file function in tools.py"
❌ Bad: "Make it better"

### 2. One Task at a Time
Break very large tasks into manageable pieces:
```
/agent First, refactor the auth module
# Wait for completion, then:
/agent Now add tests for the auth module
```

### 3. Review Changes
Always review diffs before confirming changes.

### 4. Use Memory
Enable memory (`--memory`) to maintain context across sessions:
```bash
blnd chat --offline --agentic --memory
```

### 5. Check the Plan
Use `/plan` to see what the AI intends to do before execution.

---

## 📊 Comparison with Other Tools

| Feature | BlondE Agentic | Windsurf | Claude |
|---------|---------------|----------|--------|
| Task Decomposition | ✅ | ✅ | ✅ |
| File Editing | ✅ | ✅ | ✅ |
| Code Refactoring | ✅ | ✅ | ✅ |
| Git Integration | ✅ | ✅ | ❌ |
| Offline Mode | ✅ | ❌ | ❌ |
| CLI Interface | ✅ | ❌ | ❌ |
| Memory Persistence | ✅ | ✅ | ✅ |
| Cost | Free (local) | Paid | Paid |

---

## 🐛 Troubleshooting

### "Agentic mode disabled"
**Cause:** `agentic_tools.py` not found or import error
**Fix:** 
```bash
pip install -e . --force-reinstall --no-deps
```

### Tool execution fails
**Cause:** Permission issues or file not found
**Fix:** Check file paths and permissions

### Planning takes too long
**Cause:** Complex task with many steps
**Fix:** Break into smaller sub-tasks

### Changes not visible
**Cause:** File not saved properly
**Fix:** Check file permissions and disk space

---

## 🔮 Future Enhancements

Coming soon:
- 🔄 **Undo/Redo** - Rollback specific operations
- 🧪 **Test Generation** - Auto-generate unit tests
- 📊 **Code Metrics** - Analyze code quality
- 🔍 **Smart Search** - Semantic code search
- 🎨 **UI Mode** - Web interface for agentic tasks
- 🌐 **Multi-file Refactoring** - Refactor across multiple files
- 🤝 **Collaboration** - Share agentic workflows

---

## 📖 More Examples

### Create a Feature End-to-End
```
/agent Create a user authentication system with login, logout, and session management
```

### Fix All TODOs
```
/agent Find all TODO comments in the codebase and create GitHub issues for them
```

### Documentation Generation
```
/agent Generate API documentation for all public functions in the project
```

### Code Migration
```
/agent Migrate all print statements to use the Rich console
```

### Dependency Management
```
/agent Analyze requirements.txt and update outdated packages to latest compatible versions
```

---

## 🎓 Learning Path

1. **Start Simple** - Use `/tools` to see what's available
2. **Try Examples** - Run the examples above
3. **Check Plans** - Use `/plan` to understand the AI's approach
4. **Build Complex** - Combine multiple operations
5. **Customize** - Extend `agentic_tools.py` with your own tools

---

## 💪 Power User Tips

### Chaining Commands
```bash
# In one session:
/agent Add logging to all API endpoints
/plan
# Review the plan
/agent Continue with the plan
```

### Combine with Memory
With memory enabled, the AI remembers previous work:
```
/agent Refactor the database module
# Later in the same session:
/agent Add the same refactoring pattern to the API module
```

### Custom Workflows
Create your own task patterns:
```
/agent [Read → Analyze → Refactor → Test] for module.py
```

---

## 🙋 FAQ

**Q: Is it safe to use agentic mode?**
A: Yes! All destructive operations require confirmation, and you can use git to revert changes.

**Q: Can it work with any programming language?**
A: Yes! The tools are language-agnostic. The AI's understanding depends on the model you use.

**Q: Does it require internet?**
A: No! Works completely offline with local models.

**Q: Can I add custom tools?**
A: Yes! Edit `agentic_tools.py` and add your functions to `EnhancedToolRegistry`.

**Q: How is this different from GitHub Copilot?**
A: Copilot suggests code as you type. BlondE autonomously executes complete multi-step tasks.

---

## 🚀 Get Started Now!

```bash
# Install/update
pip install -e . --force-reinstall --no-deps

# Start agentic mode
blnd chat --offline --agentic

# Try your first autonomous task
/agent List all Python files and count their total lines
```

**Welcome to autonomous coding!** 🤖✨
