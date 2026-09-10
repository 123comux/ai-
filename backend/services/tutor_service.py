"""AI tutor service using fine-tuned Qwen2.5-1.5B model."""

import os
import re
from pathlib import Path
from typing import Optional

from config import PROCESSED_DIR, AI_HTTP_TIMEOUT

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# Lazy-loaded model
_model_cache = None


def _load_model():
    """Load Qwen LoRA model (cached). torch/transformers/peft 惰性导入，避免拖慢启动。"""
    global torch, AutoTokenizer, AutoModelForCausalLM, PeftModel, _model_cache
    if _model_cache is not None:
        return _model_cache

    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel

    model_dir = MODELS_DIR / "tutor"
    if not model_dir.exists():
        raise FileNotFoundError(f"Tutor model not found: {model_dir}. Run training first.")

    # Requires CUDA GPU
    if not torch.cuda.is_available():
        raise RuntimeError("Tutor model requires CUDA (GPU).")

    base_model_name = "Qwen/Qwen2.5-1.5B-Instruct"

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir), trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load base model in float16 (faster inference than 4-bit on RTX 4060)
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        trust_remote_code=True,
        device_map="auto",
    )

    # Load LoRA adapter and merge
    model = PeftModel.from_pretrained(base_model, str(model_dir))
    model = model.merge_and_unload()
    model.eval()

    device = torch.device("cuda")

    _model_cache = {
        "tokenizer": tokenizer,
        "model": model,
        "device": device,
    }
    return _model_cache


def _cleanup_response(text: str) -> str:
    """Post-process model output: remove redundancy, collapse whitespace, strip Markdown decoration."""
    if not text:
        return text

    # 1) Remove Markdown heading/emphasis markers (##, **, __, >) but keep content
    text = re.sub(r"^\s*#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)

    # 2) Standardize list markers: keep "1. 2. 3." and "- " only, collapse others
    #    Replace bullets such as •/·/★ with "- "
    text = re.sub(r"^\s*[•·●○★▪▫➢➤➔▶→]\s*", "- ", text, flags=re.MULTILINE)

    # 3) Collapse blank lines (3+ newlines -> 2) and trim trailing spaces per line
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

    # 4) Merge repeated punctuation (。。。->。, ？？？->？, ，，，->，)
    text = re.sub(r"([，。！？；：,.!?;:])\1{2,}", r"\1", text)

    # 5) Merge duplicate consecutive short sentences (within 30 chars, repeat exactly)
    seen = set()
    out_lines = []
    for line in text.splitlines():
        key = line.strip()
        if len(key) <= 30 and key in seen:
            continue
        if key:
            seen.add(key)
        out_lines.append(line)
    text = "\n".join(out_lines)

    return text.strip()


def chat(
    question: str,
    system_prompt: Optional[str] = None,
    max_new_tokens: int = 220,
    temperature: float = 0.0,
) -> dict:
    """Generate concise AI tutor response.

    Preferred path: Zhipu GLM API (cloud) with course-RAG context.
    Fallback: local Qwen LoRA model (requires GPU).

    Args:
        question: Student's question
        system_prompt: Optional custom system prompt
        max_new_tokens: Maximum tokens to generate
        temperature: Sampling temperature

    Returns:
        Response dict with answer and metadata
    """
    if system_prompt is None:
        system_prompt = (
            "你是一位 AI 学习导师，请用中文直接作答。"
            "只保留核心要点，去掉铺垫、重复和客套。"
            "分点回答时仅使用 1. 2. 3.，不要 Markdown 符号。"
            "控制在 4 行以内，每点一句话结论。"
        )

    # 1. 优先走智谱 GLM API（若配置了 key）
    try:
        from config import ZHIPU_API_KEY
        if ZHIPU_API_KEY:
            return _chat_zhipu(question, system_prompt, max_new_tokens, temperature)
    except Exception:
        pass

    # 2. 回退：本地 Qwen LoRA 模型
    return _chat_local(question, system_prompt, max_new_tokens, temperature)


def _chat_zhipu(question, system_prompt, max_new_tokens, temperature) -> dict:
    """Call Zhipu GLM API with course-RAG context."""
    import requests
    from config import ZHIPU_API_KEY, ZHIPU_API_URL

    # 检索课程知识库，把相关内容拼入上下文
    context = ""
    try:
        from services.knowledge_base import retrieve_context
        context = retrieve_context(question, k=4)
    except Exception:
        context = ""

    messages = [{"role": "system", "content": system_prompt}]
    if context:
        messages.append({
            "role": "system",
            "content": "以下是从课程资料中检索到的相关知识，回答时优先参考：\n" + context,
        })
    messages.append({"role": "user", "content": question})

    resp = requests.post(
        ZHIPU_API_URL,
        headers={"Authorization": f"Bearer {ZHIPU_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "glm-4-flash",
            "messages": messages,
            "max_tokens": max_new_tokens,
            "temperature": temperature,
        },
        timeout=AI_HTTP_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    answer = data["choices"][0]["message"]["content"]

    return {
        "question": question,
        "answer": _cleanup_response(answer),
        "model": "glm-4-flash (Zhipu)",
        "tokens_generated": data.get("usage", {}).get("total_tokens", 0),
    }


def _chat_local(question, system_prompt, max_new_tokens, temperature) -> dict:
    """Fallback: local Qwen LoRA model."""
    cache = _load_model()
    tokenizer = cache["tokenizer"]
    model = cache["model"]

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

    # Generate (concise: greedy + repeat penalty + hard stop)
    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=0.0,
            repetition_penalty=1.15,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            use_cache=True,
            num_beams=1,
        )

    # Decode only the new tokens
    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )

    response = _cleanup_response(response)

    return {
        "question": question,
        "answer": response,
        "model": "Qwen2.5-1.5B-Instruct (LoRA)",
        "tokens_generated": outputs.shape[1] - inputs["input_ids"].shape[1],
    }


def get_model_info() -> dict:
    """Report tutor model availability WITHOUT loading the model (fast)."""
    model_dir = MODELS_DIR / "tutor"
    if not model_dir.exists() or not any(model_dir.iterdir()):
        return {"status": "not available", "reason": "model not found"}
    return {
        "status": "available",
        "model_type": "Qwen2.5-1.5B-Instruct (LoRA fine-tuned)",
        "device": "cuda" if __import__("torch").cuda.is_available() else "cpu",
        "training_data": "StudyChat (4,073 samples)",
    }


def warm_up() -> bool:
    """后台预热：加载模型进缓存，失败静默返回 False（供启动线程调用，不阻塞启动）。"""
    try:
        _load_model()
        return True
    except Exception:
        return False
