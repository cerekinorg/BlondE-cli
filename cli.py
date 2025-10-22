


import difflib
import os
import time
import requests
import typer
import yaml
import json
import re
import ast
import logging
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.layout import Layout
from rich.text import Text
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress
from rich.status import Status
from difflib import unified_diff
from tenacity import retry, stop_after_attempt, wait_fixed
from dotenv import load_dotenv
import magic
from git import Repo

console = Console()
app = typer.Typer()
load_dotenv()
logging.basicConfig(filename=str(Path.home() / ".blonde/debug.log"), level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("blonde")

# =====================
#  Constants
# =====================
ASCII_LOGO = r"""
 ██████╗ ██╗      ██████╗ ███╗   ██╗██████╗ ███████╗
 ██╔══██╗██║     ██╔═══██╗████╗  ██║██╔══██╗██╔════╝
██████╔╝██║     ██║   ██║██╔██╗ ██║██║  ██║█████╗  
██╔══██╗██║     ██║   ██║██║╚██╗██║██║  ██║██╔══╝  
 ██████╔╝███████╗╚██████╔╝██║ ╚████║██████╔╝███████╗
 ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝
"""

HELP_TEXT = """
[bold cyan]Blonde CLI Help[/bold cyan]

[green]Modes:[/green]
 • [bold]blnd chat[/bold] → interactive chat
 • [bold]blnd gen "prompt"[/bold] → generate code
 • [bold]blnd fix file.py[/bold] → fix code with diff preview
 • [bold]blnd doc file.py[/bold] → explain/document code
 • [bold]blnd create "description" file.py[/bold] → create new file

[green]In chat mode:[/green]
 • Type any message to chat with Blonde
 • [bold]exit[/bold] or [bold]quit[/bold] to leave
 • [bold]help[/bold] to see this message again
 • [bold]/save[/bold] → export chat to Markdown
"""


HISTORY_FILE = Path.home() / ".blonde_history_default.json"
EXCLUDED_DIRS = {"__pycache__", ".git", "venv", "node_modules", ".idea", ".mypy_cache"}
INCLUDED_EXTS = {"py", "js", "ts", "java", "c", "cpp", "json", "yml", "yaml", "toml", "md"}
repo_map_cache = {}
CONFIG_FILE = Path.home() / ".blonde" / "config.json"
CONFIG_FILE.parent.mkdir(exist_ok=True)


# =====================
#  Utilities (To Extract to utils.py Later)
# =====================

def save_api_key(key_name: str, key_value: str):
    config = {}
    if CONFIG_FILE.exists():
        config = json.loads(CONFIG_FILE.read_text())
    config[key_name] = key_value
    CONFIG_FILE.write_text(json.dumps(config))
    console.print(f"[green]{key_name} saved locally![/green]")

def load_api_key(key_name: str) -> str:
    if CONFIG_FILE.exists():
        config = json.loads(CONFIG_FILE.read_text())
        return config.get(key_name)
    return ""

@app.command()
def set_key(model: str, key: str):
    """Set API key for a model."""
    key_name = f"{model.upper()}_API_KEY"
    save_api_key(key_name, key)


def detect_language(file_path: str) -> str:
    """Detects programming language from file content or extension.
    Args:
        file_path: Path to the file.
    Returns:
        Language string (e.g., 'python', 'javascript').
    Why it works: Uses file extension and content analysis via python-magic.
    Pitfalls: Non-standard extensions may return 'unknown'; ensure python-magic is installed.
    Learning: Explore tree-sitter for precise language parsing.
    """
    ext_lang_map = {
        "py": "python", "js": "javascript", "ts": "typescript",
        "java": "java", "c": "c", "cpp": "cpp"
    }
    ext = file_path.split(".")[-1].lower()
    if ext in ext_lang_map:
        return ext_lang_map[ext]
    
    try:
        with open(file_path, "rb") as f:
            content = f.read(1024)
        mime = magic.from_buffer(content, mime=True)
        if "python" in mime:
            return "python"
        elif "javascript" in mime or "ecmascript" in mime:
            return "javascript"
        elif "java" in mime:
            return "java"
        elif "c++" in mime or "c" in mime:
            return "cpp" if ext == "cpp" else "c"
        return ext_lang_map.get(ext, "unknown")
    except Exception as e:
        logger.debug(f"Language detection failed for {file_path}: {e}")
        return ext_lang_map.get(ext, "unknown")

def scan_repo(path: str) -> dict:
    """Walk through a repo, extract functions, classes, imports, and call graphs.
    Args:
        path: Directory path to scan.
    Returns:
        Dict mapping file paths to metadata.
    Why it works: Uses AST for Python files, skips irrelevant dirs.
    Pitfalls: Large repos may be slow; non-Python files have limited parsing.
    Learning: Add tree-sitter for multi-language parsing.
    """
    repo_map = {}
    class CallGraphVisitor(ast.NodeVisitor):
        def __init__(self):
            self.calls = []
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                self.calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.calls.append(node.func.attr)
            self.generic_visit(node)

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            ext = file.split(".")[-1]
            if ext not in INCLUDED_EXTS:
                continue
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, path)
            repo_map[relative_path] = {
                "functions": [], "classes": [], "imports": [], "calls": []
            }
            try:
                if ext == "py":
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    tree = ast.parse(content)
                    visitor = CallGraphVisitor()
                    visitor.visit(tree)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            repo_map[relative_path]["functions"].append(node.name)
                        elif isinstance(node, ast.ClassDef):
                            repo_map[relative_path]["classes"].append(node.name)
                        elif isinstance(node, (ast.Import, ast.ImportFrom)):
                            for alias in node.names:
                                repo_map[relative_path]["imports"].append(alias.name)
                    repo_map[relative_path]["calls"] = visitor.calls
                else:
                    repo_map[relative_path]["functions"].append(f"unparsed_{ext}")
            except Exception as e:
                repo_map[relative_path]["error"] = str(e)
                logger.debug(f"Scan error for {file_path}: {e}")
    return repo_map

