


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
from utils import save_api_key, load_api_key

# Import memory and tools for context-aware and agentic capabilities
try:
    from memory import MemoryManager
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    logger = logging.getLogger("blonde")
    logger.debug("Memory system not available. Install dependencies: pip install chromadb")

try:
    from tools import ToolRegistry
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    logger = logging.getLogger("blonde")
    logger.debug("Tools system not available.")

try:
    from model_selector import select_model
    MODEL_SELECTOR_AVAILABLE = True
except ImportError:
    MODEL_SELECTOR_AVAILABLE = False

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
#  Utilities
# =====================

@app.command()
def set_key(model: str, key: str):
    """Set API key for a model."""
    key_name = f"{model.upper()}_API_KEY"
    save_api_key(key_name, key)
    console.print(f"[green]{key_name} saved locally![/green]")


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
def chat(
    debug: bool = typer.Option(False, help="Enable debug logging"),
    offline: bool = typer.Option(False, help="Use offline GGUF model"),
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)"),
    memory: bool = typer.Option(True, help="Enable context memory (remembers past conversations)"),
    agentic: bool = typer.Option(False, help="Enable agentic mode (AI can use tools)"),
    stream: bool = typer.Option(True, help="Stream responses for better UX")
):
    """Interactive chat with Blonde - now with memory and agentic capabilities!"""
    global bot
    
    # Interactive model selection for offline mode
    if offline and not model and MODEL_SELECTOR_AVAILABLE:
        selection = select_model()
        if selection is None:
            console.print("[yellow]Cancelled. Exiting.[/yellow]")
            return
        
        repo, file, is_cached, path = selection
        if is_cached and path:
            # Use the cached model directly
            model = f"{repo}/{file}"
        else:
            # Will download
            model = f"{repo}/{file}"
    
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model)
    
    # Initialize memory manager if enabled
    memory_manager = None
    if memory and MEMORY_AVAILABLE:
        try:
            memory_manager = MemoryManager(user_id="default", enable_vector_store=True)
            console.print("[dim]✓ Memory enabled - I'll remember our conversation![/dim]")
        except Exception as e:
            logger.warning(f"Failed to initialize memory: {e}")
            console.print("[yellow]⚠ Memory disabled - install chromadb to enable[/yellow]")
    
    # Initialize tool registry if agentic mode enabled
    tool_registry = None
    if agentic and TOOLS_AVAILABLE:
        try:
            tool_registry = ToolRegistry(require_confirmation=True, log_calls=True)
            console.print("[dim]✓ Agentic mode enabled - I can help with tasks![/dim]")
        except Exception as e:
            logger.warning(f"Failed to initialize tools: {e}")
            console.print("[yellow]⚠ Agentic mode disabled[/yellow]")
    
    animate_logo()
    
    # Enhanced welcome message
    welcome_parts = ["Type your prompt below. Use /help for commands."]
    if memory_manager:
        welcome_parts.append("💭 Memory: ON")
    if tool_registry:
        welcome_parts.append("🔧 Agentic: ON")
    if stream:
        welcome_parts.append("⚡ Streaming: ON")
    
    console.print(Panel(Text(" | ".join(welcome_parts), justify="center"), border_style="cyan"))

    chat_history = load_history()

    while True:
        user_input = Prompt.ask("[bold green]You[/bold green]")
        
        # Handle exit commands
        if user_input.lower() in ("exit", "quit"):
            save_history(chat_history)
            if memory_manager:
                console.print("[dim]💾 Saving memories...[/dim]")
            console.print("[bold red]Goodbye! 👋[/bold red]")
            break
            
        # Handle /help command
        if user_input.lower() == "/help":
            enhanced_help = HELP_TEXT + "\n[green]Enhanced Commands:[/green]\n"
            enhanced_help += " • [bold]/memory[/bold] → show memory stats\n"
            enhanced_help += " • [bold]/tools[/bold] → list available tools\n"
            enhanced_help += " • [bold]/context[/bold] → show conversation context\n"
            console.print(Panel(Text(enhanced_help, justify="left"), border_style="cyan"))
            continue
            
        # Handle /clear command
        if user_input.lower() == "/clear":
            chat_history = []
            if memory_manager:
                memory_manager.clear_session()
            console.print("[bold yellow]💨 Chat and memory cleared.[/yellow]")
            continue
            
        # Handle /save command
        if user_input.lower() == "/save":
            out_file = "blonde_chat.md"
            with open(out_file, "w") as f:
                for sender, msg in chat_history:
                    f.write(f"**{sender}:** {msg}\n\n")
            console.print(f"[bold green]💾 Chat exported to {out_file}[/bold green]")
            continue
        
        # NEW: Handle /memory command
        if user_input.lower() == "/memory" and memory_manager:
            memory_manager.show_session_state()
            continue
            
        # NEW: Handle /tools command
        if user_input.lower() == "/tools" and tool_registry:
            tools_list = tool_registry.list_tools()
            console.print(Panel(f"[cyan]Available tools: {', '.join(tools_list)}[/cyan]", 
                              border_style="cyan"))
            continue
            
        # NEW: Handle /context command
        if user_input.lower() == "/context" and memory_manager:
            context = memory_manager.get_context_for_prompt(user_input, max_context_length=500)
            console.print(Panel(f"[dim]{context}[/dim]", title="Current Context", border_style="cyan"))
            continue

        # Terminal command suggestions
        suggestion = suggest_terminal_command(user_input)
        if suggestion and not agentic:
            console.print(suggestion)
            if Prompt.ask("Run it? [y/n]", default="n") == "y":
                os.system(suggestion.replace("[yellow]Suggested command: ", "").strip())
            continue

        # Add to chat history
        chat_history.append(("You", user_input))
        
        # Build context-aware prompt
        prompt = user_input
        if memory_manager:
            # Retrieve relevant context from long-term memory
            context = memory_manager.get_context_for_prompt(user_input, max_context_length=2000)
            if context:
                prompt = f"Context from previous conversations:\n{context}\n\nCurrent query: {user_input}"
        
        console.print("[magenta]Blonde:[/magenta]")
        try:
            # Get response with streaming if enabled
            if stream:
                response = get_response(prompt, debug)
                stream_response(response)
            else:
                response = get_response(prompt, debug)
                render_code_blocks(response)
            
            chat_history.append(("Blonde", response))
            
            # Store in memory if enabled
            if memory_manager:
                memory_manager.add_conversation(user_input, response)
                
        except Exception as e:
            logger.error(f"Chat error: {e}")
            console.print(f"[red]Error: {e}[/red]")
        
        console.rule(style="dim")




