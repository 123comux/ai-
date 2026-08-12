"""AI-powered API routes: tutor chat, assessment analysis, course recommendation."""

import concurrent.futures
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/api", tags=["ai"])

# AI 推荐运行在模块级线程池并设超时：BERT 冷加载慢时不阻塞接口，
# 超时回退纯关键词匹配，worker 继续后台预热模型。
_recommend_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
_RECOMMEND_TIMEOUT_SECONDS = 6.0

# 模型信息接口也用线程池+超时，避免模型冷加载阻塞 /api/ai/models
_model_info_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


# ---- Schemas ----

class TutorRequest(BaseModel):
    """AI tutor chat request."""
    question: str = Field(..., min_length=1, max_length=2000)
    system_prompt: Optional[str] = None
    max_new_tokens: int = Field(500, ge=50, le=2048)
    temperature: float = Field(0.0, ge=0.0, le=2.0)


class TutorResponse(BaseModel):
    question: str
    answer: str
    model: str
    tokens_generated: int


class AnalyzeRequest(BaseModel):
    """Assessment analysis request."""
    content: str = Field(..., min_length=1, max_length=5000)


class AnalyzeResponse(BaseModel):
    text: str
    predicted_topic: str
    topic_key: str
    confidence: float
    all_topics: dict
    recommendation: str


# ---- Routes ----

@router.post("/tutor/chat", response_model=TutorResponse)
async def tutor_chat(req: TutorRequest):
    """AI tutor: answer student questions.

    Primary: Zhipu GLM API (fast, no local model loading) with course-RAG.
    Fallback: local Qwen LoRA model (requires GPU).
    """
    if req.system_prompt is None:
        system_prompt = (
            "你是一位专业的 AI 学习导师，请用中文给出深入而清晰的讲解。\n"
            "要求：\n"
            "1. 回答要有深度：先一句话概括，再分点解释原理和原因，避免只给结论。\n"
            "2. 用通俗类比帮助初学者理解，但不要过度冗长。\n"
            "3. 必须严格基于提供的课程资料回答；资料没有的内容可补充常识，但标注\"补充\"。\n"
            "4. 不要编造课程资料中没有的事实。"
        )
    else:
        system_prompt = req.system_prompt

    # 1. flash 档（高频轻量，智谱 glm-4-flash 为主，回退 DeepSeek，双供应商并存）
    try:
        from services.model_router import chat_flash
        result = chat_flash(
            question=req.question,
            system_prompt=system_prompt,
            max_new_tokens=req.max_new_tokens,
            temperature=req.temperature,
        )
        return TutorResponse(**result)
    except Exception:
        pass

    # 2. 回退：本地 Qwen LoRA（import 会加载 torch，慢）
    try:
        from services.tutor_service import chat
        result = chat(
            question=req.question,
            system_prompt=system_prompt,
            max_new_tokens=req.max_new_tokens,
            temperature=req.temperature,
        )
        return TutorResponse(**result)
    except Exception:
        # 本地模型缺失/加载失败：进入兜底，不抛 5xx，保证导师页不崩溃
        pass

    # 3. 兜底：未配置任何 AI 模型（智谱 key 缺失且无本地模型）时，
    #    返回一段有用的规则化引导，前端可正常展示，避免 503/500。
    fallback_answer = (
        "同学你好～我是 AI 学习导师。当前服务端尚未配置 AI 模型（需设置 ZHIPU_API_KEY "
        "或部署本地 Qwen 模型），所以暂时无法实时生成详解。\n\n"
        "你可以先按课程中心的学习路径系统学习；配置好模型后，这里就能针对你的问题给出深入解答。\n\n"
        f"你刚才的问题是：「{req.question}」\n建议从基础概念入手，结合课程里的实操项目动手练习，"
        "遇到具体报错再把信息发给我，我会帮你定位。"
    )
    return TutorResponse(
        question=req.question,
        answer=fallback_answer,
        model="rule-fallback",
        tokens_generated=0,
    )


