"""
全功能模块测试套件（对应《功能模块实现与测试验证文档》v3.0）。
零基础AI教学平台 · 押金式培训版。

分层：
- 纯函数单测：token 验签、三锁判定辅助、章节标准化、技能掌握判定、方向融合
- 集成测试：15 个后端路由模块的端到端链路

运行：
    cd D:/aishixi/backend
    DEV_MODE=true python -m pytest tests/ -q   (若有 pytest)
    # 或
    DEV_MODE=true python -m unittest tests.test_all -v

注意：`.env` 中 DEV_MODE=false（真实微信登录）时，测试用假 code 登录会返回 401。
测试以 DEV_MODE=true 覆盖运行即可，勿修改 .env 里的真实登录配置。
"""

import os
import sys
import time
import unittest
import base64
import json

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


class TestDbDialect(unittest.TestCase):
    """方言翻译纯函数：SQLite 写法 → MySQL（无 DB 依赖即可验证）。"""

    def _t(self):
        from db import to_mysql, to_mysql_ddl
        return to_mysql, to_mysql_ddl

    def test_placeholder_skips_string_literal_question(self):
        to_mysql, _ = self._t()
        sql = "SELECT id FROM favorites WHERE item_type=? AND item_id=? AND detail_path='/pages/courseDetail/index?id='"
        out = to_mysql(sql)
        self.assertEqual(out, "SELECT id FROM favorites WHERE item_type=%s AND item_id=%s AND detail_path='/pages/courseDetail/index?id='")

    def test_datetime_now(self):
        to_mysql, _ = self._t()
        self.assertIn("NOW()", to_mysql("UPDATE t SET watched_at=datetime('now') WHERE id=?"))

    def test_upsert_or_replace(self):
        to_mysql, _ = self._t()
        out = to_mysql("INSERT OR REPLACE INTO user_chapter_progress (user_id, course_id, chapter_id) VALUES (?,?,?)")
        self.assertTrue(out.startswith("REPLACE INTO"))

    def test_on_conflict_to_duplicate_key(self):
        to_mysql, _ = self._t()
        sql = "INSERT INTO p (user_id, video_id, minutes) VALUES (?,?,?) ON CONFLICT(user_id, video_id) DO UPDATE SET minutes=excluded.minutes, watched_at=datetime('now')"
        out = to_mysql(sql)
        self.assertIn("ON DUPLICATE KEY UPDATE minutes=VALUES(minutes), watched_at=NOW()", out)

    def test_ddl_autoincrement(self):
        _, to_mysql_ddl = self._t()
        out = to_mysql_ddl("CREATE TABLE t (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(100) NOT NULL UNIQUE)")
        self.assertIn("AUTO_INCREMENT", out)
        self.assertNotIn("AUTOINCREMENT", out)

    def test_ddl_timestamp_default(self):
        _, to_mysql_ddl = self._t()
        out = to_mysql_ddl("CREATE TABLE t (created_at TEXT NOT NULL DEFAULT (datetime('now')))")
        self.assertIn("DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP", out)

    def test_ddl_text_literal_default_becomes_expression(self):
        _, to_mysql_ddl = self._t()
        out = to_mysql_ddl("CREATE TABLE t (description TEXT NOT NULL DEFAULT '')")
        self.assertIn("DEFAULT ('')", out)

    def test_text_in_key_stays_varchar(self):
        _, to_mysql_ddl = self._t()
        out = to_mysql_ddl("CREATE TABLE t (id VARCHAR(100) PRIMARY KEY, openid VARCHAR(200) NOT NULL UNIQUE)")
        self.assertNotIn("TEXT PRIMARY KEY", out)
        self.assertIn("VARCHAR(200) NOT NULL UNIQUE", out)


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
        # 学完五阶段课程全部章节（完课率按章节计，不依赖遗留视频库）
        courses = client.get("/api/courses").json()
        for c in courses:
            for ch in (c.get("chapters") or []):
                r = client.post(
                    f"/api/courses/{c['id']}/chapters/{ch['id']}/complete",
                    headers=auth_header(token),
                )
                self.assertEqual(r.status_code, 200, f"complete chapter {ch['id']}")
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
        # 退费：申请 → 待人工复核 → 后台放行 → refunded
        r = client.post("/api/deposit/refund", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "refund_pending")
        adm = client.post("/api/admin/login", params={"username": "admin", "password": "admin123"}).json()
        ah = {"Authorization": f"Bearer {adm['token']}"}
        rv = client.get("/api/admin/deposit/refund-reviews", headers=ah)
        self.assertGreater(rv.json()["count"], 0)
        uid = rv.json()["reviews"][0]["user_id"]
        r = client.post(f"/api/admin/deposit/refund-reviews/{uid}", json={"approved": True}, headers=ah)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["result"], "approved")
        st2 = client.get("/api/deposit/status", headers=auth_header(token)).json()
        self.assertEqual(st2["deposit"]["status"], "refunded")