@app.command()
def gen(
    prompt: str, 
    debug: bool = typer.Option(False, help="Enable debug logging"),
    offline: bool = typer.Option(False, help="Use offline GGUF model"),
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)"),
    memory: bool = typer.Option(True, help="Enable context memory for better generation"),
    save: str = typer.Option(None, help="Save generated code to file"),
    lang: str = typer.Option(None, help="Target language (python, javascript, etc)")
):
    """Generate code from a prompt with context awareness.
    
    Enhanced with memory to remember past code patterns and preferences.
    """
    global bot
    
    # Interactive model selection for offline mode
    if offline and not model and MODEL_SELECTOR_AVAILABLE:
        selection = select_model()
        if selection is None:
            console.print("[yellow]Cancelled. Exiting.[/yellow]")
            return
        repo, file, is_cached, path = selection
        model = f"{repo}/{file}"
    
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model)
    
    # Initialize memory if enabled
    memory_manager = None
    if memory and MEMORY_AVAILABLE:
        try:
            memory_manager = MemoryManager(user_id="default", enable_vector_store=True)
        except Exception as e:
            logger.warning(f"Memory disabled: {e}")
    
    console.print(Panel("Blonde CLI - Context-Aware Code Generation", style="bold cyan"))
    
    # Build context-aware prompt
    enhanced_prompt = prompt
    if memory_manager:
        context = memory_manager.get_context_for_prompt(prompt, max_context_length=1500)
        if context:
            enhanced_prompt = f"Previous code context:\n{context}\n\nNew request: {prompt}"
            console.print("[dim]✓ Using relevant context from memory[/dim]")
    
    if lang:
        enhanced_prompt = f"Generate code in {lang}:\n{enhanced_prompt}"
    
    response = get_response(enhanced_prompt, debug)
    render_code_blocks(response)
    
    # Store in memory for future reference
    if memory_manager:
        memory_manager.add_conversation(f"Code generation: {prompt}", response)
    
    # Save to file if requested
    if save:
        code = extract_code(response)
        with open(save, "w", encoding="utf-8") as f:
            f.write(code)
        console.print(f"[green]✓ Code saved to {save}[/green]")

