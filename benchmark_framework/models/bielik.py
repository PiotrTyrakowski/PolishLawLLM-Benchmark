import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.constants import SYSTEM_PROMPT


class BielikModel(BaseModel):
    """
    Bielik language model implementation from Hugging Face.
    """

    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_name, **kwargs)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
            device_map="auto",
        )

    def generate_response(self, prompt: str) -> str:
        """
        Generate an answer for the given prompt using the Bielik model.
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        inputs = self.tokenizer.apply_chat_template(
            messages, return_tensors="pt", return_attention_mask=True, return_dict=True
        )
        input_ids = inputs["input_ids"].to(self.device)
        input_len = input_ids.shape[1]

        attention_mask = inputs["attention_mask"].to(self.device)
        outputs = self.model.generate(
            input_ids=input_ids, attention_mask=attention_mask, max_new_tokens=1000
        )
        generated_tokens = outputs[0, input_len:]
        response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

        return response
