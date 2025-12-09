import os
from typing import Optional
from openai import OpenAI

from benchmark_framework.configs.runner_config import RunnerConfig
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.constants import MAX_NEW_TOKENS
from benchmark_framework.configs.model_config import ModelConfig


class NvidiaModel(BaseModel):
    """
    Model implementation via NVIDIA API.
    """

    def __init__(
        self, model_name: str, model_config: Optional[ModelConfig] = None, **kwargs
    ):
        super().__init__(model_name, model_config, **kwargs)
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise ValueError("NVIDIA_API_KEY environment variable must be set")
        self._api_key = api_key
        self._set_client()

    def _set_client(self):
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1", api_key=self._api_key
        )

    def generate_response(self, system_prompt: str, prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=MAX_NEW_TOKENS,
            extra_body=self.model_config.extra_body,
            stream=False,
        )
        return completion.choices[0].message.content

    def get_default_runner_config(self):
        return RunnerConfig(requests_per_minute=35)
