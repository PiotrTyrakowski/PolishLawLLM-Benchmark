import os
from openai import OpenAI

from src.benchmark_framework.configs.runner_config import RunnerConfig
from src.benchmark_framework.models.base_model import BaseModel
from src.benchmark_framework.configs.model_config import ModelConfig

MODEL_PROVIDER_DICT = {
    "meta-llama/llama-3.3-70b-instruct": {
        "order": ["novita/bf16"],
        "allow_fallbacks": False,
    },
    "meta-llama/llama-3.1-405b-instruct": {
        "order": ["together/fp8"],
        "allow_fallbacks": False,
    },
    "meta-llama/llama-4-maverick": {"quantizations": ["fp8"], "allow_fallbacks": False},
    "deepseek/deepseek-v3.2": {"quantizations": ["fp8"], "allow_fallbacks": False},
    "google/gemma-3-12b-it": {"order": ["deepinfra/bf16"], "allow_fallbacks": False},
    "mistralai/mistral-nemo": {"order": ["deepinfra/fp8"], "allow_fallbacks": False},
}


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
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        request_kwargs = {
            "model": self.model_name,
            "messages": messages,
        }

        # Only add extra_body if the model is defined in the provider dict
        if self.model_name in MODEL_PROVIDER_DICT:
            request_kwargs["extra_body"] = {
                "provider": MODEL_PROVIDER_DICT[self.model_name]
            }

        completion = self.client.chat.completions.create(**request_kwargs)

        return completion.choices[0].message.content

    def get_default_runner_config(self):
        return RunnerConfig()