class TestHomework(unittest.TestCase):
    """作业提交 / AI 评审 / 后台复核（过程锁作业闭环）。AI 评审用 mock 打桩，避免真实网络调用。"""

    def _patch_review(self, score=82.0, feedback="写得很清楚"):
        from unittest.mock import patch
        import routers.homework as hw  # 与 main.py `from routers import homework` 同一模块对象
        return patch.object(hw, "_ai_review", return_value=(score, feedback))

    def test_questions_public(self):
        r = client.get("/api/deposit/homework/questions")
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.json()["questions"]), 5)

    def test_submit_requires_auth(self):
        r = client.post("/api/deposit/homework/1/submit", json={"content": "x" * 50})
        self.assertEqual(r.status_code, 401)

    def test_submit_review_flow(self):
        token, _ = _login("hw_user")
        with self._patch_review(82.0, "写得很清楚"):
            r = client.post("/api/deposit/homework/1/submit",
                            json={"content": "AI能帮我写文案翻译总结，显著提升效率，但也要注意核实。" * 5},
                            headers=auth_header(token))
            self.assertEqual(r.status_code, 200, r.text)
            body = r.json()
            self.assertTrue(body["passed"])
            self.assertEqual(body["score"], 82.0)
        st = client.get("/api/deposit/homework/status", headers=auth_header(token)).json()
        self.assertEqual(st["passed_count"], 1)
        self.assertEqual(st["items"][0]["status"], "passed")

    def test_reject_below_threshold(self):
        token, _ = _login("hw_low")
        with self._patch_review(40.0, "内容不完整"):
            r = client.post("/api/deposit/homework/1/submit",
                            json={"content": "AI能帮我写文案翻译总结，显著提升效率，但也要注意核实。" * 5},
                            headers=auth_header(token))
            self.assertEqual(r.status_code, 200)
            self.assertFalse(r.json()["passed"])
            self.assertEqual(r.json()["status"], "rejected")

    def test_short_content_rejected(self):
        token, _ = _login("hw_short")
        r = client.post("/api/deposit/homework/1/submit", json={"content": "短"}, headers=auth_header(token))
        self.assertEqual(r.status_code, 422)

    def test_invalid_stage(self):
        token, _ = _login("hw_badstage")
        r = client.post("/api/deposit/homework/9/submit", json={"content": "x" * 50}, headers=auth_header(token))
        self.assertEqual(r.status_code, 400)

    def test_process_lock_requires_all_stages(self):
        token, _ = _login("hw_process")
        with self._patch_review(82.0, "好"):
            for s in range(1, 6):
                r = client.post(f"/api/deposit/homework/{s}/submit",
                                json={"content": f"第{s}阶段作业内容，完整作答。" * 6},
                                headers=auth_header(token))
                self.assertEqual(r.status_code, 200, r.text)
        st = client.get("/api/deposit/homework/status", headers=auth_header(token)).json()
        self.assertTrue(st["all_passed"])
        self.assertEqual(st["passed_count"], 5)

    def test_admin_review_override(self):
        token, _ = _login("hw_admin_rev")
        with self._patch_review(50.0, "需要改进"):
            client.post("/api/deposit/homework/1/submit",
                        json={"content": "AI能帮我写文案翻译总结，显著提升效率，但也要注意核实。" * 5},
                        headers=auth_header(token))
        adm = client.post("/api/admin/login", params={"username": "admin", "password": "admin123"}).json()
        ah = {"Authorization": f"Bearer {adm['token']}"}
        rv = client.get("/api/admin/homework/reviews", params={"status": "all"}, headers=ah)
        self.assertEqual(rv.status_code, 200)
        self.assertGreater(rv.json()["count"], 0)
        sid = rv.json()["reviews"][0]["id"]
        r = client.post(f"/api/admin/homework/reviews/{sid}", json={"status": "passed", "score": 90}, headers=ah)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["submission"]["status"], "passed")
        self.assertEqual(r.json()["submission"]["ai_score"], 90)
        # 无 admin token 应 401
        bad = client.get("/api/admin/homework/reviews", headers=auth_header(token))
        self.assertEqual(bad.status_code, 401)


