"""AI tutor service using fine-tuned Qwen2.5-1.5B model."""

import os
from pathlib import Path
from typing import Optional

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

from config import PROCESSED_DIR

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# Lazy-loaded model
_model_cache = None


def _load_model():
    """Load Qwen LoRA model (cached)."""
    global _model_cache
    if _model_cache is not None:
        return _model_cache

    model_dir = MODELS_DIR / "tutor"
    if not model_dir.exists():
        raise FileNotFoundError(f"Tutor model not found: {model_dir}. Run training first.")

    # 4-bit quantization requires CUDA
    if not torch.cuda.is_available():
        raise RuntimeError("Tutor model requires CUDA (GPU) for 4-bit quantization inference.")

    base_model_name = "Qwen/Qwen2.5-1.5B-Instruct"

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir), trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load base model with 4bit quantization
    from transformers import BitsAndBytesConfig
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        quantization_config=bnb_config,
        trust_remote_code=True,
        device_map="auto",
    )

    # Load LoRA adapter
    model = PeftModel.from_pretrained(base_model, str(model_dir))
    model.eval()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    _model_cache = {
        "tokenizer": tokenizer,
        "model": model,
        "device": device,
    }
    return _model_cache


def chat(
    question: str,
    system_prompt: Optional[str] = None,
    max_new_tokens: int = 512,
    temperature: float = 0.7,
) -> dict:
    """Generate AI tutor response.

    Args:
        question: Student's question
        system_prompt: Optional custom system prompt
        max_new_tokens: Maximum tokens to generate
        temperature: Sampling temperature

    Returns:
        Response dict with answer and metadata
    """
    cache = _load_model()
    tokenizer = cache["tokenizer"]
    model = cache["model"]

    if system_prompt is None:
        system_prompt = (
            "You are a helpful AI tutor specialized in machine learning, "
            "deep learning, and data science. Answer questions clearly and concisely."
        )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    # Apply chat template
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            top_p=0.9,
            pad_token_id=tokenizer.pad_token_id,
        )

    # Decode only the new tokens
    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )

    return {
        "question": question,
        "answer": response.strip(),
        "model": "Qwen2.5-1.5B-Instruct (LoRA)",
        "tokens_generated": outputs.shape[1] - inputs["input_ids"].shape[1],
    }


def get_model_info() -> dict:
    """Get tutor model info."""
    cache = _load_model()
    return {
        "model_type": "Qwen2.5-1.5B-Instruct (LoRA fine-tuned)",
        "device": str(cache["device"]),
        "training_data": "StudyChat (4,073 samples)",
    }
