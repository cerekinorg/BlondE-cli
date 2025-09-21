# Blonde CLI – A Quick‑Start Guide

Below is a plain‑English walkthrough of the **Blonde CLI** Python script.  
It’s a command‑line tool that lets you chat with an AI, generate code, fix bugs, and document codebases—all from the terminal.

> **TL;DR**  
> *Run `blnd chat` to talk to the AI.*  
> *Run `blnd gen "prompt"` to generate code.*  
> *Run `blnd fix path/to/file.py` (or a folder) to auto‑fix bugs.*  
> *Run `blnd doc path/to/file.py` (or a folder) to get a Markdown explanation.*

---

## 1. Imports & Global Objects

```python
import difflib, os, time, json, yaml, re
import typer, json, yaml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.prompt import Prompt
from rich.layout import Layout
from rich.text import Text
from rich.syntax import Syntax
from difflib import unified_diff
from tenacity import retry, stop_after_attempt, wait_fixed
```

* **`typer`** – Builds the CLI interface.  
* **`rich`** – Adds pretty printing, panels, syntax highlighting, etc.  
* **`difflib`** – Generates unified diffs for file changes.  
* **`tenacity`** – Retries failed API calls.  
* **`yaml` / `json`** – Reads config and stores chat history.  
* **`Path`** – Handles file paths in a cross‑platform way.

```python
console = Console()
app = typer.Typer()
```

* `console` is the Rich console used for all output.  
* `app` is the Typer application that will hold all commands.

---

## 2. ASCII Logo & Help Text

```python
ASCII_LOGO = r""" ... """
HELP_TEXT = """ ... """
```

* `ASCII_LOGO` is a stylised “Blonde” banner.  
* `HELP_TEXT` explains the available commands and in‑chat shortcuts.

---

## 3. History File

```python
HISTORY_FILE = Path.home() / ".blonde_history.json"
```

* Stores the chat history between sessions.

---

## 4. Adapter Loader

The CLI can talk to different LLM back‑ends (OpenAI, HuggingFace, OpenRouter).  
The adapter is chosen based on `config.yml`.

```python
def load_adapter(debug: bool = False):
    try:
        with open("config.yml") as f:
            cfg = yaml.safe_load(f)
        model = cfg.get("default_model", "openrouter")
    except FileNotFoundError:
        model = "openrouter"

    if model == "openai":
        from models.openai import OpenAIAdapter
        return OpenAIAdapter(debug=debug)
    elif model == "hf":
        from models.hf import HFAdapter
        return HFAdapter(debug=debug)
    else:
        from models.openrouter import OpenRouterAdapter
        return OpenRouterAdapter(debug=debug)
```

* The adapter exposes a `chat(prompt)` method that returns the model’s response.

```python
bot = load_adapter()
```

* `bot` is the global instance used by all commands.

---

## 5. Shared Helper Functions

| Function | What it does |
|----------|--------------|
| `animate_logo()` | Clears the screen, prints the ASCII logo, a welcome panel, and the help text. |
| `get_response(prompt, debug=False)` | Calls `bot.chat(prompt)` with retry logic. Normalises the response to a plain string. |
| `show_diff(original, modified, filename)` | Uses `difflib.unified_diff` to print a coloured diff. |
| `save_history(history)` / `load_history()` | Persist chat history to `~/.blonde_history.json`. |
| `render_code_blocks(text)` | Parses Markdown code fences (` ```lang ... ``` `) and prints them with syntax highlighting. |
| `extract_code(text)` | Pulls out the first code block from a Markdown string; if none, returns the raw text. |
| `stream_response(text, delay=0.02)` | Prints words one by one to mimic a typing effect. |

---

## 6. Chat Mode (`blnd chat`)

```python
@app.command()
def chat():
    ...
```

1. **Show logo & welcome panel** (`animate_logo()`).
2. **Load previous chat history** (`load_history()`).
3. **Loop**:
   * Prompt the user (`Prompt.ask`).
   * Handle commands:
     * `/help` – show help text again.
     * `/clear` – wipe the chat history.
     * `/save` – export the conversation to `blonde_chat.md`.
     * `exit` / `quit` – exit the loop (history is saved).
   * Append the user message to `chat_history`.
   * Call `get_response()` to get the AI reply.
   * Append the reply to `chat_history`.
   * Render the reply with `render_code_blocks()` (so any code fences are highlighted).
   * Print a rule (`console.rule`) to separate turns.

---

## 7. Generate Mode (`blnd gen "prompt"`)

```python
@app.command()
def gen(prompt: str):
    response = get_response(prompt)
    console.print(render_code_blocks(response))
```

* Sends the prompt to the model and prints the result, automatically highlighting any code fences.

---

## 8. Repository Scanning

```python
def scan_repo(path: str) -> dict:
    ...
```