class TestWxpayPayment(unittest.TestCase):
    """微信支付 V3：加密/签名原语 + 回调置已支付 + 未配置商户号占位路径。

    不依赖真实商户号：AES/RSA 用临时密钥自测，回调验签用 mock。
    """

    def test_aes_gcm_decrypt_roundtrip(self):
        from services import wxpay_service as w
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        key = "a" * 32
        w.WXPAY_APIV3_KEY = key
        aesgcm = AESGCM(key.encode())
        nonce = b"b" * 12
        payload = b'{"out_trade_no":"dep_1_1","trade_state":"SUCCESS","transaction_id":"txn1"}'
        ct = aesgcm.encrypt(nonce, payload, b"assoc")
        dec = w.decrypt_resource(
            base64.b64encode(ct).decode(), base64.b64encode(nonce).decode(), "assoc")
        self.assertEqual(dec["out_trade_no"], "dep_1_1")
        self.assertEqual(dec["trade_state"], "SUCCESS")

    def test_rsa_sign_roundtrip(self):
        import tempfile
        import os
        from services import wxpay_service as w
        from cryptography.hazmat.primitives.asymmetric import rsa, padding as ap
        from cryptography.hazmat.primitives import serialization, hashes
        priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pem = priv.private_bytes(serialization.Encoding.PEM,
                                 serialization.PrivateFormat.PKCS8,
                                 serialization.NoEncryption()).decode()
        tmp = tempfile.NamedTemporaryFile(suffix=".pem", mode="w", delete=False)
        tmp.write(pem); tmp.close()
        w.WXPAY_PRIVATE_KEY = tmp.name
        try:
            msg = "POST\n/v3/pay/transactions/jsapi\n1700000000\nnonce\n{}\n"
            sig = base64.b64decode(w._sign(msg))
            priv.public_key().verify(sig, msg.encode(), ap.PKCS1v15(), hashes.SHA256())
        finally:
            os.unlink(tmp.name)

    def test_placeholder_enroll_without_merchant(self):
        # 未配置商户号：报名直接置 active（占位），/api/pay/jsapi 返回占位提示
        token, _ = _login("pay_placeholder")
        r = client.post("/api/deposit/enroll", json={}, headers=auth_header(token))
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.json().get("need_pay"))
        r2 = client.post("/api/pay/jsapi", headers=auth_header(token))
        self.assertEqual(r2.status_code, 200)
        self.assertTrue(r2.json()["placeholder"])

    def test_notify_marks_deposit_paid(self):
        import base64 as b64
        from unittest.mock import patch
        from services import wxpay_service as w
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from database import upsert_deposit, get_deposit

        token, user = _login("pay_notify")
        upsert_deposit(user["id"], {"amount": 199, "status": "pending_payment",
                                    "out_trade_no": "dep_notify_1"})
        key = "a" * 32
        w.WXPAY_APIV3_KEY = key
        aesgcm = AESGCM(key.encode())
        nonce = b"n" * 12
        payload = b'{"out_trade_no":"dep_notify_1","trade_state":"SUCCESS","transaction_id":"4200abc"}'
        ad_str = "transaction"
        ct = aesgcm.encrypt(nonce, payload, ad_str.encode())
        body = json.dumps({
            "event_type": "TRANSACTION.SUCCESS",
            "resource": {
                "algorithm": "AEAD_AES_256_GCM",
                "ciphertext": b64.b64encode(ct).decode(),
                "associated_data": ad_str,
                "nonce": b64.b64encode(nonce).decode(),
            },
        })
        with patch("services.wxpay_service.verify_notify_signature", return_value=True):
            r = client.post("/api/pay/notify", content=body)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json().get("code"), "SUCCESS")
        dep = get_deposit(user["id"])
        self.assertEqual(dep["status"], "active")
        self.assertEqual(dep["transaction_id"], "4200abc")


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
    """提示词模板库 + FAQ 公开接口。"""

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

    def test_faq(self):
        """FAQ 常见问题库公开接口。"""
        r = client.get("/api/content/faq")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        self.assertIn("question", data[0])
        self.assertIn("answer", data[0])
        # 分类列表
        r = client.get("/api/content/faq/categories")
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
        for k in ("users", "checkins", "posts", "assessments", "faq_count"):
            self.assertIn(k, data)
        # 泛型表管理：新表 users 可读
        r = client.get("/api/admin/users", headers=h)
        self.assertEqual(r.status_code, 200)
        # 无 token 应 401
        r = client.get("/api/admin/dashboard")
        self.assertEqual(r.status_code, 401)


