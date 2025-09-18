# # models/openrouter.py
# import os
# from openai import OpenAI

# class OpenRouterAdapter:
#     def __init__(self):
#         self.client = OpenAI(
#             api_key=os.getenv("OPENROUTER_API_KEY"),  # your OpenRouter key
#             base_url=os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1")  # optional default
#         )

#     def chat(self, prompt: str) -> str:
#         response = self.client.chat.completions.create(
#             model=os.getenv("openai/gpt-oss-120b:free", "mistral-7b-chat"),  # choose your OpenRouter model
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0
#         )
#         return response.choices[0].message.content


# models/openrouter.py
import os
import requests
import json

class OpenRouterAdapter:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1")
        # self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b:free")
        self.model = "openai/gpt-oss-20b:free"
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")

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
        print("Response text:", response.text[:500])  
        response.raise_for_status()
        try:
            res_json = response.json()
        except json.JSONDecodeError:
            raise ValueError(f"Invalid response from OpenRouter:\n{response.text}")
        return res_json["choices"][0]["message"]["content"]