@app.command()
def create(
    description: str,
    file: str,
    debug: bool = typer.Option(False, help="Enable debug logging"),
    offline: bool = typer.Option(False, help="Use offline GGUF model"),
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)"),
    memory: bool = typer.Option(True, help="Enable context memory"),
    agentic: bool = typer.Option(False, help="Enable agentic mode (auto-create related files)"),
    iterative: bool = typer.Option(False, help="Enable iterative refinement"),
    with_tests: bool = typer.Option(False, help="Generate unit tests alongside code")
):
    """Create a new code file with context awareness and agentic capabilities.
    
    Enhanced features:
    - Memory: Learns from past file creations
    - Agentic: Can suggest and create related files
    - Iterative: Refine the code before saving
    - Tests: Auto-generate unit tests
    """
    global bot
    
    # Interactive model selection for offline mode
    if offline and not model and MODEL_SELECTOR_AVAILABLE:
        selection = select_model()
        if selection is None:
            console.print("[yellow]Cancelled. Exiting.[/yellow]")
            return
        repo, file_model, is_cached, path = selection
        model = f"{repo}/{file_model}"
    
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model)
    
    # Initialize memory and tools
    memory_manager = None
    tool_registry = None
    
    if memory and MEMORY_AVAILABLE:
        try:
            memory_manager = MemoryManager(user_id="default", enable_vector_store=True)
            console.print("[dim]✓ Memory enabled[/dim]")
        except Exception as e:
            logger.warning(f"Memory disabled: {e}")
    
    if agentic and TOOLS_AVAILABLE:
        try:
            tool_registry = ToolRegistry(require_confirmation=True, log_calls=True)
            console.print("[dim]✓ Agentic mode enabled[/dim]")
        except Exception as e:
            logger.warning(f"Agentic mode disabled: {e}")
    
    console.print(Panel("Blonde CLI - Intelligent File Creation", style="bold cyan"))

    repo_path = os.path.dirname(file) if os.path.dirname(file) else "."
    repo_map = scan_repo(repo_path) if os.path.isdir(repo_path) else {}
    context = str(repo_map)[:2000]
    lang = detect_language(file)
    
    # Build enhanced prompt with memory context
    enhanced_description = description
    if memory_manager:
        mem_context = memory_manager.get_context_for_prompt(description, max_context_length=1000)
        if mem_context:
            enhanced_description = f"Context from similar past files:\n{mem_context}\n\nNew file description: {description}"
            console.print("[dim]✓ Using relevant context from memory[/dim]")
    
    prompt = f"""
    You are a code generator. Given this description and repo context, output ONLY the source code for a new file.
    Use language: {lang}.
    Repo context: {context}
    Description: {enhanced_description}
    Output code:
    """
    response = get_response(prompt, debug)
    cleaned = extract_code(response)
    
    # Iterative refinement
    if iterative:
        max_iters = 3
        for i in range(max_iters):
            console.print(Panel(f"Refinement Iteration {i+1}/{max_iters}", style="yellow"))
            console.print(Syntax(cleaned, lang, theme="monokai", line_numbers=True))
            feedback = Prompt.ask("[green]Feedback (or 'done')[/green]", default="done")
            if feedback.lower() == "done":
                break
            refine_prompt = f"""
            Refine this code based on feedback: {feedback}
            Current code: {cleaned}
            Output ONLY the refined source code (language: {lang}).
            """
            cleaned = extract_code(get_response(refine_prompt, debug))

    console.print("\n[bold yellow]Preview of generated file:[/bold yellow]")
    console.print(Syntax(cleaned, lang, theme="monokai", line_numbers=True))

    # Agentic suggestions for related files
    if agentic and tool_registry:
        suggestion_prompt = f"""
        Given this new file and its purpose, what related files should be created?
        File: {file}
        Description: {description}
        
        Suggest 1-3 related files (e.g., tests, config, documentation).
        Format: filename: purpose
        """
        suggestions = get_response(suggestion_prompt, debug)
        console.print(Panel(f"[cyan]Suggested related files:\n{suggestions}[/cyan]", 
                          title="Agentic Suggestions", border_style="cyan"))
        if Prompt.ask("Create suggested files?", choices=["y", "n"], default="n") == "y":
            console.print("[yellow]Agentic file creation will be added in future version[/yellow]")

    if os.path.exists(file):
        if Prompt.ask(f"[yellow]{file} exists. Overwrite?[/yellow]", choices=["y", "n"], default="n") == "n":
            console.print("[red]Creation discarded.[/red]")
            return
    
    choice = Prompt.ask("\nSave file?", choices=["y", "n"], default="y")
    if choice == "y":
        with open(file, "w", encoding="utf-8") as f:
            f.write(cleaned)
        console.print(f"[green]✓ File created: {file}[/green]")
        
        # Store in memory
        if memory_manager:
            memory_manager.add_conversation(f"Created file {file}: {description}", cleaned[:500])
        
        # Generate tests if requested
        if with_tests:
            test_file = file.replace(".py", "_test.py").replace(".js", ".test.js")
            test_prompt = f"""
            Generate unit tests for this code:
            {cleaned}
            
            Output ONLY the test code in {lang}.
            """
            test_code = extract_code(get_response(test_prompt, debug))
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_code)
            console.print(f"[green]✓ Tests created: {test_file}[/green]")
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
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)"),
    memory: bool = typer.Option(True, help="Enable context memory for better fixes")
):
    """Fix bugs with context awareness from past fixes.
    
    Enhanced with memory to learn from previous bug fixes and apply similar patterns.
    """
    global bot, repo_map_cache
    
    # Interactive model selection for offline mode
    if offline and not model and MODEL_SELECTOR_AVAILABLE:
        selection = select_model()
        if selection is None:
            console.print("[yellow]Cancelled. Exiting.[/yellow]")
            return
        repo, file, is_cached, path = selection
        model = f"{repo}/{file}"
    
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model)
    
    # Initialize memory
    memory_manager = None
    if memory and MEMORY_AVAILABLE:
        try:
            memory_manager = MemoryManager(user_id="default", enable_vector_store=True)
            console.print("[dim]✓ Memory enabled - learning from past fixes[/dim]")
        except Exception as e:
            logger.warning(f"Memory disabled: {e}")
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
                    diff = _fix_file(file_path, repo_map_cache[path], export, preview, iterative, suggest, debug, memory_manager)
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
            diff = _fix_file(path, repo_map_cache.get(os.path.dirname(path)), export, preview, iterative, suggest, debug, memory_manager)
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

