# models/openai.py
import os
from openai import OpenAI

class OpenAIAdapter:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def chat(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            # model="openai/gpt-oss-20b:free",
            model="openai/gpt-oss-120b:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        # return response.choices[0].message.content
        return response["choices"][0]["message"]["content"]

