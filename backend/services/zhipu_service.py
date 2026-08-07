"""Zhipu GLM chat service — pure requests, no torch/transformers import.

Importing this module is fast; it never triggers heavy model loading.
Used by the AI tutor as the primary path (with course-RAG context).
"""

import requests

from config import ZHIPU_API_KEY, ZHIPU_API_URL


def chat_zhipu(
    question: str,
    system_prompt: str,
    max_new_tokens: int = 220,
    temperature: float = 0.0,
) -> dict:
    """Call Zhipu GLM API, optionally with course-RAG context."""
    if not ZHIPU_API_KEY:
        raise RuntimeError("ZHIPU_API_KEY not configured")

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
            "content": (
                "以下是课程资料中检索到的相关知识，回答时必须优先、准确地使用这些资料：\n\n"
                + context
                + "\n\n（如果资料内容足够，回答应以此为准；资料未覆盖的可以补充常识但需注明）"
            ),
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
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    answer = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})

    return {
        "question": question,
        "answer": answer,
        "model": "glm-4-flash (Zhipu)",
        "tokens_generated": usage.get("total_tokens", 0),
    }