def render_code_blocks(text: str) -> None:
    """Renders Markdown text with code blocks using syntax highlighting.
    Args:
        text: Markdown text to render.
    Why it works: Splits text into code and non-code segments, uses Syntax for highlighting.
    Pitfalls: Malformed Markdown may cause errors; handle gracefully.
    Learning: Explore Rich’s Live for real-time rendering.
    """
    text = text.strip()
    if "```" not in text:
        console.print(Markdown(text, style="white"))
        return
    segments = text.split("```")
    for i, segment in enumerate(segments):
        if i % 2 == 1:
            try:
                lang, *code_lines = segment.split("\n", 1)
                code = code_lines[0].strip() if code_lines else ""
                if code:
                    console.print(Syntax(code, lang.strip() or "python", theme="monokai", line_numbers=False))
            except Exception as e:
                logger.debug(f"Render code error: {e}")
                console.print(f"[red]Error rendering code: {e}[/red]")
                console.print(segment.strip(), style="white")
        else:
            if segment.strip():
                console.print(Markdown(segment.strip(), style="white"))

def extract_code(text: str) -> str:
    """Extracts code from markdown-style ``` blocks.
    Args:
        text: Input text with potential code blocks.
    Returns:
        Extracted code or original text.
    Why it works: Uses regex to extract code reliably.
    Pitfalls: Malformed Markdown may return partial code.
    Learning: Study re module for advanced pattern matching.
    """
    if "```" in text:
        matches = re.findall(r"```(?:\w+)?\n([\s\S]*?)```", text)
        if matches:
            return matches[0].strip()
    return text.strip()

# =====================
#  Shared Helpers
# =====================
def animate_logo():
    """Displays the Blonde CLI logo and help text.
    Why it works: Uses Rich for styled output.
    Pitfalls: Console size may affect rendering.
    Learning: Explore Rich’s Panel for custom layouts.
    """
    console.clear()
    console.print(Text(ASCII_LOGO, style="bold magenta"), justify="center")
    console.print(Panel(
        Text("Welcome to Blonde CLI 🚀", justify="center", style="bold cyan"),
        border_style="blue", expand=False
    ))
    console.print(HELP_TEXT)
    time.sleep(1)

