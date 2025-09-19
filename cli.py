# # Custom ASCII Logo for Blonde
# # ASCII_LOGO = r"""
# #  /$$$$$$$  /$$                           /$$          
# # | $$__  $$| $$                          | $$          
# # | $$  \ $$| $$  /$$$$$$  /$$$$$$$   /$$$$$$$  /$$$$$$ 
# # | $$$$$$$ | $$ /$$__  $$| $$__  $$ /$$__  $$ /$$__  $$
# # | $$__  $$| $$| $$  \ $$| $$  \ $$| $$  | $$| $$$$$$$$
# # | $$  \ $$| $$| $$  | $$| $$  | $$| $$  | $$| $$_____/
# # | $$$$$$$/| $$|  $$$$$$/| $$  | $$|  $$$$$$$|  $$$$$$$
# # |_______/ |__/ \______/ |__/  |__/ \_______/ \_______/                                   
                                                      



# # blonde_cli.py
# from rich.console import Console
# from rich.panel import Panel
# from rich.markdown import Markdown
# from rich.live import Live
# from rich.align import Align
# from rich.prompt import Prompt
# from rich.layout import Layout
# from rich.text import Text
# from models.openrouter import OpenRouterAdapter
# import time

# console = Console()
# bot = OpenRouterAdapter()

# # Custom ASCII Logo for Blonde
# ASCII_LOGO = r"""
#  ██████╗ ██╗      ██████╗ ███╗   ██╗██████╗ ███████╗
#  ██╔══██╗██║     ██╔═══██╗████╗  ██║██╔══██╗██╔════╝
# ██████╔╝██║     ██║   ██║██╔██╗ ██║██║  ██║█████╗  
# ██╔══██╗██║     ██║   ██║██║╚██╗██║██║  ██║██╔══╝  
#  ██████╔╝███████╗╚██████╔╝██║ ╚████║██████╔╝███████╗
#  ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝
# """

# HELP_TEXT = """
# [bold cyan]Blonde CLI Help[/bold cyan]

# [green]Commands:[/green]
#  • Type any message to chat with Blonde
#  • [bold]exit[/bold] or [bold]quit[/bold] to leave
#  • [bold]help[/bold] to see this message again
# """

# # def animate_logo():
# #     console.clear()
# #     for line in ASCII_LOGO.splitlines():
# #         console.print(Text(line, style="bold magenta"), justify="center")
# #         time.sleep(0.05)
# #     console.print(Panel(Text("Welcome to Blonde CLI!", justify="center", style="bold cyan"),
# #                         border_style="blue", expand=False))
# #     time.sleep(1)
# #     console.clear()


# def animate_logo():
#     console.clear()
#     console.print(Text(ASCII_LOGO, style="bold magenta"), justify="center")
#     console.print(Panel(
#         Text("Welcome to Blonde CLI 🚀", justify="center", style="bold cyan"),
#         border_style="blue", expand=False
#     ))
#     console.print(HELP_TEXT)
#     time.sleep(1)


# def render_chat(chat_history):
#     """Render chat messages as panels inside a single layout."""
#     layout = Layout()
#     panels = []
#     for sender, message in chat_history:
#         if sender == "You":
#             panel = Panel(message, title=f"[green]{sender}[/green]", border_style="green", expand=False)
#         else:
#             panel = Panel(Markdown(message), title=f"[magenta]{sender}[/magenta]", border_style="magenta", expand=False)
#         panels.append(panel)

#     if panels:
#         layout.split(*[Layout(panel) for panel in panels])
#     else:
#         layout.update(Panel("Start the conversation!", border_style="blue", expand=False))
#     return layout

# from difflib import unified_diff

# def show_diff(original: str, modified: str, filename: str):
#     diff = unified_diff(
#         original.splitlines(),
#         modified.splitlines(),
#         fromfile=f"{filename} (original)",
#         tofile=f"{filename} (fixed)",
#         lineterm=""
#     )
#     for line in diff:
#         if line.startswith("+"):
#             console.print(line, style="green")
#         elif line.startswith("-"):
#             console.print(line, style="red")
#         else:
#             console.print(line, style="white")


