import os
from pathlib import Path
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from tenacity import retry, stop_after_attempt, wait_fixed
from rich.console import Console

console = Console()

class LocalAdapter:
    def __init__(self, model_name="TheBloke/CodeLlama-7B-GGUF", model_file="codellama-7b.Q4_K_M.gguf", debug: bool = False):
        """Initialize GGUF model adapter.
        Args:
            model_name: Hugging Face model repo (e.g., TheBloke/CodeLlama-7B-GGUF).
            model_file: Specific GGUF file in repo (e.g., codellama-7b.Q4_K_M.gguf).
            debug: Enable debug logging.
        """
        self.model_name = model_name
        self.model_file = model_file
        self.debug = debug
        self.cache_dir = Path.home() / ".blonde" / "models"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self._download_model()
        self.llm = self._load_model()

    def _download_model(self) -> str:
        """Download GGUF model from Hugging Face if not cached.
        Returns:
            Path to cached model file.
        Raises:
            ValueError: If download fails.
        """
        try:
            console.print(f"[cyan]Checking for model {self.model_name}/{self.model_file}...[/cyan]")
            model_path = hf_hub_download(
                repo_id=self.model_name,
                filename=self.model_file,
                cache_dir=self.cache_dir,
                local_dir_use_symlinks=False
            )
            console.print(f"[green]Model cached at {model_path}[/green]")
            return model_path
        except Exception as e:
            console.print(f"[red]Failed to download model: {e}[/red]")
            raise ValueError(f"Model download failed: {e}")

    def _load_model(self) -> Llama:
        """Load GGUF model using llama-cpp-python.
        Returns:
            Llama instance for inference.
        Raises:
            ValueError: If model loading fails.
        """
        try:
            return Llama(
                model_path=str(self.model_path),
                n_ctx=2048,  # Context length
                n_threads=os.cpu_count() or 4,  # Use available CPU cores
                verbose=self.debug
            )
        except Exception as e:
            console.print(f"[red]Failed to load model: {e}[/red]")
            raise ValueError(f"Model loading failed: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def chat(self, prompt: str) -> str:
        """Generate response from GGUF model.
        Args:
            prompt: Input string.
        Returns:
            Generated text.
        Raises:
            ValueError: If inference fails.
        """
        try:
            output = self.llm(
                prompt,
                max_tokens=200,  # Limit output length
                temperature=0.7,
                stop=["</s>", "<|end|>"],  # Common stop tokens for GGUF
                echo=False  # Don't repeat prompt
            )
            response = output["choices"][0]["text"].strip()
            if self.debug:
                console.print(f"[yellow]Debug: Local model response: {response[:100]}...[/yellow]")
            return response
        except Exception as e:
            console.print(f"[red]Inference failed: {e}[/red]")
            raise ValueError(f"Inference failed: {e}")