# # # cli.py
# # import typer
# # from models.openai import OpenAIAdapter
# # from models.hf import HFAdapter
# # from models.openrouter import OpenRouterAdapter

# # app = typer.Typer()

# # # pick your default model here
# # # model = OpenAIAdapter()
# # model = OpenRouterAdapter()


# # @app.command()
# # def gen(prompt: str):
# #     """Generate code from natural language prompt"""
# #     print(model.chat(prompt))

# # @app.command()
# # def fix(file: str):
# #     """Suggest fixes for a given Python file"""
# #     with open(file, "r") as f:
# #         code = f.read()
# #     prompt = f"Fix bugs in this Python code:\n{code}"
# #     print(model.chat(prompt))

# # @app.command()
# # def doc(file: str):
# #     """Generate documentation for a Python file"""
# #     with open(file, "r") as f:
# #         code = f.read()
# #     prompt = f"Explain this code in plain English:\n{code}"
# #     print(model.chat(prompt))

# # if __name__ == "__main__":
# #     app()


# # blonde_cli.py
# from rich.console import Console
# from rich.panel import Panel
# from rich.markdown import Markdown
# from rich.live import Live
# from rich.align import Align
# from rich.spinner import Spinner
# from rich.layout import Layout
# from rich.text import Text
# from rich.prompt import Prompt
# from models.openrouter import OpenRouterAdapter
# import time

# console = Console()
# bot = OpenRouterAdapter()

# def render_chat(chat_history):
#     """Render the chat messages as a single panel for Live display."""
#     panels = []
#     for sender, message in chat_history:
#         if sender == "You":
#             panel = Panel(
#                 message, title=f"[green]{sender}[/green]", border_style="green", expand=False
#             )
#         else:
#             md = Markdown(message)
#             panel = Panel(
#                 md, title=f"[magenta]{sender}[/magenta]", border_style="magenta", expand=False
#             )
#         panels.append(panel)
#     return Align.center(Panel(Align.center("\n".join([str(p) for p in panels]), vertical="top"), border_style="blue"))

# def main():
#     console.print("[bold cyan]Welcome to Blonde CLI![/bold cyan]")
#     console.print("[dim]Type 'exit' to quit\n[/dim]")

#     chat_history = []

#     with Live(render_chat(chat_history), refresh_per_second=4, console=console) as live:
#         while True:
#             user_input = Prompt.ask("[bold green]You[/bold green]")
#             if user_input.lower() in ("exit", "quit"):
#                 console.print("[bold red]Goodbye![/bold red]")
#                 break

#             chat_history.append(("You", user_input))
#             live.update(render_chat(chat_history))

#             # Show a spinner while the bot is thinking
#             with console.status("[bold magenta]Blonde is typing...[/bold magenta]", spinner="dots"):
#                 try:
#                     response = bot.chat(user_input)
#                 except Exception as e:
#                     response = f"[bold red]Error:[/bold red] {e}"

#             chat_history.append(("Blonde", response))
#             live.update(render_chat(chat_history))

# if __name__ == "__main__":
#     main()





# Custom ASCII Logo for Blonde
# ASCII_LOGO = r"""
#  /$$$$$$$  /$$                           /$$          
# | $$__  $$| $$                          | $$          
# | $$  \ $$| $$  /$$$$$$  /$$$$$$$   /$$$$$$$  /$$$$$$ 
# | $$$$$$$ | $$ /$$__  $$| $$__  $$ /$$__  $$ /$$__  $$
# | $$__  $$| $$| $$  \ $$| $$  \ $$| $$  | $$| $$$$$$$$
# | $$  \ $$| $$| $$  | $$| $$  | $$| $$  | $$| $$_____/
# | $$$$$$$/| $$|  $$$$$$/| $$  | $$|  $$$$$$$|  $$$$$$$
# |_______/ |__/ \______/ |__/  |__/ \_______/ \_______/                                   
                                                      
# """

# ASCII_LOGO = r"""
#        ___           ___       ___           ___           ___           ___     
#      /\  \         /\__\     /\  \         /\__\         /\  \         /\  \    
#     /::\  \       /:/  /    /::\  \       /::|  |       /::\  \       /::\  \   
#    /:/\:\  \     /:/  /    /:/\:\  \     /:|:|  |      /:/\:\  \     /:/\:\  \  
#   /::\~\:\__\   /:/  /    /:/  \:\  \   /:/|:|  |__   /:/  \:\__\   /::\~\:\  \ 
#  /:/\:\ \:|__| /:/__/    /:/__/ \:\__\ /:/ |:| /\__\ /:/__/ \:|__| /:/\:\ \:\__\
#  \:\~\:\/:/  / \:\  \    \:\  \ /:/  / \/__|:|/:/  / \:\  \ /:/  / \:\~\:\ \/__/
#   \:\ \::/  /   \:\  \    \:\  /:/  /      |:/:/  /   \:\  /:/  /   \:\ \:\__\  
#    \:\/:/  /     \:\  \    \:\/:/  /       |::/  /     \:\/:/  /     \:\ \/__/  
#     \::/__/       \:\__\    \::/  /        /:/  /       \::/__/       \:\__\    
#      ~~            \/__/     \/__/         \/__/         ~~            \/__/                                                     
# """



# blonde_cli.py
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.align import Align
from rich.prompt import Prompt
from rich.layout import Layout
from rich.text import Text
from models.openrouter import OpenRouterAdapter
import time

console = Console()
bot = OpenRouterAdapter()

# Custom ASCII Logo for Blonde
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

[green]Commands:[/green]
 • Type any message to chat with Blonde
 • [bold]exit[/bold] or [bold]quit[/bold] to leave
 • [bold]help[/bold] to see this message again
"""

def animate_logo():
    console.clear()
    for line in ASCII_LOGO.splitlines():
        console.print(Text(line, style="bold magenta"), justify="center")
        time.sleep(0.05)
    console.print(Panel(Text("Welcome to Blonde CLI!", justify="center", style="bold cyan"),
                        border_style="blue", expand=False))
    time.sleep(1)
    console.clear()

def render_chat(chat_history):
    """Render chat messages as panels inside a single layout."""
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

def main():
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

            # Add user's message
            chat_history.append(("You", user_input))
            live.update(render_chat(chat_history))

            # Add temporary typing message
            chat_history.append(("Blonde", "[italic magenta]Blonde is typing...[/italic magenta]"))
            live.update(render_chat(chat_history))

            # Get bot response
            try:
                response = bot.chat(user_input)
            except Exception as e:
                response = f"[bold red]Error:[/bold red] {e}"

            # Replace typing message with real response
            chat_history[-1] = ("Blonde", response)
            live.update(render_chat(chat_history))

if __name__ == "__main__":
    main()
