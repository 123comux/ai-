"""AI-powered API routes: tutor chat, assessment analysis, course recommendation."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/api", tags=["ai"])


# ---- Schemas ----

class TutorRequest(BaseModel):
    """AI tutor chat request."""
    question: str = Field(..., min_length=1, max_length=2000)
    system_prompt: Optional[str] = None
    max_new_tokens: int = Field(512, ge=50, le=2048)
    temperature: float = Field(0.7, ge=0.0, le=2.0)


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
    try:
        from services.recommend_service import recommend_courses as recommend
        results = recommend(interest=interest, limit=limit, topic=topic)
        return {
            "interest": interest,
            "recommendations": results,
            "total": len(results),
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Model not available: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


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
