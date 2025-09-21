import difflib
import os
import time
import typer
import yaml
import json
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
#from blonde-cli.repo_map import scan_repo

console = Console()
app = typer.Typer()

# =====================
#  ASCII LOGO
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

[green]In chat mode:[/green]
 • Type any message to chat with Blonde
 • [bold]exit[/bold] or [bold]quit[/bold] to leave
 • [bold]help[/bold] to see this message again
 • [bold]/save[/bold] → export chat to Markdown
"""

HISTORY_FILE = Path.home() / ".blonde_history.json"

# =====================
#  Adapter Loader
# =====================
# def load_adapter():
#     try:
#         with open("config.yml") as f:
#             cfg = yaml.safe_load(f)
#         model = cfg.get("default_model", "openrouter")
#     except FileNotFoundError:
#         model = "openrouter"

#     if model == "openai":
#         from models.openai import OpenAIAdapter
#         return OpenAIAdapter()
#     elif model == "hf":
#         from models.hf import HFAdapter
#         return HFAdapter()
#     else:
#         from models.openrouter import OpenRouterAdapter
#         return OpenRouterAdapter()

# In cli.py (replace load_adapter)
def load_adapter(debug: bool = False):
    """Loads the appropriate model adapter based on config.yml."""
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

bot = load_adapter()

# =====================
#  Shared Helpers
# =====================
def animate_logo():
    console.clear()
    console.print(Text(ASCII_LOGO, style="bold magenta"), justify="center")
    console.print(Panel(
        Text("Welcome to Blonde CLI 🚀", justify="center", style="bold cyan"),
        border_style="blue", expand=False
    ))
    console.print(HELP_TEXT)
    time.sleep(1)





# @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
# def get_response(prompt: str) -> str:
#     """Fetches response from the active adapter, normalizing output.
#     Args:
#         prompt: User input to send to the model.
#     Returns:
#         Stripped string response.
#     Raises:
#         ValueError: If response format is invalid.
#     """
#     try:
#         response = bot.chat(prompt)
#         if isinstance(response, str):
#             return response.strip()
#         elif isinstance(response, dict):
#             # Handle OpenAI/OpenRouter-style response
#             content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
#             if not content:
#                 raise ValueError("Empty content in response")
#             return content.strip()
#         else:
#             raise ValueError(f"Unexpected response type: {type(response)}")
#     except Exception as e:
#         console.print(f"[red]API Error: {e}[/red]")
#         return "Sorry, there was an error processing your request."

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_response(prompt: str, debug: bool = False) -> str:
    """Fetches response from the active adapter, normalizing output.
    Args:
        prompt: User input to send to the model.
        debug: If True, log debug info.
    Returns:
        Stripped string response.
    """
    try:
        response = bot.chat(prompt)
        if isinstance(response, str):
            return response.strip()
        elif isinstance(response, dict):
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                raise ValueError("Empty content in response")
            return content.strip()
        else:
            raise ValueError(f"Unexpected response type: {type(response)}")
    except Exception as e:
        console.print(f"[red]API Error: {e}[/red]")
        return "Sorry, there was an error processing your request."


def show_diff(original: str, modified: str, filename: str):
    diff = unified_diff(
        original.splitlines(),
        modified.splitlines(),
        fromfile=f"{filename} (original)",
        tofile=f"{filename} (fixed)",
        lineterm=""
    )
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            console.print(line, style="green")
        elif line.startswith("-") and not line.startswith("---"):
            console.print(line, style="red")
        elif line.startswith("@@"):
            console.print(line, style="yellow")
        else:
            console.print(line, style="white")

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

# def render_code_blocks(text: str) -> None:
#     """Renders Markdown text with code blocks using syntax highlighting.
#     Args:
#         text: Input string with optional ```lang code``` blocks.
#     """
#     if "```" not in text:
#         console.print(Markdown(text))
#         return

#     segments = text.split("```")
#     for i, segment in enumerate(segments):
#         if i % 2 == 1:  # Inside code block
#             try:
#                 lang, *code_lines = segment.split("\n", 1)
#                 code = code_lines[0] if code_lines else ""
#                 console.print(Syntax(code.strip(), lang.strip() or "python", theme="monokai", line_numbers=False))
#             except Exception as e:
#                 console.print(f"[red]Error rendering code: {e}[/red]")
#                 console.print(segment, style="white")
#         else:
#             if segment.strip():
#                 console.print(Markdown(segment))


