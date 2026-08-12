"""Community & learning-motivation API router.

Covers three platform features (迭代计划 · 平台化量力加):
- 每日 AI 打卡（checkins）：连续打卡记录、连续天数、激励
- 学习排行榜（leaderboard）：按学习时长/完课率排行
- 学习社区（posts/replies）：学员提问、互助、FAQ 沉淀
- 分享解锁（share-unlock）：分享课程解锁进阶内容（社交裂变）
- 好友组队学习（teams）：组队学习、裂变增长

All data is per-user (multi-tenant). Auth required via get_current_user.
"""
from datetime import datetime, date

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from database import get_connection, insert_row, query_one
from auth_utils import get_current_user

router = APIRouter(prefix="/api/community", tags=["community"])


# ---------- Schemas ----------

class CheckinRequest(BaseModel):
    note: str = ""


class PostRequest(BaseModel):
    title: str
    content: str = ""
    category: str = "general"


class ReplyRequest(BaseModel):
    content: str


# ---------- Helpers ----------

def _checkin_streak(user_id: int) -> int:
    """连续打卡天数：从今天（或昨天）往前数连续有打卡记录的天数。"""
    conn = get_connection()
    rows = conn.execute(
        "SELECT checkin_date FROM checkins WHERE user_id=? ORDER BY checkin_date DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    dates = {r["checkin_date"] for r in rows}
    if not dates:
        return 0
    streak = 0
    cur = date.today()
    if cur.isoformat() not in dates:
        # 今天还没打卡，从昨天开始算（不因今天未打卡清零）
        from datetime import timedelta
        cur = cur - timedelta(days=1)
    while cur.isoformat() in dates:
        streak += 1
        from datetime import timedelta
        cur = cur - timedelta(days=1)
    return streak


def _user_learning_seconds(user_id: int) -> int:
    """用户累计学习时长（秒），来自 user_video_progress 的 minutes 汇总。"""
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(minutes), 0) AS total FROM user_video_progress WHERE user_id=?",
        (user_id,),
    ).fetchone()
    conn.close()
    return int(row["total"]) * 60 if row else 0


# ---------- 每日打卡 ----------

@router.post("/checkin")
async def checkin(body: CheckinRequest | None = None, user: dict = Depends(get_current_user)):
    """今日打卡。同一用户一天只能打一次（UNIQUE 约束）。"""
    today = date.today().isoformat()
    conn = get_connection()
    exists = conn.execute(
        "SELECT id FROM checkins WHERE user_id=? AND checkin_date=?", (user["id"], today)
    ).fetchone()
    conn.close()
    if exists:
        raise HTTPException(status_code=400, detail="今日已打卡")
    insert_row("checkins", {"user_id": user["id"], "checkin_date": today,
                            "note": (body.note if body else "")[:100]})
    streak = _checkin_streak(user["id"])
    # 订阅消息：打卡成功提醒（模板未配置则静默跳过）
    try:
        from services.wechat_msg import notify_checkin
        notify_checkin(user, streak)
    except Exception:
        pass
    return {"ok": True, "checkin_date": today, "streak": streak}


@router.get("/checkin/status")
async def checkin_status(user: dict = Depends(get_current_user)):
    """当前用户打卡状态：今日是否已打、连续天数、本月打卡记录。"""
    today = date.today().isoformat()
    conn = get_connection()
    rows = conn.execute(
        "SELECT checkin_date FROM checkins WHERE user_id=? ORDER BY checkin_date DESC LIMIT 30",
        (user["id"],),
    ).fetchall()
    today_done = any(r["checkin_date"] == today for r in rows)
    conn.close()
    return {
        "today_checked": today_done,
        "streak": _checkin_streak(user["id"]),
        "recent_dates": [r["checkin_date"] for r in rows],
    }


# ---------- 学习排行榜 ----------

