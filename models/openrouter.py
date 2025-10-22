# # In models/openrouter.py
# import os
# import requests
# import json
# from tenacity import retry, stop_after_attempt, wait_fixed

# class OpenRouterAdapter:
#     def __init__(self):
#         self.api_key = os.getenv("OPENROUTER_API_KEY")
#         if not self.api_key:
#             raise ValueError("OPENROUTER_API_KEY is not set")
#         self.api_url = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
#         self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")  # Configurable

#     @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
#     def chat(self, prompt: str) -> str:
#         """Sends prompt to OpenRouter API and returns response content.
#         Args:
#             prompt: User input string.
#         Returns:
#             Response text from the model.
#         Raises:
#             ValueError: If API response is invalid.
#             requests.HTTPError: If API call fails.
#         """
#         headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Content-Type": "application/json",
#         }
#         data = {
#             "model": self.model,
#             "messages": [{"role": "user", "content": prompt}],
#             "temperature": 0,
#         }

#         try:
#             response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
#             print(f"Status code: {response.status_code}")
#             print(f"Response preview: {response.text[:500]}")

#             if "text/html" in response.headers.get("Content-Type", ""):
#                 raise ValueError(f"Received HTML response. Check API key or model.\n{response.text[:500]}")
#             response.raise_for_status()

#             try:
#                 res_json = response.json()
#                 return res_json["choices"][0]["message"]["content"]
#             except json.JSONDecodeError:
#                 raise ValueError(f"Invalid JSON response:\n{response.text[:500]}")
#             except (KeyError, IndexError):
#                 raise ValueError(f"Unexpected response structure:\n{json.dumps(res_json, indent=2)}")
#         except requests.RequestException as e:
#             print(f"API request failed: {e}")
#             raise


# In models/openrouter.py
import os
import requests
import json
from tenacity import retry, stop_after_attempt, wait_fixed
from cli import load_api_key
from utils import setup_logging

class OpenRouterAdapter:
    def __init__(self, debug: bool = False):
        self.logger = setup_logging(debug)
        # self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_key = os.getenv("OPENROUTER_API_KEY") or load_api_key("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")
        self.api_url = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def chat(self, prompt: str) -> str:
        """Sends prompt to OpenRouter API and returns response content.
        Args:
            prompt: User input string.
        Returns:
            Response text from the model.
        Raises:
            ValueError: If API response is invalid.
            requests.HTTPError: If API call fails.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
            self.logger.debug(f"Status code: {response.status_code}")
            self.logger.debug(f"Response preview: {response.text[:500]}")

            if "text/html" in response.headers.get("Content-Type", ""):
                raise ValueError(f"Received HTML response. Check API key or model.")
            response.raise_for_status()

            try:
                res_json = response.json()
                return res_json["choices"][0]["message"]["content"]
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON response")
            except (KeyError, IndexError):
                raise ValueError(f"Unexpected response structure")
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise