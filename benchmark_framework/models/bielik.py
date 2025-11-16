import os
from openai import OpenAI
from benchmark_framework.configs.runner_config import RunnerConfig
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.constants import SYSTEM_PROMPT, MAX_NEW_TOKENS
from benchmark_framework.configs.model_config import ModelConfig


class BielikModel(BaseModel):
    """
    Bielik language model implementation via NVIDIA API.
    Uses the OpenAI SDK to interact with the Bielik model hosted on NVIDIA's platform.
    Requires NVIDIA_API_KEY environment variable to be set.
    """

    def __init__(self, model_name: str, model_config: ModelConfig, **kwargs):
        super().__init__(model_name, model_config, **kwargs)
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise ValueError("NVIDIA_API_KEY environment variable must be set")

        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1", api_key=api_key
        )

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the Bielik model.
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        completion = self.client.chat.completions.create(
            model="speakleash/bielik-11b-v2.6-instruct",
            messages=messages,
            max_tokens=MAX_NEW_TOKENS,
        )

        return completion.choices[0].message.content

    def get_default_runner_config(self):
        """
        Returns default rate limiting configuration for the Bielik model.
        Adjust these values based on NVIDIA API limits.
        """
        return RunnerConfig(requests_per_minute=30)
