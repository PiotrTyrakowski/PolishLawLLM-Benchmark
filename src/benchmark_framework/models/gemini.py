from google import genai
from google.genai import types

from src.benchmark_framework.configs.runner_config import RunnerConfig
from src.benchmark_framework.models.base_model import BaseModel
from src.benchmark_framework.configs.model_config import ModelConfig


class GeminiModel(BaseModel):
    """
    Google Gemini language model implementation.

    Uses the Google Generative AI SDK to interact with Gemini models.
    Requires GEMINI_API_KEY environment variable to be set.
    """

    def __init__(self, model_name: str, model_config: ModelConfig, **kwargs):
        # uses GEMINI_API_KEY env var
        super().__init__(model_name, model_config, **kwargs)
        self.client = genai.Client()

    def generate_response(self, system_prompt: str, prompt: str):
        resp = self.client.models.generate_content(
            model=self.model_name,
            config=self.create_generate_config(system_prompt),
            contents=prompt,
        )
        return resp.text

    def create_generate_config(self, system_prompt: str):
        if self.model_config.google_search:
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            config = types.GenerateContentConfig(
                system_instruction=system_prompt, tools=[grounding_tool]
            )
        else:
            config = types.GenerateContentConfig(system_instruction=system_prompt)
        return config

    def get_default_runner_config(self):
        return RunnerConfig(requests_per_minute=100)
