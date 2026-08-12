"""作业提交 / AI 评审 / 后台复核（押金式培训「过程锁」的作业闭环）。

用户侧：
- GET  /api/deposit/homework/questions     各阶段作业题目（公开）
- GET  /api/deposit/homework/status        当前用户各阶段作业状态（含题目+提交+AI分数）
- POST /api/deposit/homework/{stage}/submit 提交作业 → AI 按 rubric 评审打分 → 落库

后台侧：
- GET  /api/admin/homework/reviews         待复核作业列表（可只取 pending）
- POST /api/admin/homework/reviews/{id}     人工复核改判（pass/reject + 分数）——防刷一环

评分说明：AI 评审走大模型（智谱/DeepSeek），不可用时回退「作答完整度」启发式，
保证任何环境都能闭环；人工复核可在后台改判最终结果。
"""
import re

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field

from auth_utils import get_current_user
from database import (
    get_homework_question, get_homework_questions, get_homework_submission,
    get_homework_submissions, get_all_homework_submissions, admin_judge_homework,
    upsert_homework_submission,
)

router = APIRouter(prefix="/api/deposit/homework", tags=["homework"])
admin_router = APIRouter(prefix="/api/admin/homework", tags=["homework_admin"])

PASS_SCORE = 60  # 作业评审及格线

STAGE_NAMES = {1: "认知", 2: "入门", 3: "进阶", 4: "实战", 5: "熟练"}


# ---------- Schemas ----------

class HomeworkSubmitRequest(BaseModel):
    content: str = Field(..., min_length=10, max_length=4000, description="作业作答内容")


class AdminJudgeRequest(BaseModel):
    status: str  # passed / rejected
    score: float = Field(0, ge=0, le=100)


# ---------- AI 评审 ----------

def _fallback_score(content: str) -> int:
    """无 AI 时的兜底评分：按作答完整度粗评，仅供流程跑通，最终以人工复核为准。"""
    n = len(content.strip())
    if n >= 200:
        return 80
    if n >= 100:
        return 66
    if n >= 40:
        return 52
    return 32


def _ai_review(stage: int, question: dict, content: str) -> tuple[float, str]:
    """用大模型按 rubric 评审作业，返回 (score 0-100, feedback)。

    走 model_router 的 pro 档（DeepSeek reasoner 优先，回退智谱 glm-4），
    双供应商均不可用时回退启发式评分，保证接口不 5xx。
    """
    rubric = question.get("rubric", "")
    prompt = (
        f"你是一位严格的 AI 学习作业评审老师，请评审学员第 {stage} 阶段（{STAGE_NAMES.get(stage,'')}）的作业。\n"
        f"【题目】{question.get('title', '')}\n"
        f"【作答要求】{question.get('requirement', '')}\n"
        f"【评审标准】{rubric}\n"
        f"【学员作答】\n{content}\n"
        "请按评审标准给 0-100 的整数分，并给出 2-3 句中文评语，指出优点与改进点。\n"
        "输出格式（严格）：\n【得分】NN\n【评语】...\n"
    )
    try:
        from services.model_router import chat_pro
        resp = chat_pro(question=content[:2000], system_prompt=prompt, max_new_tokens=300, temperature=0.3)
        raw = resp.get("answer", "")
        m = re.search(r"【得分】\s*(\d+)", raw)
        score = int(m.group(1)) if m else None
        fb = re.search(r"【评语】\s*(.+)", raw, re.S)
        feedback = fb.group(1).strip()[:500] if fb else ""
        if score is None:
            score = _fallback_score(content)
        return max(0, min(100, float(score))), feedback
    except Exception:
        return float(_fallback_score(content)), "（AI 评审暂不可用，按作答完整度初步评分，可联系人工复核。）"


# ---------- 用户侧 ----------

@router.get("/questions")
async def homework_questions():
    """各阶段作业题目（公开，无需登录）。"""
    return {"questions": get_homework_questions()}


@router.get("/status")
async def homework_status(user: dict = Depends(get_current_user)):
    """当前用户各阶段作业状态：题目 + 提交内容 + AI 评分 + 是否通过。"""
    questions = {q["stage"]: q for q in get_homework_questions()}
    subs = {s["stage"]: s for s in get_homework_submissions(user["id"])}
    items = []
    for stage in sorted(questions.keys()):
        q = questions[stage]
        sub = subs.get(stage)
        items.append({
            "stage": stage,
            "stage_name": STAGE_NAMES.get(stage, ""),
            "title": q["title"],
            "requirement": q["requirement"],
            "rubric": q["rubric"],
            "course_id": q["course_id"],
            "submitted": bool(sub),
            "content": sub["content"] if sub else "",
            "ai_score": sub["ai_score"] if sub else None,
            "ai_feedback": sub["ai_feedback"] if sub else "",
            "status": sub["status"] if sub else "none",
            "passed": bool(sub and sub["status"] == "passed"),
            "updated_at": sub["updated_at"] if sub else "",
        })
    passed_count = sum(1 for it in items if it["passed"])
    return {"items": items, "passed_count": passed_count, "total": len(items), "all_passed": passed_count == len(items)}


@router.post("/{stage}/submit")
async def homework_submit(stage: int, body: HomeworkSubmitRequest, user: dict = Depends(get_current_user)):
    """提交第 stage 阶段作业：AI 评审 → 落库（重交覆盖）。评分 ≥60 记为通过。"""
    if stage not in STAGE_NAMES:
        raise HTTPException(400, f"阶段需在 1~{len(STAGE_NAMES)} 之间")
    q = get_homework_question(stage)
    if not q:
        raise HTTPException(404, f"第 {stage} 阶段作业题目不存在")

    content = body.content.strip()
    score, feedback = _ai_review(stage, q, content)
    status = "passed" if score >= PASS_SCORE else "rejected"
    sub = upsert_homework_submission(user["id"], stage, q["course_id"], content, score, feedback, status)
    # 订阅消息：作业评审结果通知（模板未配置则静默跳过）
    try:
        from services.wechat_msg import notify_homework_result
        notify_homework_result(user, stage, score, status == "passed")
    except Exception:
        pass
    return {
        "ok": True,
        "stage": stage,
        "stage_name": STAGE_NAMES[stage],
        "score": sub["ai_score"],
        "feedback": sub["ai_feedback"],
        "status": sub["status"],
        "passed": sub["status"] == "passed",
        "pass_score": PASS_SCORE,
        "note": "AI 评审结果供参考，最终以人工复核为准。" if sub["status"] != "passed" else "",
    }


# ---------- 后台复核（防刷：人工改判） ----------

@admin_router.get("/reviews")
async def list_reviews(request: Request, status: str = "all"):
    """后台作业复核列表（带用户昵称），按状态筛选：all / passed / rejected。需 admin token。"""
    from routers.admin import verify_token
    verify_token(request)
    filt = None if status == "all" else status
    subs = get_all_homework_submissions(status=filt)
    return {"reviews": subs, "count": len(subs)}


@admin_router.post("/reviews/{submission_id}")
async def judge_review(request: Request, submission_id: int, body: AdminJudgeRequest):
    """人工复核改判作业：passed/rejected + 分数。需 admin token。"""
    from routers.admin import verify_token
    verify_token(request)
    sub = admin_judge_homework(submission_id, body.status, body.score)
    if not sub:
        raise HTTPException(404, "作业提交不存在或状态非法")
    return {"ok": True, "submission": sub}
