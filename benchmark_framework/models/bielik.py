import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.constants import SYSTEM_PROMPT


class BielikModel(BaseModel):
    """
    Bielik language model implementation from Hugging Face.
    """

    def __init__(self, model_name: str, model_tools: str = None, **kwargs):
        super().__init__(model_name, model_tools, **kwargs)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, low_cpu_mem_usage=True, device_map="auto"
        )

    def generate_response(self, prompt: str) -> str:
        full_prompt = SYSTEM_PROMPT + "\n\nUser: " + prompt + "\nAssistant:"

        inputs = self.tokenizer(full_prompt, return_tensors="pt", truncation=True)
        model_device = next(self.model.parameters()).device

        input_ids = inputs["input_ids"].to(model_device)
        attention_mask = inputs.get("attention_mask")
        if attention_mask is not None:
            attention_mask = attention_mask.to(model_device)

        input_len = input_ids.shape[1]

        outputs = self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            do_sample=False,
            eos_token_id=(
                self.tokenizer.eos_token_id
                if self.tokenizer.eos_token_id is not None
                else self.tokenizer.pad_token_id
            ),
            pad_token_id=(
                self.tokenizer.pad_token_id
                if self.tokenizer.pad_token_id is not None
                else self.tokenizer.eos_token_id
            ),
        )

        if outputs.shape[1] > input_len:
            generated_tokens = outputs[0, input_len:]
            response = self.tokenizer.decode(
                generated_tokens, skip_special_tokens=True
            ).strip()
        else:
            response = self.tokenizer.decode(
                outputs[0], skip_special_tokens=True
            ).strip()

        return response
