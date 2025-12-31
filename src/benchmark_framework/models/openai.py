import os
from openai import OpenAI

from src.benchmark_framework.configs.runner_config import RunnerConfig
from src.benchmark_framework.models.base_model import BaseModel
from src.benchmark_framework.configs.model_config import ModelConfig


class OpenAIModel(BaseModel):
    """
    OpenAI language model implementation.

    Uses the OpenAI SDK to interact with OpenAI models (GPT-4, GPT-3.5, etc.).
    Requires OPENAI_API_KEY environment variable to be set.
    """

    def __init__(self, model_name: str, model_config: ModelConfig, **kwargs):
        super().__init__(model_name, model_config, **kwargs)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")

        self.client = OpenAI(api_key=api_key)

    def generate_response(self, system_prompt: str, prompt: str) -> str:
        """
        Generate a response from an OpenAI model.
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
        Returns default rate limiting configuration for OpenAI models.
         """
        return RunnerConfig(requests_per_minute=50)
