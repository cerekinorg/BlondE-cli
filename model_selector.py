"""
Interactive Model Selector for BlondE-CLI
Allows users to select from cached models or download new ones
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

console = Console()

# Recommended GGUF models with metadata
AVAILABLE_MODELS = {
    "1": {
        "name": "CodeLlama-7B",
        "repo": "TheBloke/CodeLlama-7B-GGUF",
        "file": "codellama-7b.Q4_K_M.gguf",
        "size": "3.8GB",
        "description": "Best for code generation, bug fixing, and coding tasks",
        "recommended": True
    },
    "2": {
        "name": "Mistral-7B-Instruct",
        "repo": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
        "file": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "size": "4.1GB",
        "description": "Fast general-purpose model, great for chat and code"
    },
    "3": {
        "name": "DeepSeek-Coder-6.7B",
        "repo": "TheBloke/deepseek-coder-6.7b-instruct-GGUF",
        "file": "deepseek-coder-6.7b-instruct.Q4_K_M.gguf",
        "size": "3.8GB",
        "description": "Specialized for advanced coding tasks"
    },
    "4": {
        "name": "Llama-2-7B-Chat",
        "repo": "TheBloke/Llama-2-7B-Chat-GGUF",
        "file": "llama-2-7b-chat.Q4_K_M.gguf",
        "size": "3.8GB",
        "description": "Optimized for conversational tasks"
    },
    "5": {
        "name": "Phi-2",
        "repo": "TheBloke/phi-2-GGUF",
        "file": "phi-2.Q4_K_M.gguf",
        "size": "1.6GB",
        "description": "Smaller, faster model - good for quick tasks"
    }
}


def get_cache_dir() -> Path:
    """Get the model cache directory."""
    cache_dir = Path.home() / ".blonde" / "models"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def find_cached_models() -> List[Dict[str, str]]:
    """Find all GGUF models in cache directory."""
    cache_dir = get_cache_dir()
    cached = []
    
    if cache_dir.exists():
        for model_file in cache_dir.rglob("*.gguf"):
            size_mb = model_file.stat().st_size / (1024 * 1024)
            
            # Extract repo name from HuggingFace cache structure
            # Structure: models--{OWNER}--{NAME}/snapshots/{HASH}/{FILE}
            repo_name = "Unknown"
            try:
                # Walk up to find the models-- directory
                parts = model_file.parts
                for i, part in enumerate(parts):
                    if part.startswith("models--"):
                        # Convert models--TheBloke--phi-2-GGUF to TheBloke/phi-2-GGUF
                        repo_name = part.replace("models--", "").replace("--", "/", 1)
                        break
            except Exception:
                repo_name = "Unknown"
            
            cached.append({
                "file": model_file.name,
                "path": str(model_file),
                "size": f"{size_mb:.1f}MB",
                "repo": repo_name
            })
    
    return cached


def display_cached_models(cached_models: List[Dict[str, str]]) -> None:
    """Display cached models in a table."""
    if not cached_models:
        console.print("[yellow]No cached models found.[/yellow]")
        return
    
    table = Table(title="📦 Cached Local Models", show_header=True, header_style="bold cyan")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Model File", style="green")
    table.add_column("Size", style="yellow", justify="right")
    table.add_column("Repository", style="dim")
    
    for idx, model in enumerate(cached_models, 1):
        table.add_row(
            str(idx),
            model["file"],
            model["size"],
            model["repo"]
        )
    
    console.print(table)


def display_downloadable_models() -> None:
    """Display available models to download."""
    table = Table(title="🌐 Available Models to Download", show_header=True, header_style="bold magenta")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Model", style="green")
    table.add_column("Size", style="yellow", justify="right")
    table.add_column("Description", style="white")
    
    for key, model in AVAILABLE_MODELS.items():
        name = model["name"]
        if model.get("recommended"):
            name += " ⭐"
        table.add_row(
            key,
            name,
            model["size"],
            model["description"]
        )
    
    console.print(table)


def select_model() -> Optional[tuple]:
    """
    Interactive model selection.
    
    Returns:
        Tuple of (model_repo, model_file, is_cached, cache_path) or None if cancelled
    """
    # Don't clear screen - keep previous messages visible
    console.print()
    console.print(Panel(
        Text("🤖 BlondE-CLI Local Model Selector", justify="center", style="bold cyan"),
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print()
    
    # Check for cached models
    cached_models = find_cached_models()
    
    if cached_models:
        display_cached_models(cached_models)
        console.print()
        console.print("[bold green]✓ You have cached models ready to use![/bold green]")
        console.print()
        
        # Ask if user wants to use cached or download new
        choice = Prompt.ask(
            "[cyan]Choose an option[/cyan]",
            choices=["use", "download", "cancel"],
            default="use"
        )
        
        if choice == "cancel":
            console.print("[yellow]Cancelled.[/yellow]")
            return None
        
        if choice == "use":
            # Let user select cached model
            model_num = Prompt.ask(
                f"[cyan]Select cached model[/cyan] [dim](1-{len(cached_models)})[/dim]",
                default="1"
            )
            
            try:
                idx = int(model_num) - 1
                if 0 <= idx < len(cached_models):
                    selected = cached_models[idx]
                    console.print(f"\n[green]✓ Using: {selected['file']}[/green]")
                    return (selected["repo"], selected["file"], True, selected["path"])
                else:
                    console.print("[red]Invalid selection.[/red]")
                    return None
            except ValueError:
                console.print("[red]Invalid input.[/red]")
                return None
    else:
        console.print("[yellow]No cached models found.[/yellow]")
        console.print()
    
    # Show downloadable models
    display_downloadable_models()
    console.print()
    
    # Show recommendation but always let user choose
    if not cached_models:
        console.print("[bold cyan]💡 Recommended for first-time users: CodeLlama-7B (Option 1)[/bold cyan]")
        console.print()
    
    # Let user select from downloadable models (always show menu)
    model_choice = Prompt.ask(
        "[cyan]Select model to download[/cyan] [dim](1-5 or 'cancel')[/dim]",
        default="1"
    )
    
    if model_choice.lower() == "cancel":
        console.print("[yellow]Cancelled.[/yellow]")
        return None
    
    if model_choice in AVAILABLE_MODELS:
        model = AVAILABLE_MODELS[model_choice]
        console.print(f"\n[green]✓ Selected: {model['name']} ({model['size']})[/green]")
        console.print(f"[dim]{model['description']}[/dim]")
        console.print()
        console.print("[cyan]Model will download on first use (5-10 minutes, one-time only)[/cyan]")
        console.print()
        return (model["repo"], model["file"], False, None)
    else:
        console.print("[red]Invalid selection.[/red]")
        return None


if __name__ == "__main__":
    # Test the selector
    result = select_model()
    if result:
        repo, file, is_cached, path = result
        console.print(f"\n[green]Selected:[/green]")
        console.print(f"  Repo: {repo}")
        console.print(f"  File: {file}")
        console.print(f"  Cached: {is_cached}")
        if path:
            console.print(f"  Path: {path}")
