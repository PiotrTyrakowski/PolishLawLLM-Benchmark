from google import genai
from google.genai import types

from benchmark_framework.models.base import BaseModel
from benchmark_framework.constants import CONFIG_PROMPT

class GeminiModel(BaseModel):
    def __init__(self, **kwargs):
        # uses GEMINI_API_KEY env var
        super().__init__(**kwargs)
        self.client = genai.Client()

    def generate_answer(self, question, choices):
        resp = self.client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(system_instruction=CONFIG_PROMPT),
            contents=question,
        )
        return resp.text