def _fix_file(file: str, repo_map: dict | None, export: str | None, preview: bool, iterative: bool, suggest: bool, debug: bool, memory_manager=None) -> tuple | None:
    """Internal helper to fix one file with repo context and memory.
    Args:
        file: Path to file.
        repo_map: Repository metadata from scan_repo.
        export: Export diff path.
        preview: Enable batch preview.
        iterative: Enable refinement mode.
        suggest: Show structured suggestions.
        debug: Enable debug logging.
        memory_manager: Optional memory manager for context-aware fixes.
    Returns:
        Tuple (file, (original, cleaned, diff_text, suggestion)) or None.
    Why it works: Uses memory to learn from past fixes and apply patterns.
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
    
    # Add memory context for better fixes
    memory_context = ""
    if memory_manager:
        mem_ctx = memory_manager.get_context_for_prompt(f"fixing {lang} code", max_context_length=800)
        if mem_ctx:
            memory_context = f"\n\nLearned patterns from past fixes:\n{mem_ctx}"

    suggestion = ""
    if suggest:
        prompt = f"""
        You are a code fixer. Analyze this file and repo context, then provide a table in Markdown with:
        - Issue: What's wrong (e.g., "Potential division by zero")
        - Fix: Proposed change (e.g., "Add error handling")
        - Impact: Why it matters (e.g., "Prevents runtime errors")
        Repo context: {context}{memory_context}
        File ({file}, language: {lang}):
        {original}
        """
        suggestion = get_response(prompt, debug)
        console.print(Panel(Markdown(suggestion), title="Suggested Fixes", border_style="yellow"))

    prompt = f"""
    You are a professional code fixer.
    Repository map (for context): {context}{memory_context}
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
            
            # Store fix in memory for learning
            if memory_manager:
                memory_manager.add_conversation(
                    f"Fixed {lang} file: {file}", 
                    f"Applied fix pattern. Diff summary: {diff_text[:300]}"
                )
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
    model: str = typer.Option(None, help="Model name (e.g., TheBloke/CodeLlama-7B-GGUF/codellama-7b.Q4_K_M.gguf)"),
    memory: bool = typer.Option(True, help="Enable context memory for better documentation"),
    style: str = typer.Option("detailed", help="Documentation style: concise, detailed, tutorial")
):
    """Generate context-aware documentation with memory.
    
    Enhanced features:
    - Memory: Learns documentation patterns
    - Styles: Choose between concise, detailed, or tutorial formats
    - Context: Uses past documentation for consistency
    """
    global bot
    
    # Interactive model selection for offline mode
    if offline and not model and MODEL_SELECTOR_AVAILABLE:
        selection = select_model()
        if selection is None:
            console.print("[yellow]Cancelled. Exiting.[/yellow]")
            return
        repo, file, is_cached, path = selection
        model = f"{repo}/{file}"
    
    bot = load_adapter(model_name="openrouter", offline=offline, debug=debug, gguf_model=model)
    
    # Initialize memory
    memory_manager = None
    if memory and MEMORY_AVAILABLE:
        try:
            memory_manager = MemoryManager(user_id="default", enable_vector_store=True)
            console.print("[dim]✓ Memory enabled - consistent documentation style[/dim]")
        except Exception as e:
            logger.warning(f"Memory disabled: {e}")
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

        # Build style-specific instructions
        style_instructions = {
            "concise": "Provide brief, one-line summaries for each component.",
            "detailed": "Provide comprehensive explanations with examples and usage patterns.",
            "tutorial": "Provide step-by-step explanations suitable for learning, with code examples."
        }
        style_guide = style_instructions.get(style, style_instructions["detailed"])
        
        # Get memory context for consistent documentation
        mem_context = ""
        if memory_manager:
            mem_ctx = memory_manager.get_context_for_prompt("documentation patterns", max_context_length=500)
            if mem_ctx:
                mem_context = f"\n\nConsistent documentation style from past docs:\n{mem_ctx}"
        
        prompt = f"""
        You are a code documentation expert. Given the repository structure and file contents below, provide a Markdown summary of the codebase.
        Documentation style: {style_guide}
        For each file, list:
        - Purpose
        - Key functions/classes
        - Dependencies (imports)
        - One-line summary
        Group by module/folder if applicable. Output only the Markdown summary.{mem_context}
        {chr(10).join(context)}
        """
        response = get_response(prompt, debug)
    else:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        
        # Add memory context for single file documentation
        mem_context = ""
        if memory_manager:
            mem_ctx = memory_manager.get_context_for_prompt("code documentation", max_context_length=400)
            if mem_ctx:
                mem_context = f"\n\nConsistent style from past docs:\n{mem_ctx}"
        
        style_instructions = {
            "concise": "Provide a brief explanation in 2-3 paragraphs.",
            "detailed": "Provide a comprehensive explanation with usage examples.",
            "tutorial": "Explain as if teaching a beginner, with step-by-step breakdown."
        }
        style_guide = style_instructions.get(style, style_instructions["detailed"])
        
        prompt = f"""
        Explain this code in plain English, in Markdown format.
        Style: {style_guide}{mem_context}
        
        Code:
        {code}
        """
        response = get_response(prompt, debug)

    if format == "txt":
        response = re.sub(r"[`*#\[\]]", "", response)
    
    render_code_blocks(response)
    
    # Store documentation pattern in memory
    if memory_manager:
        memory_manager.add_conversation(
            f"Generated {style} documentation for: {path}",
            response[:500]  # Store summary for future reference
        )

    if export:
        with open(export, "w", encoding="utf-8") as f:
            f.write(response)
        console.print(f"[green]✓ Documentation exported to {export}[/green]")


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




