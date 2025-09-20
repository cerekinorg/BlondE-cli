import difflib
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
def load_adapter():
    try:
        with open("config.yml") as f:
            cfg = yaml.safe_load(f)
        model = cfg.get("default_model", "openrouter")
    except FileNotFoundError:
        model = "openrouter"

    if model == "openai":
        from models.openai import OpenAIAdapter
        return OpenAIAdapter()
    elif model == "hf":
        from models.hf import HFAdapter
        return HFAdapter()
    else:
        from models.openrouter import OpenRouterAdapter
        return OpenRouterAdapter()

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

# def get_response(prompt: str) -> str:
#     with console.status("[bold magenta]Blonde is thinking...[/bold magenta]", spinner="dots"):
#         return bot.chat(prompt)

def get_response(prompt: str) -> str:
    with console.status("[bold magenta]Blonde is thinking...[/bold magenta]", spinner="dots"):
        response = bot.chat(prompt)

        # If it's already plain text
        if isinstance(response, str):
            return response.strip()

        # If it's a dict (like the JSON you saw)
        try:
            return response["choices"][0]["message"]["content"].strip()
        except Exception:
            return str(response).strip()


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

def render_code_blocks(text: str) -> str:
    """Detects ```python code``` blocks and replaces with Rich Syntax objects"""
    if "```" not in text:
        return text
    parts = []
    segments = text.split("```")
    for i, segment in enumerate(segments):
        if i % 2 == 1:  # inside a code block
            lang, *code_lines = segment.split("\n")
            code = "\n".join(code_lines)
            parts.append(Syntax(code, lang or "python", theme="monokai", line_numbers=False))
        else:
            parts.append(Markdown(segment))
    return parts

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



def render_code_blocks(text: str):
    """Detects ```lang code``` blocks and renders them cleanly."""
    if "```" not in text:
        console.print(Markdown(text))
        return

    segments = text.split("```")
    for i, segment in enumerate(segments):
        if i % 2 == 1:  # inside a code block
            lang, *code_lines = segment.split("\n")
            code = "\n".join(code_lines)
            console.print(Syntax(code, lang or "python", theme="monokai", line_numbers=False))
        else:
            if segment.strip():
                console.print(Markdown(segment))


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
# def fix(file: str):
#     """Fix bugs in a Python file and show diff"""
#     with open(file, "r") as f:
#         original = f.read()
#     response = get_response(
#     f"""
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

#     show_diff(original, cleaned, file)

#     console.print("\n[bold yellow]Preview of fixed file:[/bold yellow]")
#     console.print(Syntax(cleaned, "python", theme="monokai", line_numbers=True))

#     choice = Prompt.ask("\nApply changes?", choices=["y", "n", "save-as"], default="save-as")
#     if choice == "y":
#         with open(file, "w") as f:
#             f.write(cleaned)
#     elif choice == "save-as":
#         ext = file.split(".")[-1]
#         save_as = file.replace(f".{ext}", f"_fixed.{ext}")
#         with open(save_as, "w") as f:
#             f.write(cleaned)
#         console.print(f"[bold green]✅ Fixed file saved as {save_as}[/bold green]")
#     else:
#         console.print("[bold red]❌ Changes discarded[/bold red]")

@app.command()
def fix(
    file: str,
    export: str = typer.Option(None, help="Export diff instead of applying"),
):
    """Fix bugs in a code file and show diff"""
    with open(file, "r") as f:
        original = f.read()

    response = get_response(
        f"""
        You are a professional code fixer. 
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

    # Show diff in console
    console.print(diff_text, style="yellow")

    # If export flag used → save diff and exit early
    if export:
        with open(export, "w") as out:
            out.write(diff_text)
        console.print(f"[bold green]✅ Diff exported to {export}[/bold green]")
        return

    # Otherwise continue with preview + interactive apply
    console.print("\n[bold yellow]Preview of fixed file:[/bold yellow]")
    console.print(Syntax(cleaned, "python", theme="monokai", line_numbers=True))

    choice = Prompt.ask(
        "\nApply changes?", choices=["y", "n", "save-as"], default="save-as"
    )
    if choice == "y":
        with open(file, "w") as f:
            f.write(cleaned)
        console.print(f"[bold green]✅ Changes applied to {file}[/bold green]")
    elif choice == "save-as":
        ext = file.split(".")[-1]
        save_as = file.replace(f".{ext}", f"_fixed.{ext}")
        with open(save_as, "w") as f:
            f.write(cleaned)
        console.print(f"[bold green]✅ Fixed file saved as {save_as}[/bold green]")
    else:
        console.print("[bold red]❌ Changes discarded[/bold red]")


# @app.command()
# def doc(file: str):
#     """Explain a Python file in plain English"""
#     with open(file, "r") as f:
#         code = f.read()
#     response = get_response(f"Explain this code:\n{code}")
#     console.print(render_code_blocks(response))

@app.command()
def doc(file: str, export: str = typer.Option(None, help="Export explanation to a file")):
    """Explain a code file in plain English"""
    with open(file, "r") as f:
        code = f.read()

    response = get_response(f"Explain this code:\n{code}")
    console.print(render_code_blocks(response))

    if export:
        with open(export, "w") as out:
            out.write(response)
        console.print(f"[green]Documentation exported to {export}[/green]")


# =====================
#  Entrypoint
# =====================
if __name__ == "__main__":
    app()
