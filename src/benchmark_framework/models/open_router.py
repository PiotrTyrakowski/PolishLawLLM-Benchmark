import os
from openai import OpenAI

from src.benchmark_framework.configs.runner_config import RunnerConfig
from src.benchmark_framework.models.base_model import BaseModel
from src.benchmark_framework.configs.model_config import ModelConfig


class OpenRouterModel(BaseModel):
    """
    OpenRouter language model implementation.

    Uses the OpenAI SDK with OpenRouter's API endpoint to access various LLM providers.
    Requires OPENROUTER_API_KEY environment variable to be set.
    """

    def __init__(self, model_name: str, model_config: ModelConfig, **kwargs):
        super().__init__(model_name, model_config, **kwargs)
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = "https://openrouter.ai/api/v1"
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable must be set")

        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def generate_response(self, system_prompt: str, prompt: str) -> str:
        """
        Generate a response from an OpenRouter model.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )

        return completion.choices[0].message.content

    def get_default_runner_config(self):
        """
        Returns default rate limiting configuration for OpenRouter models.
        """
        return RunnerConfig(requests_per_minute=50)
