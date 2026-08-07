"""AI-powered API routes: tutor chat, assessment analysis, course recommendation."""

import concurrent.futures

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/api", tags=["ai"])

# AI 推荐运行在模块级线程池并设超时：BERT 冷加载慢时不阻塞接口，
# 超时回退纯关键词匹配，worker 继续后台预热模型。
_recommend_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
_RECOMMEND_TIMEOUT_SECONDS = 6.0


# ---- Schemas ----

class TutorRequest(BaseModel):
    """AI tutor chat request."""
    question: str = Field(..., min_length=1, max_length=2000)
    system_prompt: Optional[str] = None
    max_new_tokens: int = Field(220, ge=50, le=2048)
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
    """AI tutor: answer student questions using fine-tuned Qwen model."""
    try:
        from services.tutor_service import chat
        result = chat(
            question=req.question,
            system_prompt=req.system_prompt,
            max_new_tokens=req.max_new_tokens,
            temperature=req.temperature,
        )
        return TutorResponse(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Model not available: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


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
    """Get info about all available AI models."""
    info = {"models": {}}

    # Recommender (always available if built)
    try:
        from services.recommend_service import get_model_info
        info["models"]["recommender"] = get_model_info()
    except Exception:
        info["models"]["recommender"] = {"status": "not available"}

    # Assessment BERT
    try:
        from services.assessment_ai_service import get_model_info
        info["models"]["assessment"] = get_model_info()
    except Exception:
        info["models"]["assessment"] = {"status": "not available"}

    # Tutor Qwen
    try:
        from services.tutor_service import get_model_info
        info["models"]["tutor"] = get_model_info()
    except Exception:
        info["models"]["tutor"] = {"status": "not available"}

    return info
