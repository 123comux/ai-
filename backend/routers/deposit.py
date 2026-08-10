"""Deposit-style training API: 收押金 / 三锁进度 / 达标全额退费.

三锁门槛（对齐商业评审报告《押金式培训版》）：
- 时间锁：报名后 90 天内完成全部课程与考核，逾期不退。
- 过程锁：五阶段课程完课率 100% + 每阶段作业提交并通过。
- 考核锁：五阶段考核均分 ≥85 + 提交实战项目并通过评审。

达标后全额原路退回；未达标押金转培训费可续学一期；同一身份限退费 1 次。
说明：真实"收押金/原路退回"需接入微信支付（支付+退款 API + 商户证书），
本模块先用数据库记录金额与状态完成业务逻辑闭环，支付/退款为占位实现。
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from config import (
    DEPOSIT_DEFAULT_AMOUNT, DEPOSIT_CURRENCY, DEPOSIT_TIME_LOCK_DAYS,
    DEPOSIT_STAGES, DEPOSIT_PASS_SCORE, DEPOSIT_REFUND_WORKING_DAYS,
)
from database import (
    get_connection, get_deposit, upsert_deposit,
    count_user_watched_videos, get_stage_assessments,
)
from auth_utils import get_current_user

router = APIRouter(prefix="/api/deposit", tags=["deposit"])


# ---------- Schemas ----------

class EnrollRequest(BaseModel):
    amount: float | None = None  # 不传则用默认押金


class StageAssessmentRequest(BaseModel):
    stage: int  # 1..DEPOSIT_STAGES
    score: float  # 0..100


class ProjectSubmitRequest(BaseModel):
    passed: bool = False  # 实战项目是否通过评审（默认仅提交）


class HomeworkRequest(BaseModel):
    passed: bool = True


# ---------- Helpers ----------

def _total_video_count() -> int:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) AS c FROM videos").fetchone()
    conn.close()
    return int(row["c"]) if row else 0


def _compute_status(user_id: int, deposit: dict) -> dict:
    """Compute the three-lock progress + eligibility from per-user data."""
    now = datetime.now()

    total_videos = _total_video_count()
    watched = count_user_watched_videos(user_id)
    completion_rate = round(watched / total_videos * 100) if total_videos else 0

    stages = get_stage_assessments(user_id)
    scores = [s["score"] for s in stages]
    assess_avg = round(sum(scores) / len(scores), 1) if scores else 0.0

    # 时间锁
    deadline = deposit.get("deadline_at") or ""
    time_passed = False
    days_left = None
    if deadline:
        try:
            dl = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
            time_passed = now <= dl
            days_left = (dl - now).days
        except ValueError:
            time_passed = False

    homework_passed = bool(deposit.get("homework_passed"))
    project_submitted = bool(deposit.get("project_submitted"))
    project_passed = bool(deposit.get("project_passed"))

    process_passed = completion_rate >= 100 and homework_passed
    assess_passed = assess_avg >= DEPOSIT_PASS_SCORE and project_submitted and project_passed
    eligible = (
        deposit.get("status") == "active"
        and time_passed
        and process_passed
        and assess_passed
    )

    return {
        "completion_rate": completion_rate,
        "watched_videos": watched,
        "total_videos": total_videos,
        "stage_scores": scores,
        "stages_recorded": len(scores),
        "assessment_avg": assess_avg,
        "deadline_at": deadline,
        "days_left": max(days_left, 0) if days_left is not None else None,
        "time_lock": {"passed": time_passed, "label": f"报名后 {DEPOSIT_TIME_LOCK_DAYS} 天内完成全部课程与考核，逾期不退"},
        "process_lock": {"passed": process_passed, "completion_rate": completion_rate, "homework_passed": homework_passed,
                         "label": "五阶段课程完课率 100% + 每阶段作业提交并通过"},
        "assess_lock": {"passed": assess_passed, "avg": assess_avg, "project_submitted": project_submitted,
                        "project_passed": project_passed,
                        "label": f"五阶段考核均分 ≥{DEPOSIT_PASS_SCORE} + 提交实战项目并通过评审"},
        "refund_eligible": eligible,
    }


# ---------- Public config ----------

@router.get("/config")
async def deposit_config():
    """Public deposit-model parameters (for UI rendering)."""
    return {
        "amount": DEPOSIT_DEFAULT_AMOUNT,
        "currency": DEPOSIT_CURRENCY,
        "time_lock_days": DEPOSIT_TIME_LOCK_DAYS,
        "stages": DEPOSIT_STAGES,
        "pass_score": DEPOSIT_PASS_SCORE,
        "refund_working_days": DEPOSIT_REFUND_WORKING_DAYS,
        "locks": {
            "time": f"报名后 {DEPOSIT_TIME_LOCK_DAYS} 天内完成全部课程与考核，逾期不退",
            "process": "五阶段课程完课率 100% + 每阶段作业提交并通过",
            "assess": f"五阶段考核均分 ≥{DEPOSIT_PASS_SCORE} + 提交实战项目并通过评审",
        },
        "refund_rules": {
            "amount": "全额退还培训费，原路退回",
            "timing": f"最终考核通过后 {DEPOSIT_REFUND_WORKING_DAYS} 个工作日内到账",
            "failed": "押金转为培训费，可续学一期",
            "anti_fraud": "同一身份限退费 1 次；考核含 AI 监考 + 人工复核",
        },
    }


# ---------- 收押金（报名） ----------

@router.post("/enroll")
async def enroll(body: EnrollRequest | None = None, user: dict = Depends(get_current_user)):
    """用户报名：先收培训费（押金）。支付为占位实现，记录金额与 90 天死线。"""
    body = body or EnrollRequest()
    existing = get_deposit(user["id"])
    if existing and existing.get("status") == "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="您已报名，无需重复缴纳押金")

    amount = body.amount if body.amount and body.amount > 0 else DEPOSIT_DEFAULT_AMOUNT
    enrolled_at = datetime.now()
    deadline_at = (enrolled_at + timedelta(days=DEPOSIT_TIME_LOCK_DAYS)).strftime("%Y-%m-%d %H:%M:%S")

    deposit = upsert_deposit(user["id"], {
        "amount": amount,
        "currency": DEPOSIT_CURRENCY,
        "status": "active",
        "enrolled_at": enrolled_at.strftime("%Y-%m-%d %H:%M:%S"),
        "deadline_at": deadline_at,
        "time_lock_passed": 0,
        "course_completion_rate": 0,
        "homework_passed": 0,
        "assessment_avg_score": 0,
        "project_submitted": 0,
        "project_passed": 0,
        "refund_eligible": 0,
        "refund_amount": 0,
        "refund_at": "",
        "refund_txn": "",
    })
    return {"ok": True, "deposit": _public_deposit(deposit), "payment_note": "支付为占位实现，接入微信支付后此处发起收款"}


# ---------- 三锁进度 / 达标判定 ----------

@router.get("/status")
async def deposit_status(user: dict = Depends(get_current_user)):
    """返回当前用户的押金状态、三锁进度与是否达标（含预估退费）。"""
    deposit = get_deposit(user["id"])
    if not deposit:
        return {"enrolled": False, "config": await deposit_config()}
    status = _compute_status(user["id"], deposit)
    # 持久化最新计算结果，供退费复核
    upsert_deposit(user["id"], {
        "time_lock_passed": 1 if status["time_lock"]["passed"] else 0,
        "course_completion_rate": status["completion_rate"],
        "homework_passed": 1 if status["process_lock"]["homework_passed"] else 0,
        "assessment_avg_score": status["assessment_avg"],
        "project_submitted": 1 if status["assess_lock"]["project_submitted"] else 0,
        "project_passed": 1 if status["assess_lock"]["project_passed"] else 0,
        "refund_eligible": 1 if status["refund_eligible"] else 0,
    })
    return {
        "enrolled": True,
        "deposit": _public_deposit(deposit),
        "status": status,
    }


# ---------- 考核锁：录入五阶段考核成绩 ----------

@router.post("/stage-assessment")
async def stage_assessment(body: StageAssessmentRequest, user: dict = Depends(get_current_user)):
    if not (1 <= body.stage <= DEPOSIT_STAGES):
        raise HTTPException(status_code=400, detail=f"阶段需在 1~{DEPOSIT_STAGES} 之间")
    if not (0 <= body.score <= 100):
        raise HTTPException(status_code=400, detail="成绩需在 0~100 之间")
    from database import record_stage_assessment
    record_stage_assessment(user["id"], body.stage, body.score)
    return {"ok": True, "stage": body.stage, "score": body.score}


# ---------- 过程锁：作业通过 ----------

@router.post("/homework")
async def homework_pass(body: HomeworkRequest, user: dict = Depends(get_current_user)):
    upsert_deposit(user["id"], {"homework_passed": 1 if body.passed else 0})
    return {"ok": True, "homework_passed": body.passed}


# ---------- 考核锁：提交实战项目 ----------

@router.post("/project-submit")
async def project_submit(body: ProjectSubmitRequest, user: dict = Depends(get_current_user)):
    upsert_deposit(user["id"], {
        "project_submitted": 1,
        "project_passed": 1 if body.passed else 0,
    })
    return {"ok": True, "project_submitted": True, "project_passed": body.passed}


# ---------- 达标全额退费 ----------

@router.post("/refund")
async def refund(user: dict = Depends(get_current_user)):
    """达标后全额原路退回。业务闭环：校验三锁→置为已退费→记录退款金额。

    真实"原路退回"需调用微信支付退款 API（需商户证书与支付流水号），此处为占位。
    """
    deposit = get_deposit(user["id"])
    if not deposit:
        raise HTTPException(status_code=400, detail="尚未报名，无法退费")
    if deposit.get("status") == "refunded":
        raise HTTPException(status_code=400, detail="该身份已退费（同一身份限退费 1 次）")
    if deposit.get("status") in ("forfeited", "converted"):
        raise HTTPException(status_code=400, detail="押金已转为培训费，不可退")

    calc = _compute_status(user["id"], deposit)
    if not calc["refund_eligible"]:
        reasons = []
        if not calc["time_lock"]["passed"]:
            reasons.append("时间锁未通过（已超过 90 天期限）")
        if not calc["process_lock"]["passed"]:
            reasons.append(f"过程锁未通过（完课率 {calc['completion_rate']}%，需 100% 且作业通过）")
        if not calc["assess_lock"]["passed"]:
            reasons.append(f"考核锁未通过（均分 {calc['assessment_avg']}，需 ≥{DEPOSIT_PASS_SCORE} 且实战项目通过）")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未达标，暂不可退费：" + "；".join(reasons),
        )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated = upsert_deposit(user["id"], {
        "status": "refunded",
        "refund_amount": deposit.get("amount", 0),
        "refund_at": now,
        "refund_txn": f"manual_{int(datetime.now().timestamp())}",
        "refund_eligible": 1,
    })
    return {
        "ok": True,
        "refund_amount": updated.get("amount", 0),
        "refund_at": now,
        "timing_note": f"预计 {DEPOSIT_REFUND_WORKING_DAYS} 个工作日内原路退回（真实退款需接入微信支付）",
    }


def _public_deposit(d: dict) -> dict:
    return {
        "amount": d.get("amount", 0),
        "currency": d.get("currency", "CNY"),
        "status": d.get("status", "active"),
        "enrolled_at": d.get("enrolled_at", ""),
        "deadline_at": d.get("deadline_at", ""),
        "refund_amount": d.get("refund_amount", 0),
        "refund_at": d.get("refund_at", ""),
    }
