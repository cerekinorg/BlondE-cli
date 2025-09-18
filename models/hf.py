# models/hf.py
import os
import requests

class HFAdapter:
    def __init__(self, model_name="bigcode/starcoderbase"):
        self.model_name = model_name
        self.api_key = os.getenv("HF_TOKEN")
        if not self.api_key:
            raise ValueError("Set HF_TOKEN environment variable")
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def chat(self, prompt: str) -> str:
        payload = {"inputs": prompt}
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        return response.json()[0]["generated_text"]
