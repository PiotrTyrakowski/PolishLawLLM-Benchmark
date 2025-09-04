from google import genai
from google.genai import types

from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.constants import SYSTEM_PROMPT

class GeminiModel(BaseModel):
    def __init__(self, model_name: str, **kwargs):
        # uses GEMINI_API_KEY env var
        super().__init__(model_name, **kwargs)
        self.client = genai.Client()

    def generate_response(self, prompt: str):
        """
        Generate an answer for a multiple-choice question.

        Args:
            prompt: The question prompt (with question and choices).

        Returns:
            A string containing the model’s response.
        """
        resp = self.client.models.generate_content(
            model=self.model_name,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            contents=prompt,
        )
        
        return resp.text
