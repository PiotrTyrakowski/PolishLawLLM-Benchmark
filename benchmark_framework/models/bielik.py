import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.constants import SYSTEM_PROMPT


class BielikModel(BaseModel):
    """
    Bielik language model implementation from Hugging Face.

    This class handles loading the model and tokenizer, and then
    uses them to generate responses for given prompts.
    """
    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_name, **kwargs)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        # TODO: validate the options here
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
            device_map="auto"
        ).to(self.device)

    def generate_response(self, prompt: str) -> str:
        """
        Generate an answer for a multiple-choice question using the Bielik model.

        Args:
            prompt: The question prompt (with question and choices).

        Returns:
            A string containing the model’s response.
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        input_ids = self.tokenizer.apply_chat_template(
            messages,
            return_tensors="pt"
        ).to(self.device)

        # TODO: test do_sample option
        outputs = self.model.generate(input_ids, max_new_tokens=1000)
        response_ids = outputs[0][input_ids.shape[-1]:]
        response = self.tokenizer.decode(response_ids, skip_special_tokens=True)
        print(response)

        decoded = self.tokenizer.batch_decode(outputs)
        print(decoded)

        return response.strip()