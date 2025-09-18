# cli.py
import typer
from models.openai import OpenAIAdapter
from models.hf import HFAdapter
from models.openrouter import OpenRouterAdapter

app = typer.Typer()

# pick your default model here
# model = OpenAIAdapter()
model = OpenRouterAdapter()


@app.command()
def gen(prompt: str):
    """Generate code from natural language prompt"""
    print(model.chat(prompt))

@app.command()
def fix(file: str):
    """Suggest fixes for a given Python file"""
    with open(file, "r") as f:
        code = f.read()
    prompt = f"Fix bugs in this Python code:\n{code}"
    print(model.chat(prompt))

@app.command()
def doc(file: str):
    """Generate documentation for a Python file"""
    with open(file, "r") as f:
        code = f.read()
    prompt = f"Explain this code in plain English:\n{code}"
    print(model.chat(prompt))

if __name__ == "__main__":
    app()