# def load_adapter(debug: bool = False):
#     """Loads the appropriate model adapter based on config.yml.
#     Args:
#         debug: Enable debug logging.
#     Returns:
#         Model adapter instance.
#     Why it works: Dynamically loads adapters, defaults to OpenRouter.
#     Pitfalls: Missing config.yml causes fallback.
#     Learning: Study dynamic imports with importlib.
#     """
#     try:
#         with open("config.yml") as f:
#             cfg = yaml.safe_load(f)
#         model = cfg.get("default_model", "openrouter")
#     except FileNotFoundError:
#         model = "openrouter"
#         logger.debug("config.yml not found, using openrouter")

#     if model == "openai":
#         from models.openai import OpenAIAdapter
#         return OpenAIAdapter(debug=debug)
#     elif model == "hf":
#         from models.hf import HFAdapter
#         return HFAdapter(debug=debug)
#     else:
#         from models.openrouter import OpenRouterAdapter
#         return OpenRouterAdapter(debug=debug)


# def load_adapter(model_name="openrouter", debug=False):
#     """Load selected model adapter."""
#     if model_name == "openai":
#         from models.openai import OpenAIAdapter
#         return OpenAIAdapter()
#     elif model_name == "hf":
#         from models.hf import HFAdapter
#         return HFAdapter()
#     else:
#         from models.openrouter import OpenRouterAdapter
#         return OpenRouterAdapter(debug=debug)


def load_adapter(model_name="openrouter", offline: bool = False, debug: bool = False, gguf_model: str = None):
    """Load model adapter with optional GGUF model.
    Args:
        model_name: Online model provider (openrouter, openai, hf).
        offline: Force offline mode.
        debug: Enable debug logging.
        gguf_model: Specific GGUF model (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf).
    """
    if offline or gguf_model:
        from models.local import LocalAdapter
        if gguf_model:
            repo, file = gguf_model.split("/", 1) if "/" in gguf_model else (gguf_model, None)
            return LocalAdapter(model_name=repo, model_file=file, debug=debug)
        return LocalAdapter(debug=debug)
    try:
        # Check internet
        import requests
        requests.get("https://www.google.com", timeout=2)
        if model_name == "openai":
            from models.openai import OpenAIAdapter
            return OpenAIAdapter(debug=debug)
        elif model_name == "hf":
            from models.hf import HFAdapter
            return HFAdapter(debug=debug)
        else:
            from models.openrouter import OpenRouterAdapter
            return OpenRouterAdapter(debug=debug)
    except requests.RequestException:
        console.print("[yellow]No internet; falling back to offline.[/yellow]")
        from models.local import LocalAdapter
        return LocalAdapter(debug=debug)


# bot = load_adapter()