@router.get("/leaderboard")
async def leaderboard(limit: int = 20, user: dict = Depends(get_current_user)):
    """按累计学习时长排行（分钟），取前 N 名。学习时长来自各用户视频观看记录。"""
    conn = get_connection()
    rows = conn.execute("""
        SELECT u.id, u.nickname, u.avatar, COALESCE(SUM(p.minutes), 0) AS total_minutes,
               COUNT(DISTINCT p.video_id) AS watched_videos
        FROM users u
        LEFT JOIN user_video_progress p ON p.user_id = u.id
        GROUP BY u.id
        ORDER BY total_minutes DESC, watched_videos DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    # 当前用户名次
    my_id = user["id"]
    rank = next((i + 1 for i, r in enumerate(rows) if r["id"] == my_id), None)
    return {
        "ranking": [dict(r) for r in rows],
        "my_rank": rank,
        "my_total_minutes": _user_learning_seconds(my_id) // 60,
    }


# ---------- 学习社区 ----------

@router.post("/posts")
async def create_post(body: PostRequest, user: dict = Depends(get_current_user)):
    title = (body.title or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="标题不能为空")
    pid = insert_row("community_posts", {
        "user_id": user["id"], "title": title[:80],
        "content": (body.content or "")[:2000],
        "category": (body.category or "general")[:20],
    })
    return query_one("community_posts", pid)


@router.get("/posts")
async def list_posts(category: str = "", limit: int = 30, user: dict = Depends(get_current_user)):
    """帖子列表（带作者昵称与回复数），可选按分类过滤。"""
    conn = get_connection()
    if category:
        rows = conn.execute("""
            SELECT p.*, u.nickname, u.avatar,
                   (SELECT COUNT(*) FROM community_replies r WHERE r.post_id = p.id) AS reply_count
            FROM community_posts p JOIN users u ON u.id = p.user_id
            WHERE p.category=? ORDER BY p.id DESC LIMIT ?
        """, (category, limit)).fetchall()
    else:
        rows = conn.execute("""
            SELECT p.*, u.nickname, u.avatar,
                   (SELECT COUNT(*) FROM community_replies r WHERE r.post_id = p.id) AS reply_count
            FROM community_posts p JOIN users u ON u.id = p.user_id
            ORDER BY p.id DESC LIMIT ?
        """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/posts/{post_id}")
async def get_post(post_id: int, user: dict = Depends(get_current_user)):
    """帖子详情 + 回复列表。"""
    conn = get_connection()
    post = conn.execute("""
        SELECT p.*, u.nickname, u.avatar
        FROM community_posts p JOIN users u ON u.id = p.user_id WHERE p.id=?
    """, (post_id,)).fetchone()
    replies = conn.execute("""
        SELECT r.*, u.nickname, u.avatar FROM community_replies r
        JOIN users u ON u.id = r.user_id WHERE r.post_id=? ORDER BY r.id
    """, (post_id,)).fetchall()
    conn.close()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    return {"post": dict(post), "replies": [dict(r) for r in replies]}


@router.post("/posts/{post_id}/reply")
async def reply_post(post_id: int, body: ReplyRequest, user: dict = Depends(get_current_user)):
    content = (body.content or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="回复内容不能为空")
    conn = get_connection()
    exists = conn.execute("SELECT id FROM community_posts WHERE id=?", (post_id,)).fetchone()
    conn.close()
    if not exists:
        raise HTTPException(status_code=404, detail="帖子不存在")
    rid = insert_row("community_replies", {
        "post_id": post_id, "user_id": user["id"], "content": content[:500],
    })
    return query_one("community_replies", rid)


@router.post("/posts/{post_id}/like")
async def like_post(post_id: int, user: dict = Depends(get_current_user)):
    """点赞（简单计数，不做幂等去重——MVP 阶段够用）。"""
    conn = get_connection()
    exists = conn.execute("SELECT id FROM community_posts WHERE id=?", (post_id,)).fetchone()
    if not exists:
        conn.close()
        raise HTTPException(status_code=404, detail="帖子不存在")
    conn.execute("UPDATE community_posts SET likes = likes + 1 WHERE id=?", (post_id,))
    conn.commit()
    row = conn.execute("SELECT id, likes FROM community_posts WHERE id=?", (post_id,)).fetchone()
    conn.close()
    return dict(row)


# ---------- 分享解锁（社交裂变） ----------

@router.post("/share-unlock")
async def share_unlock(
    share_type: str = "course", share_target: str = "", user: dict = Depends(get_current_user)
):
    """分享课程/页面后解锁进阶内容（分享即解锁，无需额外验证）。"""
    if not share_target:
        raise HTTPException(status_code=400, detail="share_target 不能为空")
    conn = get_connection()
    exists = conn.execute(
        "SELECT id FROM share_unlocks WHERE user_id=? AND share_type=? AND share_target=?",
        (user["id"], share_type, share_target),
    ).fetchone()
    if exists:
        conn.close()
        return {"ok": True, "already_unlocked": True, "message": "已解锁过此内容"}
    insert_row("share_unlocks", {
        "user_id": user["id"],
        "share_type": share_type,
        "share_target": share_target,
        "unlocked_content": f"{share_type}:{share_target}",
    })
    conn.close()
    return {"ok": True, "already_unlocked": False, "message": "分享成功，已解锁进阶内容"}


@router.get("/share-unlock/status")
async def share_unlock_status(user: dict = Depends(get_current_user)):
    """查询当前用户已解锁的分享内容列表。"""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM share_unlocks WHERE user_id=? ORDER BY created_at DESC",
        (user["id"],),
    ).fetchall()
    conn.close()
    return {"unlocked": [dict(r) for r in rows], "count": len(rows)}


# ---------- 好友组队学习 ----------

@router.post("/teams")
async def create_team(name: str = "", max_members: int = 5, user: dict = Depends(get_current_user)):
    """创建学习小组。"""
    import secrets
    name = (name or "").strip()
    if not name:
        name = f"{user.get('nickname', '学员')}的学习小组"
    code = secrets.token_hex(4).upper()
    tid = insert_row("teams", {
        "name": name[:30],
        "code": code,
        "owner_id": user["id"],
        "max_members": max(2, min(max_members, 10)),
    })
    insert_row("team_members", {"team_id": tid, "user_id": user["id"]})
    return query_one("teams", tid)


@router.post("/teams/join")
async def join_team(code: str = "", user: dict = Depends(get_current_user)):
    """通过邀请码加入学习小组。"""
    code = (code or "").strip().upper()
    if not code:
        raise HTTPException(status_code=400, detail="邀请码不能为空")
    conn = get_connection()
    team = conn.execute("SELECT * FROM teams WHERE code=?", (code,)).fetchone()
    if not team:
        conn.close()
        raise HTTPException(status_code=404, detail="未找到该小组")
    if team["member_count"] >= team["max_members"]:
        conn.close()
        raise HTTPException(status_code=400, detail="小组已满")
    exists = conn.execute(
        "SELECT id FROM team_members WHERE team_id=? AND user_id=?",
        (team["id"], user["id"]),
    ).fetchone()
    if exists:
        conn.close()
        return {"ok": True, "team": dict(team), "message": "你已在该小组中"}
    insert_row("team_members", {"team_id": team["id"], "user_id": user["id"]})
    conn.execute("UPDATE teams SET member_count = member_count + 1 WHERE id=?", (team["id"],))
    conn.commit()
    team = conn.execute("SELECT * FROM teams WHERE id=?", (team["id"],)).fetchone()
    conn.close()
    return {"ok": True, "team": dict(team), "message": "加入成功"}


@router.get("/teams/mine")
async def my_teams(user: dict = Depends(get_current_user)):
    """查询我加入的学习小组。"""
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.*, tm.joined_at FROM teams t
        JOIN team_members tm ON tm.team_id = t.id AND tm.user_id = ?
        ORDER BY t.id DESC
    """, (user["id"],)).fetchall()
    conn.close()
    return {"teams": [dict(r) for r in rows]}


@router.get("/teams/{team_id}")
async def team_detail(team_id: int, user: dict = Depends(get_current_user)):
    """小组详情（含成员列表与各自学习进度）。"""
    conn = get_connection()
    team = query_one("teams", team_id)
    if not team:
        conn.close()
        raise HTTPException(status_code=404, detail="小组不存在")
    members = conn.execute("""
        SELECT u.id, u.nickname, u.avatar,
               COALESCE(SUM(uvp.minutes), 0) AS total_minutes
        FROM team_members tm
        JOIN users u ON u.id = tm.user_id
        LEFT JOIN user_video_progress uvp ON uvp.user_id = u.id
        WHERE tm.team_id = ?
        GROUP BY u.id
        ORDER BY total_minutes DESC
    """, (team_id,)).fetchall()
    conn.close()
    return {"team": dict(team), "members": [dict(m) for m in members]}
