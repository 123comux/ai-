"""DeepSeek chat service — OpenAI 兼容接口，纯 requests，无 torch/transformers 导入。

与 zhipu_service 返回结构一致，供 model_router 按场景选档位：
- deepseek-chat：标准档（通用对话，性价比高）
- deepseek-reasoner：pro 档（复杂推理：作业评审/深度分析）
"""

import requests

from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL


def chat_deepseek(
    question: str,
    system_prompt: str,
    max_new_tokens: int = 220,
    temperature: float = 0.0,
    model: str = "deepseek-chat",
) -> dict:
    """Call DeepSeek API (OpenAI-compatible chat completions)."""
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY not configured")

    # 复用课程知识库 RAG，与智谱路径一致，保证答疑质量
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
        DEEPSEEK_API_URL,
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": messages,
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "stream": False,
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    answer = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})

    return {
        "question": question,
        "answer": answer,
        "model": f"{model} (DeepSeek)",
        "tokens_generated": usage.get("total_tokens", 0),
    }