def get_response(prompt: str, debug: bool = False) -> str:
    """Fetches response from the active adapter with spinner.
    Args:
        prompt: User input.
        debug: Enable debug.
    Returns:
        Response string.
    Why it works: Spinner shows progress; retries handle transients.
    Pitfalls: Long prompts may timeout; truncate context.
    Learning: Explore Rich Status for custom spinners.
    """
    with Status("Blonde is thinking...", spinner="dots") as status:
        if debug:
            logger.debug(f"Prompt: {prompt[:500]}")
        try:
            response = bot.chat(prompt)
            if isinstance(response, str):
                return response.strip()
            elif isinstance(response, dict):
                content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not content:
                    raise ValueError("Empty content")
                return content.strip()
            else:
                raise ValueError(f"Unexpected type: {type(response)}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_after = e.response.headers.get("Retry-After", 10)
                logger.warning(f"Rate limit, waiting {retry_after}s")
                console.print(f"[yellow]Rate limit hit, waiting {retry_after}s...[/yellow]")
                time.sleep(int(retry_after))
                raise
            raise
        except Exception as e:
            logger.error(f"API Error: {e}")
            console.print(f"[red]API Error: {e}[/red]")
            return "Sorry, there was an error. Try again."

def save_history(history: list) -> None:
    """Saves chat history to JSON file.
    Args:
        history: List of (sender, message) tuples.
    Why it works: Persists chat for session continuity.
    Pitfalls: File permissions may cause errors.
    Learning: Study JSON serialization.
    """
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

def load_history() -> list:
    """Loads chat history from JSON file.
    Returns:
        List of (sender, message) tuples.
    Why it works: Restores previous chats for context.
    Pitfalls: Corrupted JSON may cause errors.
    Learning: Explore pathlib for file handling.
    """
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def stream_response(text: str, delay: float = 0.02) -> str:
    """Streams text like Claude typing.
    Args:
        text: Text to stream.
        delay: Delay between chunks.
    Returns:
        Full text buffer.
    Why it works: Improves UX with typewriter effect.
    Pitfalls: Short texts may look odd; adjust delay.
    Learning: Explore Rich’s Live for dynamic updates.
    """
    buffer = ""
    for chunk in text.split():
        buffer += chunk + " "
        console.print(chunk, end=" ", style="magenta", highlight=False, soft_wrap=True)
        time.sleep(delay)
    console.print("\n")
    return buffer

def suggest_terminal_command(user_input: str) -> str | None:
    """Suggests terminal commands based on user input.
    Args:
        user_input: User’s chat input.
    Returns:
        Suggested command or None.
    Why it works: Adds Warp-like interactivity.
    Pitfalls: Limited command mappings; expand dictionary.
    Learning: Study NLP for intent detection.
    """
    command_map = {
        "list files": "ls",
        "show directory": "pwd",
        "change directory": "cd",
        "remove file": "rm",
        "create directory": "mkdir"
    }
    for key, cmd in command_map.items():
        if key in user_input.lower():
            return f"[yellow]Suggested command: {cmd}[/yellow]"
    return None

# =====================
#  Commands
# =====================

# Add optional model selection to all commands
@app.callback()
def main(
    model: str = typer.Option("openrouter", help="Model to use (openai/hf/openrouter)"),
    debug: bool = typer.Option(False, help="Enable debug logging")
):
    global bot, HISTORY_FILE
    bot = load_adapter(model_name=model, debug=debug)
    model_name_lower = bot.__class__.__name__.replace("Adapter", "").lower()
    HISTORY_FILE = Path.home() / f".blonde_history_{model_name_lower}.json"

@app.command()
def chat(debug: bool = typer.Option(False, help="Enable debug logging"),
         offline: bool = typer.Option(False, help="Use offline GGUF model"),
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)")):
    """Interactive chat with Blonde."""
    global bot
    # bot = load_adapter(debug=debug)
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model)
    animate_logo()
    console.print(Panel(Text("Type your prompt below. Use /help for commands.", justify="left"), border_style="cyan"))

    chat_history = load_history()

    while True:
        user_input = Prompt.ask("[bold green]You[/bold green]")
        
        if user_input.lower() in ("exit", "quit"):
            save_history(chat_history)
            console.print("[bold red]Goodbye![/bold red]")
            break
        if user_input.lower() == "/help":
            console.print(Panel(Text(HELP_TEXT, justify="left"), border_style="cyan"))
            continue
        if user_input.lower() == "/clear":
            chat_history = []
            console.print("[bold yellow]Chat cleared.[/yellow]")
            continue
        if user_input.lower() == "/save":
            out_file = "blonde_chat.md"
            with open(out_file, "w") as f:
                for sender, msg in chat_history:
                    f.write(f"**{sender}:** {msg}\n\n")
            console.print(f"[bold green]💾 Chat exported to {out_file}[/bold green]")
            continue

        suggestion = suggest_terminal_command(user_input)
        if suggestion:
            console.print(suggestion)
            if Prompt.ask("Run it? [y/n]", default="n") == "y":
                os.system(suggestion.replace("[yellow]Suggested command: ", "").strip())
            continue

        chat_history.append(("You", user_input))
        console.print("[magenta]Blonde:[/magenta]")
        try:
            response = get_response(user_input, debug)
            chat_history.append(("Blonde", response))
            # stream_response(response)
            render_code_blocks(response)
        except Exception as e:
            logger.error(f"Chat error: {e}")
            console.print(f"[red]Error: {e}[/red]")
        
        console.rule(style="dim")




