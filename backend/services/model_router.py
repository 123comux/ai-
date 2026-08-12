"""AI 模型分层路由：按场景成本档位选供应商，主失败回退次（商业报告 6.3 成本分层）。

档位映射（双供应商并存，智谱为主 + DeepSeek 可选）：
- flash   高频轻量（导师答疑 / 实操练习）：智谱 glm-4-flash 为主，失败回退 DeepSeek deepseek-chat
- standard 中频（课程问答等一般生成）：有 DeepSeek key 时优先 deepseek-chat（更省），否则智谱 glm-4-flash
- pro     低频复杂（作业评审 / 深度分析）：有 DeepSeek key 时优先 deepseek-reasoner，否则智谱 glm-4-flash

说明：账号实测智谱标准档 glm-4 返回 429，故智谱统一用免费档 glm-4-flash；
标准/pro 档位的成本优势在配置 DeepSeek key 后体现（deepseek-chat 极便宜、reasoner 推理强）。
任一档位全部失败时抛 RuntimeError，由调用方兜底（rule-fallback，不 5xx）。
"""


def _try_chain(calls):
    last = None
    for fn in calls:
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 —— 双供应商逐一尝试，任一成功即返回
            last = e
    raise RuntimeError("All AI providers failed") from last


def _zhipu(question, system_prompt, max_new_tokens, temperature):
    from services.zhipu_service import chat_zhipu
    return chat_zhipu(question, system_prompt, max_new_tokens, temperature, model="glm-4-flash")


def _ds(question, system_prompt, max_new_tokens, temperature, model):
    from services.deepseek_service import chat_deepseek
    return chat_deepseek(question, system_prompt, max_new_tokens, temperature, model=model)


def _has_deepseek() -> bool:
    from config import DEEPSEEK_API_KEY
    return bool(DEEPSEEK_API_KEY)


def chat_flash(question: str, system_prompt: str = "", max_new_tokens: int = 220, temperature: float = 0.0) -> dict:
    """高频轻量档：答疑/实操，智谱 flash 优先，回退 DeepSeek。"""
    return _try_chain([
        lambda: _zhipu(question, system_prompt, max_new_tokens, temperature),
        lambda: _ds(question, system_prompt, max_new_tokens, temperature, "deepseek-chat"),
    ])


def chat_standard(question: str, system_prompt: str = "", max_new_tokens: int = 220, temperature: float = 0.0) -> dict:
    """中频标准档：课程问答等一般生成。DeepSeek key 存在时优先 deepseek-chat。"""
    if _has_deepseek():
        return _try_chain([
            lambda: _ds(question, system_prompt, max_new_tokens, temperature, "deepseek-chat"),
            lambda: _zhipu(question, system_prompt, max_new_tokens, temperature),
        ])
    return _zhipu(question, system_prompt, max_new_tokens, temperature)


def chat_pro(question: str, system_prompt: str = "", max_new_tokens: int = 512, temperature: float = 0.0) -> dict:
    """低频复杂档：作业评审/深度分析。DeepSeek key 存在时优先 deepseek-reasoner。"""
    if _has_deepseek():
        return _try_chain([
            lambda: _ds(question, system_prompt, max_new_tokens, temperature, "deepseek-reasoner"),
            lambda: _zhipu(question, system_prompt, max_new_tokens, temperature),
        ])
    return _zhipu(question, system_prompt, max_new_tokens, temperature)