# def main():
#     animate_logo()
#     console.print(Panel(Text(HELP_TEXT, justify="left"), border_style="cyan", expand=False))

#     chat_history = []

#     with Live(render_chat(chat_history), refresh_per_second=4, console=console) as live:
#         while True:
#             user_input = Prompt.ask("[bold green]You[/bold green]")
#             if user_input.lower() in ("exit", "quit"):
#                 console.print("[bold red]Goodbye![/bold red]")
#                 break
#             if user_input.lower() == "help":
#                 console.print(Panel(Text(HELP_TEXT, justify="left"), border_style="cyan", expand=False))
#                 continue

#             # Add user's message
#             chat_history.append(("You", user_input))
#             live.update(render_chat(chat_history))

#             # Add temporary typing message
#             chat_history.append(("Blonde", "[italic magenta]Blonde is typing...[/italic magenta]"))
#             live.update(render_chat(chat_history))

#             # Get bot response
#             try:
#                 response = bot.chat(user_input)
#             except Exception as e:
#                 response = f"[bold red]Error:[/bold red] {e}"

#             # Replace typing message with real response
#             chat_history[-1] = ("Blonde", response)
#             live.update(render_chat(chat_history))

# if __name__ == "__main__":
#     main()


# blonde_cli.py
import time
import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.prompt import Prompt
from rich.layout import Layout
from rich.text import Text
from rich.status import Status
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
"""

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

def get_response(prompt: str) -> str:
    with console.status("[bold magenta]Blonde is thinking...[/bold magenta]", spinner="dots"):
        return bot.chat(prompt)

def show_diff(original: str, modified: str, filename: str):
    diff = unified_diff(
        original.splitlines(),
        modified.splitlines(),
        fromfile=f"{filename} (original)",
        tofile=f"{filename} (fixed)",
        lineterm=""
    )
    for line in diff:
        if line.startswith("+"):
            console.print(line, style="green")
        elif line.startswith("-"):
            console.print(line, style="red")
        else:
            console.print(line, style="white")

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
            panel = Panel(Markdown(message), title=f"[magenta]{sender}[/magenta]", border_style="magenta", expand=False)
        panels.append(panel)

    if panels:
        layout.split(*[Layout(panel) for panel in panels])
    else:
        layout.update(Panel("Start the conversation!", border_style="blue", expand=False))
    return layout

@app.command()
def chat():
    animate_logo()
    console.print(Panel(Text(HELP_TEXT, justify="left"), border_style="cyan", expand=False))

    chat_history = []
    with Live(render_chat(chat_history), refresh_per_second=4, console=console) as live:
        while True:
            user_input = Prompt.ask("[bold green]You[/bold green]")
            if user_input.lower() in ("exit", "quit"):
                console.print("[bold red]Goodbye![/bold red]")
                break
            if user_input.lower() == "help":
                console.print(Panel(Text(HELP_TEXT, justify="left"), border_style="cyan", expand=False))
                continue

            chat_history.append(("You", user_input))
            live.update(render_chat(chat_history))

            try:
                response = get_response(user_input)
            except Exception as e:
                response = f"[bold red]Error:[/bold red] {e}"

            chat_history.append(("Blonde", response))
            live.update(render_chat(chat_history))

# =====================
#  Command Mode
# =====================
@app.command()
def gen(prompt: str):
    """Generate code from a prompt"""
    response = get_response(prompt)
    console.print(Markdown(response))

@app.command()
def fix(file: str):
    """Fix bugs in a Python file and show diff"""
    with open(file, "r") as f:
        original = f.read()

    response = get_response(f"Fix bugs in this Python code:\n{original}")
    show_diff(original, response, file)

    save_as = file.replace(".py", "_fixed.py")
    with open(save_as, "w") as f:
        f.write(response)

    console.print(f"[bold green]✅ Fixed file saved as {save_as}[/bold green]")

@app.command()
def doc(file: str):
    """Explain a Python file in plain English"""
    with open(file, "r") as f:
        code = f.read()
    response = get_response(f"Explain this code:\n{code}")
    console.print(Markdown(response))

# =====================
#  Entrypoint
# =====================
if __name__ == "__main__":
    app()