@app.command()
def gen(prompt: str, debug: bool = typer.Option(False, help="Enable debug logging"),
    offline: bool = typer.Option(False, help="Use offline GGUF model"),
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)")
    ):
    """Generate code from a prompt.
    Why it works: Renders API-generated code with spinner.
    Pitfalls: Large prompts may hit API limits.
    Learning: Explore prompt engineering.
    """
    global bot
    # bot = load_adapter(debug=debug)
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model)
    console.print(Panel("Blonde CLI - Generating Code", style="bold cyan"))
    response = get_response(prompt, debug)
    render_code_blocks(response)

@app.command()
def create(
    description: str,
    file: str,
    debug: bool = typer.Option(False, help="Enable debug logging"),
    offline: bool = typer.Option(False, help="Use offline GGUF model"),
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)")
):
    """Create a new code file from a description.
    Args:
        description: What the file should do.
        file: Output file path.
    Why it works: Generates code with repo context, previews before saving.
    Pitfalls: Overwriting existing files; added confirmation.
    Learning: Study repo scanning for context-aware generation.
    """
    global bot
    # bot = load_adapter(debug=debug)
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model)
    console.print(Panel("Blonde CLI - Creating File", style="bold cyan"))

    repo_path = os.path.dirname(file) if os.path.dirname(file) else "."
    repo_map = scan_repo(repo_path) if os.path.isdir(repo_path) else {}
    context = str(repo_map)[:2000]
    lang = detect_language(file)
    prompt = f"""
    You are a code generator. Given this description and repo context, output ONLY the source code for a new file.
    Use language: {lang}.
    Repo context: {context}
    Description: {description}
    Output code:
    """
    response = get_response(prompt, debug)
    cleaned = extract_code(response)

    console.print("\n[bold yellow]Preview of generated file:[/bold yellow]")
    console.print(Syntax(cleaned, lang, theme="monokai", line_numbers=True))

    if os.path.exists(file):
        if Prompt.ask(f"[yellow]{file} exists. Overwrite?[/yellow]", choices=["y", "n"], default="n") == "n":
            console.print("[red]Creation discarded.[/red]")
            return
    choice = Prompt.ask("\nSave file?", choices=["y", "n"], default="y")
    if choice == "y":
        with open(file, "w", encoding="utf-8") as f:
            f.write(cleaned)
        console.print(f"[green]File created: {file}[/green]")
    else:
        console.print("[red]Creation discarded.[/red]")



