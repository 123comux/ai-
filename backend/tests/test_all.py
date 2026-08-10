"""
全功能模块测试套件（对应《全功能模块实现指南与测试验证文档》v2.0）。

分层：
- 纯函数单测：token 验签、三锁判定辅助、章节标准化、技能掌握判定、方向融合
- 集成测试：14 个后端路由模块的端到端链路

运行：
    cd D:/aishixi/backend
    python -m pytest tests/ -q        (若有 pytest)
    # 或
    python -m unittest tests.test_all -v
"""

import os
import sys
import time
import unittest

# 让 backend 包与内部 `from database import ...` 均可导入
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (ROOT, BACKEND):
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.testclient import TestClient  # noqa: E402
from backend.main import app  # noqa: E402

client = TestClient(app)


def _login(nickname="tester"):
    """用 DEV_MODE 登录拿到 token + user。"""
    code = f"test_{int(time.time()*1000)}_{nickname}"
    r = client.post("/api/auth/wechat-login", json={"code": code, "nickname": nickname})
    assert r.status_code == 200, r.text
    return r.json()["token"], r.json()["user"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


class TestPureFunctions(unittest.TestCase):
    def test_token_sign_verify(self):
        from backend.auth_utils import create_token, verify_token
        tok = create_token(123)
        self.assertEqual(verify_token(tok), 123)
        # 篡改签名
        bad = tok[:-2] + ("00" if tok[-2:] != "00" else "ff")
        self.assertIsNone(verify_token(bad))
        # 过期
        exp = int(time.time()) - 10
        expired = f"123.{exp}.{create_token.__module__}"  # 伪造一个错误签名即可
        # 直接用内部签名构造过期 token
        from backend.auth_utils import _sign
        payload = f"123.{exp}"
        expired = f"{payload}.{_sign(payload)}"
        self.assertIsNone(verify_token(expired))

    def test_skill_mastered_threshold(self):
        from backend.routers.user_data import _skill_mastered
        dims_low = {"编程基础": 30, "机器学习": 20}
        self.assertFalse(_skill_mastered("Python", dims_low))
        dims_high = {"编程基础": 80}
        self.assertTrue(_skill_mastered("Python", dims_high))

    def test_fuse_direction(self):
        from backend.routers.assessment import _fuse_direction
        # 无 AI 主题 -> 保持测验方向
        self.assertEqual(_fuse_direction("大模型应用开发", ""), "大模型应用开发")
        # LLM 测验 + 编程基础 -> 仍为 LLM 方向
        self.assertEqual(_fuse_direction("大模型应用开发", "编程基础"), "大模型应用开发")

    def test_normalize_chapters(self):
        try:
            from backend.routers.courses import _normalize_chapters
        except Exception:
            self.skipTest("courses._normalize_chapters 不可用")
        # 别名兼容：content_summary -> summary, sub_chapters -> sections
        raw = [{"title": "T", "content_summary": "S", "sub_chapters": [{"title": "x"}]}]
        out = _normalize_chapters(raw)
        self.assertEqual(out[0]["summary"], "S")
        self.assertIn("sections", out[0])


class TestAuth(unittest.TestCase):
    def test_wechat_login(self):
        token, user = _login("auth_user")
        self.assertTrue(token)
        self.assertIn("id", user)

    def test_me_requires_auth(self):
        r = client.get("/api/auth/me")
        self.assertEqual(r.status_code, 401)
        token, _ = _login("auth_me")
        r = client.get("/api/auth/me", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)
        self.assertIn("id", r.json())


class TestDeposit(unittest.TestCase):
    def test_config(self):
        r = client.get("/api/deposit/config")
        self.assertEqual(r.status_code, 200)
        self.assertIn("amount", r.json())

    def test_enroll_requires_auth(self):
        r = client.post("/api/deposit/enroll")
        self.assertEqual(r.status_code, 401)

    def test_full_loop(self):
        token, user = _login("deposit_user")
        # enroll
        r = client.post("/api/deposit/enroll", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)
        # 看完全部视频
        vids = [v["id"] for v in client.get("/api/videos").json()]
        self.assertTrue(vids)
        for vid in vids:
            client.post(f"/api/videos/{vid}/complete", headers=auth_header(token), json={"minutes": 1})
        # 五阶段考核 + 作业 + 项目
        for s in range(1, 6):
            client.post("/api/deposit/stage-assessment", headers=auth_header(token),
                        json={"stage": s, "score": 90})
        client.post("/api/deposit/homework", headers=auth_header(token), json={"passed": True})
        client.post("/api/deposit/project-submit", headers=auth_header(token), json={"passed": True})
        # 状态应达标
        r = client.get("/api/deposit/status", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)
        st = r.json()
        self.assertTrue(st["status"]["refund_eligible"], st)
        # 退费
        r = client.post("/api/deposit/refund", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)
        self.assertIn("refund_amount", r.json())


class TestCourses(unittest.TestCase):
    def test_list_detail_topics(self):
        r = client.get("/api/courses")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(len(r.json()) > 0)
        cid = r.json()[0]["id"]
        r = client.get(f"/api/courses/{cid}")
        self.assertEqual(r.status_code, 200)
        r = client.get("/api/courses/topics")
        self.assertEqual(r.status_code, 200)


class TestProjects(unittest.TestCase):
    def test_list_detail(self):
        r = client.get("/api/projects")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(len(r.json()) > 0)
        pid = r.json()[0]["id"]
        r = client.get(f"/api/projects/{pid}")
        self.assertEqual(r.status_code, 200)

    def test_advance_per_user(self):
        token, user = _login("proj_user")
        pid = client.get("/api/projects").json()[0]["id"]
        r = client.post(f"/api/projects/{pid}/advance", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)
        # 无 token 不应污染（全局 JSON 路径不报错即可）
        r2 = client.post(f"/api/projects/{pid}/advance")
        self.assertIn(r2.status_code, (200, 404))


class TestVideos(unittest.TestCase):
    def test_list_and_complete(self):
        r = client.get("/api/videos")
        self.assertEqual(r.status_code, 200)
        vid = r.json()[0]["id"]
        r = client.get(f"/api/videos/{vid}")
        self.assertEqual(r.status_code, 200)
        # 课程视频
        cid = client.get("/api/courses").json()[0]["id"]
        r = client.get(f"/api/videos/course/{cid}")
        self.assertIn(r.status_code, (200, 404))
        # 完成（per-user 隔离）
        token, _ = _login("vid_user")
        r = client.post(f"/api/videos/{vid}/complete", headers=auth_header(token), json={"minutes": 3})
        self.assertEqual(r.status_code, 200)


class TestLearningPaths(unittest.TestCase):
    def test_list_detail(self):
        r = client.get("/api/learning-paths")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(len(r.json()) > 0)
        pid = r.json()[0]["id"]
        r = client.get(f"/api/learning-paths/{pid}")
        self.assertEqual(r.status_code, 200)
        # 节点完成（per-user）
        token, _ = _login("path_user")
        node = r.json()["nodes"][0]["id"] if r.json().get("nodes") else None
        if node:
            rr = client.post(f"/api/learning-paths/{pid}/nodes/{node}/complete",
                             headers=auth_header(token))
            self.assertIn(rr.status_code, (200, 400))  # 顺序锁可能 400，均允许


class TestAssessment(unittest.TestCase):
    def test_questions(self):
        r = client.get("/api/assessment/questions?count=10")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(len(r.json()) > 0)

    def test_submit_persists_per_user(self):
        token, _ = _login("assess_user")
        qs = client.get("/api/assessment/questions?count=10").json()
        qids = [q["id"] for q in qs]
        ans = [0 for _ in qs]  # 任意作答，验证提交与持久化链路
        r = client.post("/api/assessment/submit", headers=auth_header(token),
                        json={"answers": ans, "question_ids": qids})
        self.assertEqual(r.status_code, 200)
        # 提交后应能读到该用户的能力报告
        r = client.get("/api/user/ability-report", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)
        self.assertIn("dimensions", r.json())


class TestUserData(unittest.TestCase):
    def test_ability_report_and_stats_per_user(self):
        token, _ = _login("udata_user")
        r = client.get("/api/user/ability-report", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)
        r = client.get("/api/user/learning-stats", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)
        self.assertIn("learningDays", r.json())
        r = client.get("/api/user/learning-records", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json(), list)

    def test_job_matching_analyze(self):
        token, _ = _login("jm_user")
        r = client.post("/api/user/job-matching/analyze", headers=auth_header(token),
                        json={"job_description": "招聘Python机器学习工程师"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("matchScore", r.json())

    def test_job_matching_requires_description(self):
        token, _ = _login("jm_user2")
        r = client.post("/api/user/job-matching/analyze", headers=auth_header(token), json={})
        self.assertEqual(r.status_code, 400)


class TestAI(unittest.TestCase):
    def test_models(self):
        r = client.get("/api/ai/models")
        self.assertEqual(r.status_code, 200)

    def test_tutor_chat(self):
        r = client.post("/api/tutor/chat", json={"question": "什么是梯度下降？"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("answer", r.json())

    def test_recommend(self):
        r = client.get("/api/recommend/courses?interest=Python")
        self.assertEqual(r.status_code, 200)
        self.assertIn("recommendations", r.json())


class TestContent(unittest.TestCase):
    def test_banners_directions_menu(self):
        for ep in ("/api/content/banners", "/api/content/directions", "/api/content/menu-items"):
            r = client.get(ep)
            self.assertEqual(r.status_code, 200, ep)


class TestMineData(unittest.TestCase):
    def test_goals_crud(self):
        token, _ = _login("goal_user")
        h = auth_header(token)
        r = client.post("/api/mine/goals", headers=h, json={"title": "学会PyTorch"})
        self.assertEqual(r.status_code, 200)
        gid = r.json()["id"]
        r = client.put(f"/api/mine/goals/{gid}", headers=h, json={"status": "done"})
        self.assertEqual(r.status_code, 200)
        r = client.get("/api/mine/goals", headers=h)
        self.assertEqual(r.status_code, 200)
        r = client.delete(f"/api/mine/goals/{gid}", headers=h)
        self.assertEqual(r.status_code, 200)

    def test_favorites(self):
        token, _ = _login("fav_user")
        h = auth_header(token)
        cid = client.get("/api/courses").json()[0]["id"]
        r = client.post("/api/mine/favorites", headers=h, json={"item_type": "course", "item_id": cid})
        self.assertEqual(r.status_code, 200)
        fid = r.json()["id"]
        r = client.get("/api/mine/favorites", headers=h)
        self.assertEqual(r.status_code, 200)
        r = client.delete(f"/api/mine/favorites/{fid}", headers=h)
        self.assertEqual(r.status_code, 200)

    def test_portfolio(self):
        r = client.get("/api/mine/portfolio")
        self.assertEqual(r.status_code, 200)


class TestKnowledge(unittest.TestCase):
    def test_search(self):
        r = client.get("/api/knowledge/search?query=python")
        self.assertEqual(r.status_code, 200)

    def test_topics_count_browse(self):
        for ep in ("/api/knowledge/topics", "/api/knowledge/count", "/api/knowledge/browse"):
            r = client.get(ep)
            self.assertEqual(r.status_code, 200, ep)


class TestAdmin(unittest.TestCase):
    def test_login_and_crud(self):
        # admin 路由鉴权：用标准 Authorization header 携带 Bearer token
        # （已修复：此前用 `auth` header 是非标准用法，现已统一为 Authorization）
        r = client.post("/api/admin/login", params={"username": "admin", "password": "admin123"})
        self.assertEqual(r.status_code, 200, r.text)
        token = r.json()["token"]
        h = {"Authorization": f"Bearer {token}"}
        # 列出表
        r = client.get("/api/admin/tables")
        self.assertEqual(r.status_code, 200)
        # 读一个表
        r = client.get("/api/admin/courses", headers=h)
        self.assertEqual(r.status_code, 200)
        # 创建一个 banner 再删
        r = client.post("/api/admin/banners", headers=h,
                        json={"title": "测试横幅", "description": "x", "image_url": "http://e/x.png",
                              "link_url": "/pages/home/index", "sort_order": 99})
        self.assertEqual(r.status_code, 200)
        bid = r.json().get("id")
        if bid:
            rr = client.delete(f"/api/admin/banners/{bid}", headers=h)
            self.assertEqual(rr.status_code, 200)


class TestCommunity(unittest.TestCase):
    """平台化：每日打卡 / 学习排行榜 / 学习社区。"""

    def _login(self, nickname):
        code = f"comm_{int(time.time()*1000)}_{nickname}"
        r = client.post("/api/auth/wechat-login", json={"code": code, "nickname": nickname})
        self.assertEqual(r.status_code, 200)
        return r.json()["token"], r.json()["user"]

    def test_checkin_flow(self):
        token, user = self._login("comm_user")
        h = {"Authorization": f"Bearer {token}"}
        # 首次打卡成功，streak=1
        r = client.post("/api/community/checkin", headers=h, json={"note": "学提示词"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["streak"], 1)
        # 状态显示今日已打
        r = client.get("/api/community/checkin/status", headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["today_checked"])
        self.assertEqual(r.json()["streak"], 1)
        # 重复打卡应 400
        r = client.post("/api/community/checkin", headers=h, json={})
        self.assertEqual(r.status_code, 400)

    def test_checkin_requires_auth(self):
        r = client.post("/api/community/checkin", json={})
        self.assertEqual(r.status_code, 401)

    def test_leaderboard(self):
        token, user = self._login("rank_user")
        h = {"Authorization": f"Bearer {token}"}
        r = client.get("/api/community/leaderboard", headers=h)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("ranking", data)
        self.assertIsInstance(data["ranking"], list)

    def test_posts_and_replies(self):
        token, user = self._login("post_user")
        h = {"Authorization": f"Bearer {token}"}
        # 发帖
        r = client.post("/api/community/posts", headers=h,
                        json={"title": "测试帖", "content": "内容", "category": "提问"})
        self.assertEqual(r.status_code, 200)
        pid = r.json()["id"]
        # 空标题 400
        r = client.post("/api/community/posts", headers=h, json={"title": " ", "content": "x"})
        self.assertEqual(r.status_code, 400)
        # 列表
        r = client.get("/api/community/posts", headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(any(p["id"] == pid for p in r.json()))
        # 详情
        r = client.get(f"/api/community/posts/{pid}", headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["post"]["title"], "测试帖")
        # 回复
        r = client.post(f"/api/community/posts/{pid}/reply", headers=h, json={"content": "回复1"})
        self.assertEqual(r.status_code, 200)
        # 点赞
        r = client.post(f"/api/community/posts/{pid}/like", headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["likes"], 1)


class TestContentPromptTemplates(unittest.TestCase):
    """提示词模板库。"""

    def test_prompt_templates(self):
        r = client.get("/api/content/prompt-templates")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        cats = {t["category"] for t in data}
        self.assertTrue({"学生", "职场", "编程", "求职"}.issubset(cats))
        # 按分类过滤
        r = client.get("/api/content/prompt-templates?category=" + "学生")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(all(t["category"] == "学生" for t in r.json()))
        # 分类列表
        r = client.get("/api/content/prompt-templates/categories")
        self.assertEqual(r.status_code, 200)
        self.assertIn("categories", r.json())


class TestPractice(unittest.TestCase):
    """在线 AI 实操练习台（提示词优化）。"""

    def test_practice_analyze(self):
        r = client.post("/api/practice/analyze", json={"question": "帮我写周报"})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("improved_prompt", data)
        self.assertIn("suggestion", data)
        # 空问题 422（pydantic 校验）
        r = client.post("/api/practice/analyze", json={"question": ""})
        self.assertEqual(r.status_code, 422)


class TestAbilityHistory(unittest.TestCase):
    """能力成长曲线（测评历史）。"""

    def test_history(self):
        token, user = self._login("hist_user")
        h = {"Authorization": f"Bearer {token}"}
        r = client.get("/api/user/ability-history", headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertIn("history", r.json())
        self.assertIn("count", r.json())

    def _login(self, nickname):
        code = f"hist_{int(time.time()*1000)}_{nickname}"
        r = client.post("/api/auth/wechat-login", json={"code": code, "nickname": nickname})
        self.assertEqual(r.status_code, 200)
        return r.json()["token"], r.json()["user"]


class TestAdminDashboard(unittest.TestCase):
    """后台数据看板 + 泛型表管理（含 prefix Header 修复回归）。"""

    def test_dashboard_and_tables(self):
        r = client.post("/api/admin/login?username=admin&password=admin123")
        self.assertEqual(r.status_code, 200)
        token = r.json()["token"]
        h = {"Authorization": f"Bearer {token}"}
        # 数据看板（回归：带 prefix 的 Header 注入修复）
        r = client.get("/api/admin/dashboard", headers=h)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        for k in ("users", "checkins", "posts", "assessments"):
            self.assertIn(k, data)
        # 泛型表管理：新表 users 可读
        r = client.get("/api/admin/users", headers=h)
        self.assertEqual(r.status_code, 200)
        # 无 token 应 401
        r = client.get("/api/admin/dashboard")
        self.assertEqual(r.status_code, 401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
