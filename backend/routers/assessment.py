"""Assessment API router."""

import concurrent.futures

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel

from models.schemas import AssessmentQuestion, AssessmentQuestionPublic, AssessmentResult
from services.assessment_service import get_assessment, score_assessment
from auth_utils import get_optional_user

router = APIRouter(prefix="/api/assessment", tags=["assessment"])

# AI fusion runs in a module-level thread pool and is best-effort: if the BERT
# model isn't already loaded, we give up after a few seconds rather than block
# the assessment result. The worker thread keeps running in the background to
# warm the model, so a later request gets the fusion. Using a module-level pool
# (not "with") avoids the shutdown(wait=True) that would defeat the timeout.
_fusion_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
_FUSION_TIMEOUT_SECONDS = 8.0


class SubmitRequest(BaseModel):
    answers: list[int]
    question_ids: list[str]
    # Optional self-description for AI-fused direction refinement (e.g. "我熟悉 Python，想学大模型")
    self_description: str = ""


@router.get("/questions", response_model=list[AssessmentQuestionPublic])
async def get_questions(
    topic: str = Query(None, description="Filter by topic"),
    count: int = Query(10, ge=1, le=20),
):
    """Get assessment questions (without correct_answer)."""
    questions = get_assessment(topic, count)
    if not questions:
        raise HTTPException(status_code=404, detail="No questions available")
    # 隐藏正确答案，避免前端泄露
    return [AssessmentQuestionPublic(**q.model_dump()) for q in questions]


@router.post("/submit", response_model=AssessmentResult)
async def submit_assessment(req: SubmitRequest, user: Optional[dict] = Depends(get_optional_user)):
    """Submit assessment answers, get scored result, optionally fused with AI text analysis."""
    if len(req.answers) != len(req.question_ids):
        raise HTTPException(status_code=400, detail="Answers and question_ids must have same length")
    if not req.answers:
        raise HTTPException(status_code=400, detail="No answers provided")

    result = score_assessment(req.answers, req.question_ids, user_id=user["id"] if user else None)

    # AI fusion: if the user wrote a self-description, let the BERT analyzer
    # refine the recommended direction. Runs in a thread with a hard timeout so
    # a cold model never blocks the assessment result.
    if req.self_description.strip():
        try:
            future = _fusion_executor.submit(
                _fuse_with_ai, result.recommended_direction, req.self_description.strip()
            )
            try:
                fused = future.result(timeout=_FUSION_TIMEOUT_SECONDS)
            except concurrent.futures.TimeoutError:
                pass  # model warm-up too slow -> keep quiz-based direction
            else:
                if fused and fused != result.recommended_direction:
                    result.recommended_direction = fused
        except Exception:
            pass  # never let fusion break the assessment

    return result


def _fuse_with_ai(quiz_direction: str, description: str) -> str:
    """Run BERT analysis and blend its topic with the quiz-derived direction."""
    from services.assessment_ai_service import analyze_content
    analysis = analyze_content(description)
    ai_topic = analysis.get("predicted_topic", "")
    return _fuse_direction(quiz_direction, ai_topic)


def _fuse_direction(quiz_direction: str, ai_topic: str) -> str:
    """Blend quiz-derived direction with the BERT-predicted topic.

    The quiz result is primary; the AI topic nudges toward a more specific
    direction when they align or when the AI is confident on a clear signal.
    """
    if not ai_topic or ai_topic == "其他":
        return quiz_direction

    ai_direction_map = {
        "机器学习": "机器学习工程师",
        "深度学习": "深度学习工程师",
        "数据科学": "数据科学家",
        "编程基础": "AI 应用开发",
        "数学统计": "数据科学家",
    }
    ai_dir = ai_direction_map.get(ai_topic, quiz_direction)

    # If AI and quiz agree on a family, trust the quiz (more reliable signal).
    if ai_dir == quiz_direction:
        return quiz_direction

    # LLM-oriented quiz result + AI says programming base -> widen to application dev
    if quiz_direction == "大模型应用开发" and ai_topic == "编程基础":
        return "大模型应用开发"

    # Otherwise prefer the quiz direction but keep the AI hint if quiz is generic
    if quiz_direction in ("AI 应用开发", "AI 工程师"):
        return ai_dir
    return quiz_direction