@app.command()
def fix(
    path: str,
    export: str = typer.Option(None, help="Export diff(s) instead of applying"),
    preview: bool = typer.Option(False, help="Preview all diffs before applying"),
    iterative: bool = typer.Option(False, help="Iterative refinement mode"),
    suggest: bool = typer.Option(False, help="Show fix suggestions with explanations"),
    git_commit: bool = typer.Option(False, help="Auto-commit fixes to git"),
    skip_errors: bool = typer.Option(False, help="Skip files with errors and continue"),
    debug: bool = typer.Option(False, help="Enable debug logging"),
    offline: bool = typer.Option(False, help="Use offline GGUF model"),
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)")
):
    """Fix bugs in a file or folder.
    Args:
        path: File or folder to fix.
        export: Export diffs to a file or directory.
        preview: Show all diffs before applying.
        iterative: Enable refinement mode.
        suggest: Show structured suggestions.
        git_commit: Auto-commit to git.
        skip_errors: Skip files with errors.
        debug: Enable debug logging.
    Why it works: Processes files with repo context, handles errors, supports git.
    Pitfalls: Large repos may hit API limits; use --skip-errors.
    Learning: Study unified_diff for diff formatting, GitPython for commits.
    """
    global bot, repo_map_cache
    # bot = load_adapter(debug=debug)
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model)
    console.print(Panel("Blonde CLI - Fixing Codebase", style="bold cyan"))

    diffs = []
    if os.path.isdir(path):
        repo_map_cache[path] = scan_repo(path)
        console.print(f"[cyan]Repo map built with {len(repo_map_cache[path])} files[/cyan]")
        with Progress() as progress:
            task = progress.add_task("[cyan]Scanning files...", total=len(repo_map_cache[path]))
            for relative_path in repo_map_cache[path]:
                file_path = os.path.join(path, relative_path)
                try:
                    diff = _fix_file(file_path, repo_map_cache[path], export, preview, iterative, suggest, debug)
                    if diff:
                        diffs.append(diff)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    if skip_errors:
                        console.print(f"[yellow]Skipped {file_path} due to error: {e}[/yellow]")
                    else:
                        raise
                finally:
                    progress.update(task, advance=1)
    else:
        try:
            diff = _fix_file(path, repo_map_cache.get(os.path.dirname(path)), export, preview, iterative, suggest, debug)
            if diff:
                diffs.append(diff)
        except Exception as e:
            logger.error(f"Error processing {path}: {e}")
            if skip_errors:
                console.print(f"[yellow]Skipped {path} due to error: {e}[/yellow]")
            else:
                raise

    if not diffs:
        console.print("[yellow]No changes proposed.[/yellow]")
        console.print("[yellow]If errors occurred, try --skip-errors or --debug.[/yellow]")
        return

    if preview:
        table = Table(title="Proposed Changes", show_lines=True)
        table.add_column("File", style="cyan")
        table.add_column("Diff", style="white")
        valid_diffs = []
        for diff in diffs:
            try:
                file, (original, cleaned, diff_text, suggestion) = diff
                table.add_row(file, diff_text)
                valid_diffs.append(diff)
            except ValueError as e:
                logger.error(f"Invalid diff format for {diff[0]}: {e}")
                console.print(f"[yellow]Skipping invalid diff for {diff[0]}: {e}[/yellow]")
        if not valid_diffs:
            console.print("[red]No valid changes to preview.[/red]")
            return
        console.print(Panel(table, border_style="yellow"))

        choice = Prompt.ask("\nApply changes?", choices=["y", "n", "save-as"], default="save-as")
        if choice == "n":
            console.print("[red]Changes discarded.[/red]")
            return
        for file, (original, cleaned, diff_text, suggestion) in valid_diffs:
            if os.path.exists(file) and choice == "y":
                if Prompt.ask(f"[yellow]{file} exists. Overwrite?[/yellow]", choices=["y", "n"], default="n") == "n":
                    console.print(f"[yellow]Skipped {file}[/yellow]")
                    continue
            if choice == "y":
                with open(file, "w", encoding="utf-8") as f:
                    f.write(cleaned)
                console.print(f"[green]Changes applied to {file}[/green]")
            elif choice == "save-as":
                ext = file.split(".")[-1]
                save_as = file.replace(f".{ext}", f"_fixed.{ext}")
                with open(save_as, "w", encoding="utf-8") as f:
                    f.write(cleaned)
                console.print(f"[green]Fixed file saved as {save_as}[/green]")

    if git_commit and valid_diffs:
        if is_git_repo(path):
            repo = Repo(path, search_parent_directories=True)
            repo.git.add([file for file, _ in valid_diffs])
            repo.index.commit(f"Blonde CLI fixes: {len(valid_diffs)} files")
            console.print(f"[green]Committed {len(valid_diffs)} changes to git.[/green]")
        else:
            console.print("[yellow]Not a git repo; skipping commit.[/yellow]")