@router.post("/assessment/analyze", response_model=AnalyzeResponse)
async def analyze_ability(req: AnalyzeRequest):
    """AI assessment: analyze student's content to determine knowledge domain."""
    try:
        from services.assessment_ai_service import analyze_content
        result = analyze_content(req.content)
        return AnalyzeResponse(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Model not available: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/recommend/courses")
async def recommend_courses(
    interest: str,
    limit: int = 10,
    topic: Optional[str] = None,
):
    """Course recommendation: suggest courses based on user interest."""
    from services.recommend_service import recommend_courses as recommend

    # BERT 冷加载可能很慢：在线程中运行并设超时，超时后回退到纯关键词匹配，
    # 避免第一个请求卡死。模型在后台线程继续预热，后续请求即可用到 AI。
    future = _recommend_executor.submit(recommend, interest=interest, limit=limit, topic=topic)
    try:
        results = future.result(timeout=_RECOMMEND_TIMEOUT_SECONDS)
    except concurrent.futures.TimeoutError:
        # 超时：用关闭 AI 分析的纯关键词匹配重试（快速返回）
        from services.recommend_service import recommend_courses_keyword_only
        results = recommend_courses_keyword_only(interest=interest, limit=limit, topic=topic)
    return {
        "interest": interest,
        "recommendations": results,
        "total": len(results),
    }


@router.get("/ai/models")
async def model_info():
    """Get info about all available AI models.

    IMPORTANT: must NOT import services.assessment_ai_service / tutor_service here —
    those modules do top-level `import torch/transformers` which takes tens of seconds
    and would block this endpoint (and thus every request) on cold start.
    We report static model info from disk only.
    """
    info = {"models": {}}

    # Recommender (fast, no heavy imports)
    try:
        from services.recommend_service import get_model_info
        info["models"]["recommender"] = get_model_info()
    except Exception:
        info["models"]["recommender"] = {"status": "not available"}

    # Assessment BERT / Tutor Qwen: report availability from disk without importing
    # the heavy service modules (which import torch/transformers).
    models_dir = Path(__file__).resolve().parent.parent / "models"
    for key, sub in (("assessment", "assessment"), ("tutor", "tutor")):
        d = models_dir / sub
        if d.exists() and any(d.iterdir()):
            info["models"][key] = {"status": "available", "model_type": "see detail"}
        else:
            info["models"][key] = {"status": "not available", "reason": "model not found"}

    # DeepSeek 档位可用性（OpenAI 兼容，不加载任何重模型）
    try:
        from config import DEEPSEEK_API_KEY
        info["models"]["deepseek"] = {
            "status": "available" if DEEPSEEK_API_KEY else "not configured",
            "tiers": ["deepseek-chat (standard)", "deepseek-reasoner (pro)"],
        }
    except Exception:
        info["models"]["deepseek"] = {"status": "not available"}

    return info


# ---- 实操练习台：用户输入提问 → AI 对比优质提示词 → 优化建议 ----

class PracticeRequest(BaseModel):
    """Prompt practice request."""
    question: str = Field(..., min_length=1, max_length=1000)  # 用户当前想法的提问


class PracticeResponse(BaseModel):
    question: str
    improved_prompt: str   # 优化后的优质提示词
    suggestion: str        # 优化建议（为什么这样改）
    model: str
    tokens_generated: int


@router.post("/practice/analyze", response_model=PracticeResponse)
async def practice_analyze(req: PracticeRequest):
    """提示词实操：把用户粗糙的提问，改写成高质量提示词并说明优化点。

    This is the core of the "在线 AI 实操练习台" — 用户输入自己写的提问，
    AI 给出优化后的提示词 + 优化建议，帮助用户学会写出高质量提示词。
    """
    try:
        from services.model_router import chat_flash
    except Exception:
        chat_flash = None

    system_prompt = (
        "你是一位提示词工程教练。用户会给出一条粗糙的提问（prompt），"
        "请你输出两段内容，用分隔符分开：\n"
        "【优化后提示词】把用户的提问改写成一个高质量、可直接使用的最佳提示词，"
        "应包含角色、场景、目标、约束等要素。\n"
        "【优化建议】用 2-3 条说明你改进了什么、为什么这样改更好。"
    )

    if chat_flash is not None:
        try:
            resp = chat_flash(question=req.question, system_prompt=system_prompt,
                              max_new_tokens=400, temperature=0.4)
            raw = resp.get("answer", "")
            # 解析两段
            improved = req.question
            suggestion = "优化提示词可加入角色、场景、目标、约束四要素。"
            if "【优化后提示词】" in raw:
                seg = raw.split("【优化后提示词】", 1)[1]
                if "【优化建议】" in seg:
                    improved, sug = seg.split("【优化建议】", 1)
                    suggestion = sug.strip() or suggestion
                else:
                    improved = seg.strip()
            return PracticeResponse(
                question=req.question, improved_prompt=improved.strip(),
                suggestion=suggestion, model=resp.get("model", "zhipu"),
                tokens_generated=resp.get("tokens_generated", 0),
            )
        except Exception:
            pass

    # 兜底：本地规则优化（无 AI 时仍可用）
    improved = f"你是一名{req.question.strip()[:8]}方面的专家。\n目标：{req.question}\n要求：请给出清晰、具体、可执行的回答。"
    return PracticeResponse(
        question=req.question, improved_prompt=improved,
        suggestion="优质提示词应包含：①角色设定 ②明确目标 ③具体约束 ④期望输出格式。",
        model="rule-fallback", tokens_generated=0,
    )