if __name__ == "__main__":
    unittest.main(verbosity=2)


# ===== 新增：分享解锁 + 组队学习 + FAQ 管理 =====

class TestShareUnlock(unittest.TestCase):
    """分享解锁（社交裂变）。"""

    def test_share_unlock_flow(self):
        token, user = self._login("share_test")
        h = {"Authorization": f"Bearer {token}"}
        # 分享解锁
        r = client.post(f"/api/community/share-unlock?share_type=course&share_target=stage-1-cognition", headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        # 重复解锁
        r = client.post(f"/api/community/share-unlock?share_type=course&share_target=stage-1-cognition", headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["already_unlocked"])
        # 查询状态
        r = client.get("/api/community/share-unlock/status", headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(r.json()["count"], 1)

    def test_share_unlock_requires_auth(self):
        r = client.post("/api/community/share-unlock?share_type=course&share_target=test")
        self.assertEqual(r.status_code, 401)

    def _login(self, nickname):
        code = f"share_{int(time.time()*1000)}_{nickname}"
        r = client.post("/api/auth/wechat-login", json={"code": code, "nickname": nickname})
        self.assertEqual(r.status_code, 200)
        return r.json()["token"], r.json()["user"]


class TestTeams(unittest.TestCase):
    """好友组队学习。"""

    def test_team_flow(self):
        token1, user1 = self._login("team_owner")
        h1 = {"Authorization": f"Bearer {token1}"}
        # 创建小组
        r = client.post(f"/api/community/teams?name=AI学习先锋队&max_members=5", headers=h1)
        self.assertEqual(r.status_code, 200)
        team = r.json()
        self.assertIn("code", team)
        code = team["code"]
        # 查询我的小组
        r = client.get("/api/community/teams/mine", headers=h1)
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.json()["teams"]), 1)
        # 另一个用户加入
        token2, _ = self._login("team_member")
        h2 = {"Authorization": f"Bearer {token2}"}
        r = client.post(f"/api/community/teams/join?code={code}", headers=h2)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        # 小组详情
        r = client.get(f"/api/community/teams/{team['id']}", headers=h1)
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.json()["members"]), 2)

    def test_join_invalid_code(self):
        token, _ = self._login("bad_joiner")
        h = {"Authorization": f"Bearer {token}"}
        r = client.post("/api/community/teams/join?code=INVALID_CODE", headers=h)
        self.assertEqual(r.status_code, 404)

    def _login(self, nickname):
        code = f"team_{int(time.time()*1000)}_{nickname}"
        r = client.post("/api/auth/wechat-login", json={"code": code, "nickname": nickname})
        self.assertEqual(r.status_code, 200)
        return r.json()["token"], r.json()["user"]


if __name__ == "__main__":
    unittest.main(verbosity=2)