* Walks the directory tree, skipping common ignored folders (`__pycache__`, `.git`, `venv`, etc.).
* For each file with a supported extension (`py`, `js`, `ts`, `java`, `c`, `cpp`, `json`, `yml`, `yaml`, `toml`, `md`):
  * If it’s a Python file, parses the AST to collect:
    * Function names
    * Class names
    * Import statements
  * For non‑Python files, just notes that the file exists.
* Returns a dictionary mapping relative file paths to a small metadata object.

---

## 9. Fix Mode (`blnd fix path/to/file_or_folder`)

```python
@app.command()
def fix(path: str, export: str = typer.Option(None, help="Export diff(s) instead of applying")):
    ...
```

### Workflow

1. **Determine if `path` is a file or directory**.
2. **If a directory**:
   * Build a repo map with `scan_repo`.
   * Iterate over each file and call `_fix_file`.
3. **If a single file**:
   * Call `_fix_file` directly.

### `_fix_file` (internal helper)

1. **Read the original file**.
2. **Build a short context string** from the repo map (truncated to 2000 chars for safety).
3. **Ask the model** to return *only* the corrected source code.  
   * Prompt instructs the model not to include explanations or Markdown fences.
4. **Extract the code** with `extract_code`.
5. **Generate a unified diff** between the original and cleaned code.
6. **Print the diff** in yellow.
7. **Export mode** (`export` flag set):
   * If `export` is a directory → one `.diff` file per original file.
   * If `export` is a file → append all diffs to that file.
8. **Interactive preview** (default):
   * Show the cleaned code with syntax highlighting.
   * Ask the user whether to:
     * Apply changes (`y`)
     * Save as a new file (`save-as`)
     * Discard (`n`)

---

## 10. Document Mode (`blnd doc path/to/file_or_folder`)

```python
@app.command()
def doc(path: str, export: str = typer.Option(None, help="Export explanation to a file"),
        format: str = typer.Option("md", help="Output format: md, txt"),
        debug: bool = typer.Option(False, help="Enable debug logging")):
    ...
```

### Workflow

1. **Reload the adapter** with the `debug` flag if set.
2. **If a directory**:
   * Build a repo map (`scan_repo`).
   * Use a `Progress` bar to show scanning progress.
   * Build a context string that lists:
     * File paths
     * Functions, classes, imports
     * The raw file contents wrapped in Markdown code fences.
   * Send a prompt to the model asking it to produce a concise Markdown summary of the entire codebase.
3. **If a single file**:
   * Read the file and ask the model to explain it in plain English (Markdown).
4. **Post‑process**:
   * If `format` is `txt`, strip Markdown syntax.
   * Render the response with `render_code_blocks` (so any code fences are highlighted).
5. **Export**:
   * If `export` is provided, write the raw response to that file.

---

## 11. Entry Point

```python
if __name__ == "__main__":
    app()
```

* When the script is executed directly, Typer starts the CLI and registers all commands.

---

## 12. How to Use

```bash
# 1. Start a chat session
blnd chat

# 2. Generate code from a prompt
blnd gen "Create a Python function that returns the Fibonacci sequence up to n"

# 3. Fix a single file
blnd fix src/main.py

# 4. Fix all files in a folder
blnd fix src/

# 5. Export diffs instead of applying changes
blnd fix src/ --export diffs/

# 6. Document a single file
blnd doc src/main.py

# 7. Document an entire repository
blnd doc src/ --export docs.md
```

---

## 13. Things to Keep in Mind

| Topic | Note |
|-------|------|
| **API Keys** | The adapter modules (`models/*.py`) will need your OpenAI / HuggingFace / OpenRouter credentials. |
| **Rate Limits** | `tenacity` retries up to 3 times with a 2‑second wait. |
| **Large Files** | The context sent to the model is truncated to 2000 characters to avoid exceeding token limits. |
| **Diff Export** | When exporting diffs, the script creates a `.diff` file per original file or appends to a single file. |
| **Markdown Rendering** | `render_code_blocks` only highlights the first code block per message; subsequent blocks are printed as plain Markdown. |
| **History** | Chat history is stored in `~/.blonde_history.json`. Use `/save` to export a Markdown copy. |

---

## 14. Summary

The **Blonde CLI** is a lightweight, extensible tool that:

* **Chats** with an LLM in an interactive terminal.  
* **Generates** code snippets from natural‑language prompts.  
* **Fixes** bugs in single files or entire codebases, showing diffs and allowing interactive approval.  
* **Documents** codebases in Markdown, optionally exporting the output.

All of this is powered by **Rich** for beautiful terminal output, **Typer** for command parsing, and a pluggable **adapter** system that lets you switch between OpenAI, HuggingFace, or OpenRouter back‑ends with a simple `config.yml`. Happy coding!