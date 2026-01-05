from src.benchmark_framework.models.base_model import BaseModel
from src.benchmark_framework.configs.model_config import ModelConfig
from src.constants import MAX_NEW_TOKENS


class LocalModel(BaseModel):
    """
    Local model utilizing the pipeline interface for text-generation task implementation from Hugging Face.
    """

    def __init__(
        self, model_name: str, model_config: ModelConfig, quantize: str = None, **kwargs
    ):
        super().__init__(model_name, model_config, **kwargs)

        # Lazy imports - only import when LocalModel is actually used
        import torch
        from transformers import pipeline, BitsAndBytesConfig

        quantization_config = None
        if quantize == "4bit":
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16
            )
        elif quantize == "8bit":
            quantization_config = BitsAndBytesConfig(load_in_8bit=True)

        self.pipe = pipeline(
            task="text-generation",
            model=model_name,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            quantization_config=quantization_config,
        )

    def generate_response(self, system_prompt: str, prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": prompt.strip()},
        ]
        outputs = self.pipe(
            messages,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            return_full_text=False,
        )

        response = outputs[0].get("generated_text")
        if response is None:
            return ""

        assert isinstance(response, str), "generated_text should be of type str"
        return response

    def generate_batch_response(
        self, system_prompt: str, prompts: list[str], batch_size: int
    ) -> list[str]:
        chat_batch = []
        for prompt in prompts:
            messages = [
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": prompt.strip()},
            ]
            chat_batch.append(messages)

        outputs = self.pipe(
            chat_batch,
            batch_size=batch_size,
            return_full_text=False,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
        )

        responses = [output[0]["generated_text"].strip() for output in outputs]
        return responses
