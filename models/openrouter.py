# models/openrouter.py
import os
import requests
import json

class OpenRouterAdapter:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")
        
        # Ensure the endpoint points directly to chat/completions
        self.api_url = os.getenv(
            "OPENROUTER_API_URL", 
            "https://openrouter.ai/api/v1/chat/completions"
        )
        
        self.model = "openai/gpt-oss-20b:free"

    def chat(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        }

        response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
        print("Status code:", response.status_code)
        print("Response preview:", response.text[:500])

        # Check for HTML response (common if API key/model is wrong)
        if "text/html" in response.headers.get("Content-Type", ""):
            raise ValueError(f"Received HTML response. Check your API key or model.\n{response.text[:500]}")

        response.raise_for_status()

        try:
            res_json = response.json()
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response from OpenRouter:\n{response.text[:500]}")

        # Safely extract the chat content
        try:
            return res_json["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise ValueError(f"Unexpected response structure:\n{json.dumps(res_json, indent=2)}")


