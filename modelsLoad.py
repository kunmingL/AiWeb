import bitsandbytes
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch


def modlesload(model_name):
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        load_in_8bit_fp32_cpu_offload=True
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        torch_dtype="auto",
        device_map="auto",
        trust_remote_code=True
    )
    return model

def tokenizerload(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return tokenizer