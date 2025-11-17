import os
from openai import OpenAI
from benchmark_framework.configs.runner_config import RunnerConfig
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.constants import SYSTEM_PROMPT, MAX_NEW_TOKENS
from benchmark_framework.configs.model_config import ModelConfig
from typing import Generator, Union


class DeepseekModel(BaseModel):
    """
    Deepseek language model implementation via NVIDIA API.
    """

    MODEL_NAME = "deepseek-ai/deepseek-v3.1-terminus"

    def __init__(
        self, model_name: str = MODEL_NAME, model_config: ModelConfig = None, **kwargs
    ):
        super().__init__(model_name, model_config, **kwargs)
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise ValueError("NVIDIA_API_KEY environment variable must be set")
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1", api_key=api_key
        )

    def generate_response(self, prompt: str) -> Union[str, Generator[str, None, None]]:
        """
        Generate a response from the Deepseek model.
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        completion = self.client.chat.completions.create(
            model="deepseek-ai/deepseek-v3.1-terminus",
            messages=messages,
            max_tokens=MAX_NEW_TOKENS,
            extra_body={"chat_template_kwargs": {"thinking": False}},
            stream=False,
        )

        return completion.choices[0].message.content

    def get_default_runner_config(self):
        return RunnerConfig(requests_per_minute=30)
