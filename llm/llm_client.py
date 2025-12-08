# Gemini wrapper
# llm/llm_client.py

import requests
import os
from config import LLM_MODEL, LLM_TEMPERATURE, GEMINI_API_KEY

class GeminiClient:
    def __init__(self, api_key: str = None, model: str = "gemini-2.0-flash", temperature: float = LLM_TEMPERATURE):
        self.api_key = api_key or GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        self.model = model
        self.temperature = temperature
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def generate(self, prompt: str) -> str:
        """
        Sends prompt to Gemini API and returns the text response
        """
        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": 2048,
                "candidateCount": 1
            }
        }

        response = requests.post(self.endpoint, headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"Gemini API error: {response.status_code}, {response.text}")

        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