def _fix_file(file: str, repo_map: dict | None, export: str | None, preview: bool, iterative: bool, suggest: bool, debug: bool) -> tuple | None:
    """Internal helper to fix one file with repo context.
    Args:
        file: Path to file.
        repo_map: Repository metadata from scan_repo.
        export: Export diff path.
        preview: Enable batch preview.
        iterative: Enable refinement mode.
        suggest: Show structured suggestions.
        debug: Enable debug logging.
    Returns:
        Tuple (file, (original, cleaned, diff_text, suggestion)) or None.
    Why it works: Always returns consistent tuple, validates code.
    Pitfalls: API failures may return empty code; validate responses.
    Learning: Study difflib for diff customization.
    """
    try:
        with open(file, "r", encoding="utf-8") as f:
            original = f.read()
    except Exception as e:
        logger.error(f"Error reading {file}: {e}")
        console.print(f"[red]Error reading {file}: {e}[/red]")
        return None

    lang = detect_language(file)
    context = str(repo_map)[:2000] if repo_map else ""

    suggestion = ""
    if suggest:
        prompt = f"""
        You are a code fixer. Analyze this file and repo context, then provide a table in Markdown with:
        - Issue: What's wrong (e.g., "Potential division by zero")
        - Fix: Proposed change (e.g., "Add error handling")
        - Impact: Why it matters (e.g., "Prevents runtime errors")
        Repo context: {context}
        File ({file}, language: {lang}):
        {original}
        """
        suggestion = get_response(prompt, debug)
        console.print(Panel(Markdown(suggestion), title="Suggested Fixes", border_style="yellow"))

    prompt = f"""
    You are a professional code fixer.
    Repository map (for context): {context}
    Given the following file, output ONLY the corrected source code.
    Use language: {lang}.
    Do not include explanations, notes, or markdown fences.
    Preserve formatting.
    File ({file}):
    {original}
    """
    cleaned = extract_code(get_response(prompt, debug))

    # Validate cleaned code
    if "error processing your request" in cleaned.lower():
        console.print(f"[red]Failed to fix {file}: Invalid response from API[/red]")
        return None

    if lang == "python":
        try:
            ast.parse(cleaned)
        except SyntaxError as e:
            logger.error(f"Invalid Python code for {file}: {e}")
            console.print(f"[red]Invalid fixed code for {file}: {e}[/red]")
            return None

    if iterative:
        max_iters = 3
        for i in range(max_iters):
            console.print(Panel(f"Iteration {i+1}/{max_iters}", style="yellow"))
            console.print(Syntax(cleaned, lang, theme="monokai", line_numbers=True))
            console.print("[yellow]Refine this? Enter feedback or 'done' to stop.[/yellow]")
            feedback = Prompt.ask("[green]Feedback[/green]")
            if feedback.lower() == "done":
                break
            prompt = f"""
            Refine this code based on feedback: {feedback}
            Original file: {original}
            Current version: {cleaned}
            Output ONLY the refined source code (language: {lang}).
            """
            cleaned = extract_code(get_response(prompt, debug))
            if "error processing your request" in cleaned.lower():
                console.print(f"[red]Failed to refine {file}: Invalid response from API[/red]")
                return None
            if lang == "python":
                try:
                    ast.parse(cleaned)
                except SyntaxError as e:
                    logger.error(f"Invalid refined Python code for {file}: {e}")
                    console.print(f"[red]Invalid refined code for {file}: {e}[/red]")
                    return None

    diff = unified_diff(
        original.splitlines(),
        cleaned.splitlines(),
        fromfile=f"{file} (original)",
        tofile=f"{file} (fixed)",
        lineterm="",
    )
    diff_text = "\n".join(diff)
    if not diff_text.strip():
        console.print(f"[yellow]No changes needed for {file}[/yellow]")
        return None

    if not preview and not export:
        console.print(diff_text, style="yellow")
        console.print("\n[bold yellow]Preview of fixed file:[/bold yellow]")
        console.print(Syntax(cleaned, lang, theme="monokai", line_numbers=True))
        choice = Prompt.ask("\nApply changes?", choices=["y", "n", "save-as"], default="save-as")
        if choice == "y":
            if os.path.exists(file):
                if Prompt.ask(f"[yellow]{file} exists. Overwrite?[/yellow]", choices=["y", "n"], default="n") == "n":
                    console.print(f"[yellow]Skipped {file}[/yellow]")
                    return None
            with open(file, "w", encoding="utf-8") as f:
                f.write(cleaned)
            console.print(f"[green]Changes applied to {file}[/green]")
        elif choice == "save-as":
            ext = file.split(".")[-1]
            save_as = file.replace(f".{ext}", f"_fixed.{ext}")
            with open(save_as, "w", encoding="utf-8") as f:
                f.write(cleaned)
            console.print(f"[green]Fixed file saved as {save_as}[/green]")
        else:
            console.print("[red]Changes discarded[/red]")
        return (file, (original, cleaned, diff_text, suggestion))

    if export:
        export_path = export if os.path.isdir(export) else export
        if os.path.isdir(export):
            diff_file = os.path.join(export, os.path.basename(file) + ".diff")
            with open(diff_file, "w", encoding="utf-8") as f:
                f.write(diff_text)
            console.print(f"[green]Diff exported → {diff_file}[/green]")
        else:
            with open(export, "a", encoding="utf-8") as f:
                f.write(f"# {file}\n{diff_text}\n\n")
            console.print(f"[green]Diff appended → {export}[/green]")
        return (file, (original, cleaned, diff_text, suggestion))

    return (file, (original, cleaned, diff_text, suggestion))


@app.command()
def doc(
    path: str,
    export: str = typer.Option(None, help="Export explanation to a file"),
    format: str = typer.Option("md", help="Output format: md, txt"),
    debug: bool = typer.Option(False, help="Enable debug logging"),
    offline: bool = typer.Option(False, help="Use offline GGUF model"),
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)")
):
    """Explain code in a file or folder in plain English.
    Args:
        path: File or folder to document.
        export: Export documentation to a file.
        format: Output format (md or txt).
        debug: Enable debug logging.
    Why it works: Generates clear documentation with repo context.
    Pitfalls: Large repos may overwhelm API.
    Learning: Study Markdown for structured documentation.
    """
    global bot
    # bot = load_adapter(debug=debug)
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model)
    console.print(Panel("Blonde CLI - Documenting Codebase", style="bold cyan"))

    if os.path.isdir(path):
        repo_map = scan_repo(path)
        with Progress() as progress:
            task = progress.add_task("[cyan]Scanning files...", total=len(repo_map))
            context = ["Repository structure:"]
            for rel_path, info in repo_map.items():
                context.append(f"- {rel_path}: {info.get('functions', [])}, {info.get('classes', [])}, {info.get('imports', [])}")
                try:
                    with open(os.path.join(path, rel_path), "r", encoding="utf-8") as f:
                        context.append(f"\n### {rel_path}\n```\n{f.read()}\n```")
                except Exception as e:
                    context.append(f"Error reading {rel_path}: {e}")
                    logger.debug(f"Doc error for {rel_path}: {e}")
                progress.update(task, advance=1)

        prompt = f"""
        You are a code documentation expert. Given the repository structure and file contents below, provide a concise Markdown summary of the codebase. For each file, list:
        - Purpose
        - Key functions/classes
        - Dependencies (imports)
        - One-line summary
        Group by module/folder if applicable. Output only the Markdown summary.
        {chr(10).join(context)}
        """
        response = get_response(prompt, debug)
    else:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        prompt = f"Explain this code in plain English, in Markdown format:\n{code}"
        response = get_response(prompt, debug)

    if format == "txt":
        response = re.sub(r"[`*#\[\]]", "", response)
    
    render_code_blocks(response)

    if export:
        with open(export, "w", encoding="utf-8") as f:
            f.write(response)
        console.print(f"[green]Documentation exported to {export}[/green]")


def is_git_repo(path: str) -> bool:
    """Checks if path is a git repo.
    Args:
        path: Directory path.
    Returns:
        True if .git exists.
    Why it works: Uses GitPython for reliable detection.
    Pitfalls: Shallow clones may not have .git; fallback to os.path.
    Learning: Read GitPython docs for repo ops.
    """
    try:
        Repo(path, search_parent_directories=True)
        return True
    except:
        return os.path.exists(os.path.join(path, ".git"))

# ... (detect_language, scan_repo, render_code_blocks, extract_code - same as before)

# Shared Helpers (same, with suggest_terminal_command expanded)
def suggest_terminal_command(user_input: str) -> str | None:
    """Suggests terminal commands based on user input.
    Args:
        user_input: User's chat input.
    Returns:
        Suggested command or None.
    Why it works: Matches keywords to commands, like Warp's AI suggestions.
    Pitfalls: False positives; use NLP for advanced matching.
    Learning: Study intent detection in NLP.
    """
    command_map = {
        "list files": "ls -la",
        "show directory": "pwd",
        "change directory": "cd",
        "remove file": "rm -rf",
        "create directory": "mkdir -p",
        "git status": "git status",
        "git commit": "git commit -m",
        "explain ls": "ls --help"
    }
    for key, cmd in command_map.items():
        if key in user_input.lower():
            return f"[yellow]Suggested command: {cmd}[/yellow]"
    return None


if __name__ == "__main__":
    app()




