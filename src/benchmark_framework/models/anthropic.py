import os
import anthropic

from src.benchmark_framework.configs.runner_config import RunnerConfig
from src.benchmark_framework.models.base_model import BaseModel
from src.benchmark_framework.configs.model_config import ModelConfig
from src.constants import MAX_NEW_TOKENS


class AnthropicModel(BaseModel):
    """
    Anthropic Claude language model implementation.

    Uses the Anthropic SDK to interact with Claude models.
    Requires ANTHROPIC_API_KEY environment variable to be set.
    """

    def __init__(self, model_name: str, model_config: ModelConfig, **kwargs):
        super().__init__(model_name, model_config, **kwargs)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable must be set")

        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_response(self, system_prompt: str, prompt: str) -> str:
        message = self.client.messages.create(
            model=self.model_name,
            system=system_prompt,
            max_tokens=MAX_NEW_TOKENS,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )

        return message.content[0].text

    def get_default_runner_config(self):
        return RunnerConfig(requests_per_minute=50)
