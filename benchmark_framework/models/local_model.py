from transformers import pipeline
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.constants import SYSTEM_PROMPT, MAX_NEW_TOKENS


class LocalModel(BaseModel):
    """
    Local model utilizing the pipeline interface for text-generation task implementation from Hugging Face.
    """

    def __init__(self, model_name: str, model_tools: str = None, **kwargs):
        super().__init__(model_name, model_tools, **kwargs)
        self.pipe = pipeline(
            task="text-generation", model=model_name, device_map="auto"
        )

    def generate_response(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
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

        print(f"DEBUG: {response}")

        assert len(response) == 3
        assert response[2].get("role") == "assistant"
        assert response[2].get("content") is not None

        return response[2].get("content").strip()