# In utils.py (replace render_code_blocks)
def render_code_blocks(text: str) -> None:
    """Renders Markdown text with code blocks using syntax highlighting."""
    text = text.strip()  # Remove leading/trailing newlines
    if "```" not in text:
        console.print(Markdown(text, style="white"))
        return

    segments = text.split("```")
    for i, segment in enumerate(segments):
        if i % 2 == 1:  # Inside code block
            try:
                lang, *code_lines = segment.split("\n", 1)
                code = code_lines[0].strip() if code_lines else ""
                if code:
                    console.print(Syntax(code, lang.strip() or "python", theme="monokai", line_numbers=False))
            except Exception as e:
                console.print(f"[red]Error rendering code: {e}[/red]")
                console.print(segment.strip(), style="white")
        else:
            if segment.strip():
                console.print(Markdown(segment.strip(), style="white"))

# =====================
#  Chat Mode
# =====================
def render_chat(chat_history):
    layout = Layout()
    panels = []
    for sender, message in chat_history:
        if sender == "You":
            panel = Panel(message, title=f"[green]{sender}[/green]", border_style="green", expand=False)
        else:
            # Handle code blocks nicely
            content = render_code_blocks(message)
            panel = Panel(content, title=f"[magenta]{sender}[/magenta]", border_style="magenta", expand=False)
        panels.append(panel)

    if panels:
        layout.split(*[Layout(panel) for panel in panels])
    else:
        layout.update(Panel("Start the conversation!", border_style="blue", expand=False))
    return layout


import re

def extract_code(text: str) -> str:
    """
    Extracts code from markdown-style ``` blocks, or returns raw text if no blocks.
    Works for any language (python, java, js, c, etc.).
    """
    if "```" in text:
        matches = re.findall(r"```(?:\w+)?\n([\s\S]*?)```", text)
        if matches:
            return matches[0].strip()
    return text.strip()





def stream_response(text: str, delay: float = 0.02):
    """Stream text like Claude typing."""
    buffer = ""
    for chunk in text.split():
        buffer += chunk + " "
        console.print(chunk, end=" ", style="magenta", highlight=False, soft_wrap=True)
        time.sleep(delay)
    console.print("\n")  # end line
    return buffer

@app.command()
def chat():
    animate_logo()
    console.print(Panel(Text("Type your prompt below. Use /help for commands.", justify="left"), border_style="cyan"))

    chat_history = load_history()

    while True:
        user_input = Prompt.ask("[bold green]You[/bold green]")
        
        # Commands
        if user_input.lower() in ("exit", "quit"):
            save_history(chat_history)
            console.print("[bold red]Goodbye![/bold red]")
            break
        if user_input.lower() == "/help":
            console.print(Panel(Text(HELP_TEXT, justify="left"), border_style="cyan"))
            continue
        if user_input.lower() == "/clear":
            chat_history = []
            console.print("[bold yellow]Chat cleared.[/bold yellow]")
            continue
        if user_input.lower() == "/save":
            out_file = "blonde_chat.md"
            with open(out_file, "w") as f:
                for sender, msg in chat_history:
                    f.write(f"**{sender}:** {msg}\n\n")
            console.print(f"[bold green]💾 Chat exported to {out_file}[/bold green]")
            continue

        chat_history.append(("You", user_input))
        # console.print(f"[green]You:[/green] {user_input}\n")

        console.print("[magenta]Blonde:[/magenta]")
        try:
            response = get_response(user_input)
        except Exception as e:
            response = f"**Error:** {e}"

        chat_history.append(("Blonde", response))
        render_code_blocks(response)

        console.rule(style="dim")  # divider between turns

# =====================
#  Command Mode
# =====================
@app.command()
def gen(prompt: str):
    """Generate code from a prompt"""
    response = get_response(prompt)
    console.print(render_code_blocks(response))



# @app.command()
# def fix(
#     file: str,
#     export: str = typer.Option(None, help="Export diff instead of applying"),
# ):
#     """Fix bugs in a code file and show diff"""
#     with open(file, "r") as f:
#         original = f.read()

#     response = get_response(
#         f"""
#         You are a professional code fixer. 
#         Given the following file, output ONLY the corrected source code. 
#         Do not include explanations, notes, or markdown fences. 
#         Preserve the file’s language and formatting.

#         ### Original file ({file}):
#         {original}

#         ### Corrected file:
#         """
#     )

#     cleaned = extract_code(response)

