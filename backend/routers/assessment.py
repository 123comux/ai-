"""Assessment API router."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from models.schemas import AssessmentQuestion, AssessmentQuestionPublic, AssessmentResult
from services.assessment_service import get_assessment, score_assessment

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


class SubmitRequest(BaseModel):
    answers: list[int]
    question_ids: list[str]


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
async def submit_assessment(req: SubmitRequest):
    """Submit assessment answers and get scored result."""
    if len(req.answers) != len(req.question_ids):
        raise HTTPException(status_code=400, detail="Answers and question_ids must have same length")
    if not req.answers:
        raise HTTPException(status_code=400, detail="No answers provided")

    return score_assessment(req.answers, req.question_ids)