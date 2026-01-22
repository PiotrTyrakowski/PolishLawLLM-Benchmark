import os
from mistralai import Mistral

from src.benchmark_framework.configs.runner_config import RunnerConfig
from src.benchmark_framework.models.base_model import BaseModel
from src.benchmark_framework.configs.model_config import ModelConfig


class MistralModel(BaseModel):
    """
    Mistral language model implementation.
    """

    def __init__(self, model_name: str, model_config: ModelConfig, **kwargs):
        super().__init__(model_name, model_config, **kwargs)
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY environment variable must be set")

        self.client = Mistral(api_key=api_key)

    def generate_response(self, system_prompt: str, prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        chat_response = self.client.chat.complete(
            model=self.model_name,
            messages=messages,
        )

        return chat_response.choices[0].message.content

    def get_default_runner_config(self):
        return RunnerConfig(requests_per_minute=60)