#     # Generate unified diff
#     diff = difflib.unified_diff(
#         original.splitlines(),
#         cleaned.splitlines(),
#         fromfile=f"{file} (original)",
#         tofile=f"{file} (fixed)",
#         lineterm="",
#     )
#     diff_text = "\n".join(diff)

#     # Show diff in console
#     console.print(diff_text, style="yellow")

#     # If export flag used → save diff and exit early
#     if export:
#         with open(export, "w") as out:
#             out.write(diff_text)
#         console.print(f"[bold green]✅ Diff exported to {export}[/bold green]")
#         return

#     # Otherwise continue with preview + interactive apply
#     console.print("\n[bold yellow]Preview of fixed file:[/bold yellow]")
#     console.print(Syntax(cleaned, "python", theme="monokai", line_numbers=True))

#     choice = Prompt.ask(
#         "\nApply changes?", choices=["y", "n", "save-as"], default="save-as"
#     )
#     if choice == "y":
#         with open(file, "w") as f:
#             f.write(cleaned)
#         console.print(f"[bold green]✅ Changes applied to {file}[/bold green]")
#     elif choice == "save-as":
#         ext = file.split(".")[-1]
#         save_as = file.replace(f".{ext}", f"_fixed.{ext}")
#         with open(save_as, "w") as f:
#             f.write(cleaned)
#         console.print(f"[bold green]✅ Fixed file saved as {save_as}[/bold green]")
#     else:
#         console.print("[bold red]❌ Changes discarded[/bold red]")



import os
import ast

# Directories we never want to scan
EXCLUDED_DIRS = {"__pycache__", ".git", "venv", "node_modules", ".idea", ".mypy_cache"}

# Extensions we care about
INCLUDED_EXTS = {
    "py", "js", "ts", "java", "c", "cpp", "json", "yml", "yaml", "toml", "md"
}

def scan_repo(path: str) -> dict:
    """
    Walk through a repo, extract basic info from supported files.
    Skips cache/venv/git folders.
    """
    repo_map = {}

    for root, dirs, files in os.walk(path):
        # modify dirs in-place → prevents walking into excluded folders
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            ext = file.split(".")[-1]
            if ext not in INCLUDED_EXTS:
                continue

            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, path)

            repo_map[relative_path] = {
                "functions": [],
                "classes": [],
                "imports": []
            }

            try:
                if ext == "py":
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            repo_map[relative_path]["functions"].append(node.name)
                        elif isinstance(node, ast.ClassDef):
                            repo_map[relative_path]["classes"].append(node.name)
                        elif isinstance(node, (ast.Import, ast.ImportFrom)):
                            for alias in node.names:
                                repo_map[relative_path]["imports"].append(alias.name)

                else:
                    # for non-Python files we just track that they exist
                    repo_map[relative_path]["functions"].append(f"unparsed_{ext}")

            except Exception as e:
                repo_map[relative_path]["error"] = str(e)

    return repo_map



@app.command()
def fix(
    path: str,
    export: str = typer.Option(None, help="Export diff(s) instead of applying"),
):
    """
    Fix bugs in a file OR all files in a folder, showing diffs.
    Skips irrelevant dirs like venv, __pycache__, .git.
    """
    if os.path.isdir(path):
        repo_map = scan_repo(path)
        console.print(f"[cyan]Repo map built with {len(repo_map)} files[/cyan]")

        for relative_path in repo_map:
            file_path = os.path.join(path, relative_path)
            _fix_file(file_path, repo_map, export)

    else:
        # single file fix
        _fix_file(path, None, export)


