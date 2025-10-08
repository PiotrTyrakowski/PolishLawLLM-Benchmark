import torch
from transformers import pipeline
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.constants import SYSTEM_PROMPT, MAX_NEW_TOKENS


class BielikModel(BaseModel):
    """
    Bielik language model implementation from Hugging Face.
    """

    def __init__(self, model_name: str, model_tools: str = None, **kwargs):
        super().__init__(model_name, model_tools, **kwargs)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = pipeline(
            task="text-generation", model=model_name, device=self.device
        )

    def generate_response(self, prompt: str) -> str:
        full_prompt = (
            "System: " + SYSTEM_PROMPT.strip() + "\n\n"
            "User: " + prompt.strip() + "\n\n"
            "Assistant:"
        )
        outputs = self.pipe(
            full_prompt,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            return_full_text=False,
        )
        response = outputs[0].get("generated_text")
        if response is None:
            return ""
        return response.strip()