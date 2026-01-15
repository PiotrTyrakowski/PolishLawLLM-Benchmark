import os
import requests

from transformers import AutoTokenizer

from src.constants import MAX_NEW_TOKENS
from src.benchmark_framework.configs.runner_config import RunnerConfig
from src.benchmark_framework.models.base_model import BaseModel
from src.benchmark_framework.configs.model_config import ModelConfig


class HFEndpointModel(BaseModel):
    """
    Interacts with models hosted on Hugging Face Dedicated Inference Endpoints.

    Requires the following environment variables:
    - HF_TOKEN: Your Hugging Face access token.
    - HF_ENDPOINT_URL: The unique URL of your deployed endpoint.
    """

    def __init__(self, model_name: str, model_config: ModelConfig, **kwargs):
        super().__init__(model_name, model_config, **kwargs)

        self.api_key = os.getenv("HF_TOKEN")
        self.endpoint_url = os.getenv("HF_ENDPOINT_URL")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        if not self.api_key:
            raise ValueError("HF_TOKEN environment variable must be set")
        if not self.endpoint_url:
            raise ValueError("HF_ENDPOINT_URL environment variable must be set")

    def generate_response(self, system_prompt: str, prompt: str) -> str:
        """
        Generate a response from the HF Endpoint model using requests.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        full_input = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "inputs": full_input,
            "parameters": {
                "max_new_tokens": MAX_NEW_TOKENS,
                "return_full_text": False,
            },
        }

        response = requests.post(self.endpoint_url, headers=headers, json=payload)

        # Raise an error if the request failed (e.g., 400, 500)
        response.raise_for_status()
        output = response.json()

        print(f"HF Endpoint response: {response}")

        if (
            isinstance(output, list)
            and len(output) > 0
            and "generated_text" in output[0]
        ):
            return output[0]["generated_text"]
        elif isinstance(output, dict) and "generated_text" in output:
            return output["generated_text"]
        else:
            return str(output)

    def get_default_runner_config(self):
        """
        Returns default rate limiting for the dedicated endpoint.
        """
        return RunnerConfig()
