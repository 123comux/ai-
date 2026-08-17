"""Deposit-style training API: 收押金 / 三锁进度 / 达标全额退费.

三锁门槛（对齐商业评审报告《押金式培训版》）：
- 时间锁：报名后 90 天内完成全部课程与考核，逾期不退。
- 过程锁：七阶段课程完课率 100% + 每阶段作业提交并通过。
- 考核锁：七阶段考核均分 ≥85 + 提交实战项目并通过评审。

达标后全额原路退回；未达标押金转培训费可续学一期；同一身份限退费 1 次。
说明：真实"收押金/原路退回"需接入微信支付（支付+退款 API + 商户证书），
本模块先用数据库记录金额与状态完成业务逻辑闭环，支付/退款为占位实现。
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel

from config import (
    DEV_MODE,
    DEPOSIT_DEFAULT_AMOUNT, DEPOSIT_CURRENCY, DEPOSIT_TIME_LOCK_DAYS,
    DEPOSIT_STAGES, DEPOSIT_PASS_SCORE, DEPOSIT_REFUND_WORKING_DAYS,
)
from database import (
    get_connection, get_deposit, upsert_deposit,
    count_user_completed_chapters, get_stage_assessments, parse_json_field,
    get_homework_submissions, upsert_homework_submission,
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

def _total_stage_chapters() -> int:
    """七阶段课程总章节数（完课率按章节计，不再依赖遗留视频库）。"""
    conn = get_connection()
    rows = conn.execute("SELECT chapters FROM courses").fetchall()
    conn.close()
    return sum(len(parse_json_field(r["chapters"])) for r in rows)


def _compute_status(user_id: int, deposit: dict) -> dict:
    """Compute the three-lock progress + eligibility from per-user data."""
    now = datetime.now()

    # 七阶段课程完课率：按"已完成章节 / 总章节"计算（课程为文字章节，不依赖遗留视频库）
    total_units = _total_stage_chapters()
    done_units = count_user_completed_chapters(user_id)
    completion_rate = round(done_units / total_units * 100) if total_units else 0

    stages = get_stage_assessments(user_id)
    # 同一阶段多次录入只取最新一次，避免"已录 25 阶段"这种重复计数
    latest_by_stage: dict[int, float] = {}
    for s in stages:
        latest_by_stage[s["stage"]] = s["score"]  # 列表按时间升序，后者覆盖
    stage_scores = list(latest_by_stage.values())
    stages_recorded = len(latest_by_stage)
    assess_avg = round(sum(stage_scores) / len(stage_scores), 1) if stage_scores else 0.0

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

    # 过程锁作业：按「每阶段作业提交并通过」真实判定（完整闭环，不再只是布尔打标）。
    # 数据源 homework_submissions：DEPOSIT_STAGES 个阶段全部 status=passed 才算作业通过。
    homework_subs = {s["stage"]: s for s in get_homework_submissions(user_id)}
    homework_passed = (
        len(homework_subs) >= DEPOSIT_STAGES
        and all(homework_subs[s]["status"] == "passed" for s in homework_subs)
    )
    homework_stages = sorted(homework_subs.keys())
    project_submitted = bool(deposit.get("project_submitted"))
    project_passed = bool(deposit.get("project_passed"))

    process_passed = completion_rate >= 100 and homework_passed
    assess_passed = (
        stages_recorded >= DEPOSIT_STAGES
        and assess_avg >= DEPOSIT_PASS_SCORE
        and project_submitted
        and project_passed
    )
    eligible = (
        deposit.get("status") == "active"
        and time_passed
        and process_passed
        and assess_passed
    )

    return {
        "completion_rate": completion_rate,
        "watched_videos": done_units,
        "total_videos": total_units,
        "stage_scores": stage_scores,
        "stages_recorded": stages_recorded,
        "assessment_avg": assess_avg,
        "deadline_at": deadline,
        "days_left": max(days_left, 0) if days_left is not None else None,
        "time_lock": {"passed": time_passed, "label": f"报名后 {DEPOSIT_TIME_LOCK_DAYS} 天内完成全部课程与考核，逾期不退"},
        "process_lock": {"passed": process_passed, "completion_rate": completion_rate, "homework_passed": homework_passed,
                         "homework_stages": homework_stages,
                         "label": "七阶段课程完课率 100% + 每阶段作业提交并通过"},
        "assess_lock": {"passed": assess_passed, "avg": assess_avg, "project_submitted": project_submitted,
                        "project_passed": project_passed,
                        "label": f"七阶段考核均分 ≥{DEPOSIT_PASS_SCORE} + 提交实战项目并通过评审"},
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
            "process": "七阶段课程完课率 100% + 每阶段作业提交并通过",
            "assess": f"七阶段考核均分 ≥{DEPOSIT_PASS_SCORE} + 提交实战项目并通过评审",
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
    """用户报名：先收培训费（押金）。

    - 微信支付已配置：生成支付单（status=pending_payment）并返回小程序调起支付参数，
      支付成功由回调 /api/pay/notify 置为 active；
    - DEV_MODE 且未配置支付：占位解锁（开发自测用，不真正收钱）；
    - 生产（DEV_MODE=false）未配置支付：**拒绝报名**——绝不免费解锁付费墙，
      否则未配商户号上线会直接绕过押金收费、商业闭环崩塌。
    """
    from config import wxpay_configured
    body = body or EnrollRequest()
    existing = get_deposit(user["id"])
    if existing and existing.get("status") == "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="您已报名，无需重复缴纳押金")

    amount = body.amount if body.amount and body.amount > 0 else DEPOSIT_DEFAULT_AMOUNT
    enrolled_at = datetime.now()
    deadline_at = (enrolled_at + timedelta(days=DEPOSIT_TIME_LOCK_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
    now = enrolled_at.strftime("%Y-%m-%d %H:%M:%S")

    if wxpay_configured():
        # 复用未完成的支付单（用户取消支付后重试），否则生成新单
        out_trade_no = (existing or {}).get("out_trade_no") or f"dep_{user['id']}_{int(datetime.now().timestamp())}"
        deposit = upsert_deposit(user["id"], {
            "amount": amount,
            "currency": DEPOSIT_CURRENCY,
            "status": "pending_payment",
            "enrolled_at": now,
            "deadline_at": deadline_at,
            "out_trade_no": out_trade_no,
        })
        try:
            from services.wxpay_service import build_pay_params
            pay_params = build_pay_params(
                out_trade_no, int(round(amount * 100)), user.get("openid", ""), "智学AI·押金式培训",
            )
            return {"ok": True, "need_pay": True, "deposit": _public_deposit(deposit), "pay_params": pay_params}
        except Exception as e:
            # 下单失败：保持待支付状态，提示用户稍后重试
            raise HTTPException(status_code=502, detail=f"创建支付单失败：{e}")

    if DEV_MODE:
        deposit = upsert_deposit(user["id"], {
            "amount": amount,
            "currency": DEPOSIT_CURRENCY,
            "status": "active",
            "enrolled_at": now,
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
        return {"ok": True, "deposit": _public_deposit(deposit), "payment_note": "支付为占位实现（未配置商户号，仅开发环境），接入微信支付后此处发起收款"}

    # 生产环境未配置微信支付：拒绝报名，绝不免费解锁
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="支付通道未配置，暂无法报名，请稍后再试",
    )


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


# ---------- 考核锁：录入七阶段考核成绩 ----------

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
    """过程锁作业打标（开发/遗留快捷接口）。

    passed=true 时把七阶段作业全部记为通过，写入真实 homework_submissions 记录，
    使过程锁判定走统一数据源（不再只写布尔位）。
    """
    if body.passed:
        for stage in range(1, DEPOSIT_STAGES + 1):
            upsert_homework_submission(
                user["id"], stage, "", "（开发调试：一键标记作业通过）",
                100.0, "（快捷通道自动通过）", "passed",
            )
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


# ---------- 达标全额退费（防刷：申请 → 人工复核 → 放行/驳回） ----------

@router.post("/refund")
async def refund(user: dict = Depends(get_current_user)):
    """达标后申请退费：校验三锁→置为「待人工复核」。

    防刷设计：不直接到账，先进复核队列（AI 监考 + 人工复核）；后台放行后才真正退款
    （真实退款需微信支付商户号，见 pay.py；此处占位标记 refunded）。
    """
    deposit = get_deposit(user["id"])
    if not deposit:
        raise HTTPException(status_code=400, detail="尚未报名，无法退费")
    if deposit.get("status") == "refunded":
        raise HTTPException(status_code=400, detail="该身份已退费（同一身份限退费 1 次）")
    if deposit.get("status") == "refund_pending":
        raise HTTPException(status_code=400, detail="退费申请已提交，等待人工复核")
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
    upsert_deposit(user["id"], {
        "status": "refund_pending",
        "refund_requested_at": now,
        "refund_eligible": 1,
    })
    return {
        "ok": True,
        "status": "refund_pending",
        "refund_amount": deposit.get("amount", 0),
        "timing_note": f"退费申请已提交，等待人工复核（含 AI 监考，预计 {DEPOSIT_REFUND_WORKING_DAYS} 个工作日内处理）",
    }


# ---------- 后台人工复核（防刷） ----------

admin_router = APIRouter(prefix="/api/admin/deposit", tags=["deposit_admin"])


@admin_router.get("/refund-reviews")
async def list_refund_reviews(request: Request = None):
    """待复核退费申请列表（带用户昵称）。需 admin token。"""
    from routers.admin import verify_token
    verify_token(request)
    conn = get_connection()
    rows = conn.execute(
        "SELECT d.user_id, u.nickname, d.amount, d.currency, d.status, d.refund_requested_at, "
        "d.deadline_at, d.course_completion_rate, d.homework_passed, d.assessment_avg_score, "
        "d.project_submitted, d.project_passed "
        "FROM user_deposits d LEFT JOIN users u ON u.id=d.user_id "
        "WHERE d.status='refund_pending' ORDER BY d.refund_requested_at ASC"
    ).fetchall()
    conn.close()
    reviews = [dict(r) for r in rows]
    return {"reviews": reviews, "count": len(reviews)}


class RefundReviewRequest(BaseModel):
    approved: bool


@admin_router.post("/refund-reviews/{user_id}")
async def judge_refund_review(user_id: int, body: RefundReviewRequest, request: Request = None):
    """人工复核放行/驳回退费。放行 → refunded（占位，真实退款见 pay.py）；驳回 → 回到 active。"""
    from routers.admin import verify_token
    verify_token(request)
    deposit = get_deposit(user_id)
    if not deposit:
        raise HTTPException(404, "押金记录不存在")
    if deposit.get("status") != "refund_pending":
        raise HTTPException(400, f"当前状态 {deposit.get('status')} 不在待复核队列")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if body.approved:
        # 已配置商户号且押金有支付单 → 调微信支付退款；否则占位标记退费
        from config import wxpay_configured
        refund_txn = f"manual_{int(datetime.now().timestamp())}"
        real_refund = False
        if wxpay_configured() and deposit.get("out_trade_no"):
            try:
                from services.wxpay_service import refund as wxpay_refund
                total_fen = int(round(float(deposit.get("amount", 0)) * 100))
                res = wxpay_refund(
                    deposit["out_trade_no"],
                    f"ref_{user_id}_{int(datetime.now().timestamp())}",
                    total_fen, total_fen,
                    "押金式培训达标全额退费",
                )
                refund_txn = res.get("refund_id") or res.get("out_refund_no") or refund_txn
                real_refund = True
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"真实退款发起失败：{e}")
        updated = upsert_deposit(user_id, {
            "status": "refunded",
            "refund_amount": deposit.get("amount", 0),
            "refund_at": now,
            "refund_txn": refund_txn,
        })
        return {"ok": True, "result": "approved", "refund_amount": updated.get("amount", 0),
                "note": "已放行退费（真实退款已发起）" if real_refund else "已放行退费（未配置商户号，占位记录）"}
    else:
        upsert_deposit(user_id, {"status": "active", "refund_requested_at": ""})
        return {"ok": True, "result": "rejected", "note": "已驳回，用户押金回到有效状态"}


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