def _fix_file(file: str, repo_map: dict | None, export: str | None):
    """Internal helper to fix one file with repo context."""
    with open(file, "r", encoding="utf-8") as f:
        original = f.read()

    context = str(repo_map)[:2000] if repo_map else ""  # truncate for safety

    response = get_response(
        f"""
        You are a professional code fixer. 
        Repository map (for context):
        {context}

        Given the following file, output ONLY the corrected source code. 
        Do not include explanations, notes, or markdown fences. 
        Preserve the file’s language and formatting.

        ### Original file ({file}):
        {original}

        ### Corrected file:
        """
    )

    cleaned = extract_code(response)

    # Generate unified diff
    diff = difflib.unified_diff(
        original.splitlines(),
        cleaned.splitlines(),
        fromfile=f"{file} (original)",
        tofile=f"{file} (fixed)",
        lineterm="",
    )
    diff_text = "\n".join(diff)

    console.print(diff_text, style="yellow")

    # Export mode → save diff(s) only
    if export:
        export_path = (
            export if os.path.isdir(export) else export
        )
        if os.path.isdir(export):
            # save one diff per file
            diff_file = os.path.join(export, os.path.basename(file) + ".diff")
            with open(diff_file, "w", encoding="utf-8") as out:
                out.write(diff_text)
            console.print(f"[bold green]✅ Diff exported → {diff_file}[/bold green]")
        else:
            # single export file (append all diffs)
            with open(export, "a", encoding="utf-8") as out:
                out.write(diff_text + "\n\n")
            console.print(f"[bold green]✅ Diff appended → {export}[/bold green]")
        return

    # Interactive preview
    console.print("\n[bold yellow]Preview of fixed file:[/bold yellow]")
    ext = file.split(".")[-1]
    console.print(Syntax(cleaned, ext, theme="monokai", line_numbers=True))

    choice = Prompt.ask(
        "\nApply changes?", choices=["y", "n", "save-as"], default="save-as"
    )
    if choice == "y":
        with open(file, "w", encoding="utf-8") as f:
            f.write(cleaned)
        console.print(f"[bold green]✅ Changes applied to {file}[/bold green]")
    elif choice == "save-as":
        save_as = file.replace(f".{ext}", f"_fixed.{ext}")
        with open(save_as, "w", encoding="utf-8") as f:
            f.write(cleaned)
        console.print(f"[bold green]✅ Fixed file saved as {save_as}[/bold green]")
    else:
        console.print("[bold red]❌ Changes discarded[/bold red]")




# In cli.py (add new command)
# @app.command()
# def doc(
#     path: str,
#     export: str = typer.Option(None, help="Export explanation to a file"),
#     format: str = typer.Option("md", help="Output format: md, txt"),
# ):
#     """Explain code in a file or folder in plain English.
#     Args:
#         path: File or directory to document.
#         export: Optional file to save output.
#         format: Output format (md or txt).
#     """
#     if os.path.isdir(path):
#         repo_map = scan_repo(path)
#         console.print(f"[cyan]Scanning {len(repo_map)} files in {path}[/cyan]")
        
#         # Build context with repo map and file contents
#         context = ["Repository structure:"]
#         for rel_path, info in repo_map.items():
#             context.append(f"- {rel_path}: {info.get('functions', [])}, {info.get('classes', [])}, {info.get('imports', [])}")
#             try:
#                 with open(os.path.join(path, rel_path), "r", encoding="utf-8") as f:
#                     context.append(f"\n### {rel_path}\n```\n{f.read()}\n```")
#             except Exception as e:
#                 context.append(f"Error reading {rel_path}: {e}")
        
#         prompt = f"""
#         You are a code documentation expert. Given the repository structure and file contents below, provide a concise Markdown summary of the codebase. For each file, list:
#         - Purpose
#         - Key functions/classes
#         - Dependencies (imports)
#         - One-line summary
#         Group by module/folder if applicable. Output only the Markdown summary.

#         {chr(10).join(context)}
#         """
#         response = get_response(prompt)
#     else:
#         with open(path, "r", encoding="utf-8") as f:
#             code = f.read()
#         prompt = f"Explain this code in plain English, in Markdown format:\n{code}"
#         response = get_response(prompt)

#     if format == "txt":
#         # Strip Markdown formatting for plain text
#         response = re.sub(r"[`*#\[\]]", "", response)
    
#     render_code_blocks(response)

#     if export:
#         with open(export, "w", encoding="utf-8") as out:
#             out.write(response)
#         console.print(f"[green]Documentation exported to {export}[/green]")


# In cli.py (replace doc command)
from rich.progress import Progress
from rich.panel import Panel

@app.command()
def doc(
    path: str,
    export: str = typer.Option(None, help="Export explanation to a file"),
    format: str = typer.Option("md", help="Output format: md, txt"),
    debug: bool = typer.Option(False, help="Enable debug logging")
):
    """Explain code in a file or folder in plain English."""
    global bot
    bot = load_adapter(debug=debug)  # Reload adapter with debug flag
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
        response = get_response(prompt, debug=debug)
    else:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        prompt = f"Explain this code in plain English, in Markdown format:\n{code}"
        response = get_response(prompt, debug=debug)

    if format == "txt":
        response = re.sub(r"[`*#\[\]]", "", response)
    
    render_code_blocks(response)

    if export:
        with open(export, "w", encoding="utf-8") as out:
            out.write(response)
        console.print(f"[green]Documentation exported to {export}[/green]")

# =====================
#  Entrypoint
# =====================
if __name__ == "__main__":
    app()
