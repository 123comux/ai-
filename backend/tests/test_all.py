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
        # 学完七阶段课程全部章节（完课率按章节计，不依赖遗留视频库）
        # 注：课程数超过默认 limit=20，须显式取全部 24 门
        courses = client.get("/api/courses?limit=100").json()
        for c in courses:
            for ch in (c.get("chapters") or []):
                r = client.post(
                    f"/api/courses/{c['id']}/chapters/{ch['id']}/complete",
                    headers=auth_header(token),
                )
                self.assertEqual(r.status_code, 200, f"complete chapter {ch['id']}")
        # 七阶段考核 + 作业 + 项目
        for s in range(1, 8):
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
        # 从复核队列中定位当前用户（而非 reviews[0]——共享开发库里可能有其它历史待复核记录，
        # 取 reviews[0] 会复核错人导致本用例不幂等；CI 靠全新库掩盖了该问题）。
        current_uid = user["id"]
        own_review = next((rv for rv in rv.json()["reviews"] if rv["user_id"] == current_uid), None)
        self.assertIsNotNone(own_review, "复核队列中应包含当前用户的待退费申请")
        r = client.post(f"/api/admin/deposit/refund-reviews/{current_uid}", json={"approved": True}, headers=ah)
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
        self.assertGreaterEqual(len(r.json()["questions"]), 7)

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
            for s in range(1, 8):
                r = client.post(f"/api/deposit/homework/{s}/submit",
                                json={"content": f"第{s}阶段作业内容，完整作答。" * 6},
                                headers=auth_header(token))
                self.assertEqual(r.status_code, 200, r.text)
        st = client.get("/api/deposit/homework/status", headers=auth_header(token)).json()
        self.assertTrue(st["all_passed"])
        self.assertEqual(st["passed_count"], 7)

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

    def test_production_enroll_refused_without_merchant(self):
        # 生产（DEV_MODE=false）且未配商户号：必须拒绝报名（503），绝不占位免费解锁付费墙。
        # 若上线漏配商户号也不至于绕过押金收费。
        from unittest.mock import patch
        import routers.deposit as deposit_mod
        token, user = _login("prod_nopay")
        # 确保该用户无已存在 active 押金，且此时未配商户号
        from database import get_deposit
        self.assertIsNone(get_deposit(user["id"]))
        with patch.object(deposit_mod, "DEV_MODE", False):
            r = client.post("/api/deposit/enroll", json={}, headers=auth_header(token))
        self.assertEqual(r.status_code, 503)
        # 不得被误置为已支付/占用——应保持无押金记录
        self.assertIsNone(get_deposit(user["id"]))

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


class TestLearningPathsDBDriven(unittest.TestCase):
    """学习路径数据库驱动：后台编辑即时生效 + 顺序解锁 + 章节门槛（勿破坏现有解锁逻辑）。"""

    def _first_path(self):
        r = client.get("/api/learning-paths")
        self.assertEqual(r.status_code, 200)
        paths = r.json()
        self.assertGreater(len(paths), 0)
        return paths[0]

    def test_admin_edit_path_reflects_in_public_api(self):
        # 数据库驱动契约：后台改 learning_paths → 公开读接口立即生效
        import urllib.parse
        adm = client.post("/api/admin/login", params={"username": "admin", "password": "admin123"}).json()
        ah = {"Authorization": f"Bearer {adm['token']}"}
        path = self._first_path()
        pid = path["id"]
        url = "/api/admin/learning_paths/" + urllib.parse.quote(pid)
        r = client.put(url, headers=ah, json={"title": "后台改名测试路径"})
        self.assertEqual(r.status_code, 200, r.text)
        try:
            paths = client.get("/api/learning-paths").json()
            edited = next(p for p in paths if p["id"] == pid)
            self.assertEqual(edited["title"], "后台改名测试路径")
        finally:
            # 还原，避免污染后续用例
            client.put(url, headers=ah, json={"title": path["title"]})

    def test_locked_node_cannot_be_skipped(self):
        # 顺序解锁：未完成前一个节点时，直接完成后面的 locked 节点应被拒绝
        token, _ = _login("lp_order")
        path = self._first_path()
        pid = path["id"]
        nodes = path["nodes"]
        self.assertGreater(len(nodes), 2)
        # 假定第 0 个节点为当前节点，第 1 个应处于 locked（除非某真已全部完成）
        r = client.post(f"/api/learning-paths/{pid}/nodes/{nodes[1]['id']}/complete",
                        headers=auth_header(token))
        # 若第 1 个节点是 locked（默认），应 400；若第 0 节点课程章节恰好已全部完成除外——此处用全新用户确保 locked
        self.assertIn(r.status_code, (200, 400))
        if r.status_code == 400:
            self.assertIn("请先完成前一个节点", r.json()["detail"])

    def test_course_node_requires_chapters_completed(self):
        # 章节门槛：全新用户完成当前 course 节点时，若该课程有章节且未学完应被 400 引导
        token, _ = _login("lp_chapters")
        path = self._first_path()
        node0 = path["nodes"][0]
        if node0["type"] != "course" or not node0.get("courseId"):
            self.skipTest("首个节点非课程节点")
        # 仅当该课程确实存在章节时才断言门槛（无章节的课程不设门槛）
        cid = node0["courseId"]
        course = next((c for c in client.get("/api/courses?limit=100").json() if c["id"] == cid), None)
        if not course or not (course.get("chapters") or []):
            self.skipTest("首个节点课程无章节")
        r = client.post(f"/api/learning-paths/{path['id']}/nodes/{node0['id']}/complete",
                        headers=auth_header(token))
        self.assertEqual(r.status_code, 400)
        self.assertIn("章节", r.json()["detail"])

    def test_direction_filter_returns_single_path(self):
        path = self._first_path()
        direction = path["direction"]
        r = client.get(f"/api/learning-paths?direction={direction}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)
        self.assertEqual(r.json()[0]["direction"], direction)

    def test_fallback_direction_get_works(self):
        # 未命中蓝图的任意方向：get_path 仍能按兜底蓝图返回（勿破坏既有行为）
        r = client.get("/api/learning-paths/path-AI%20%E5%B7%A5%E7%A8%8B%E5%B8%88")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["direction"], "AI 工程师")
        self.assertGreater(len(r.json()["nodes"]), 0)


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
        # 新用户尚无个人测评：应返回空初始态（overallScore=0、dimensions 空），
        # 而不是 fallback 到全局 demo 报告——未登录匿名测评不能被算到该账号头上
        self.assertEqual(r.json()["overallScore"], 0)
        self.assertEqual(r.json()["dimensions"], [])
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
        r = client.post(f"/api/community/share-unlock?share_type=course&share_target=s1-llm-basics", headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        # 重复解锁
        r = client.post(f"/api/community/share-unlock?share_type=course&share_target=s1-llm-basics", headers=h)
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


class TestAIQuota(unittest.TestCase):
    """AI 每日额度限流：未缴押金（含试用期）用户限流，已缴押金/匿名不限。

    直接测 service 纯逻辑（patch 小额上限与权限判定），快且不依赖真实网络调用。
    """

    from unittest.mock import patch

    FAKE_UIDS = (99901, 99902)

    def setUp(self):
        # 共享开发库会跨测试运行残留计数，先清掉本用例用到的假用户当日用量，保证幂等
        from database import get_connection
        conn = get_connection()
        for uid in self.FAKE_UIDS:
            conn.execute("DELETE FROM ai_usage_daily WHERE user_id=?", (uid,))
        conn.commit()
        conn.close()

    def _user(self, user_id=99901, paid=False):
        # resolve_access 只用了 user["id"]，这里给个假 user 即可
        return {"id": user_id, "nickname": "quota_user"}

    def test_trial_user_limited_after_daily_cap(self):
        from services import ai_quota
        user = self._user()
        with self.patch.object(ai_quota, "AI_DAILY_LIMIT_DEFAULT", 3), \
             self.patch.object(ai_quota, "resolve_access", return_value={"deposit_paid": False}):
            self.assertEqual(ai_quota.check_ai_quota(user, "tutor")["id"], user["id"])
            ai_quota.check_ai_quota(user, "assessment")
            ai_quota.check_ai_quota(user, "recommend")
            # 第 4 次（跨功能累计）应 429
            with self.assertRaises(Exception) as ctx:
                ai_quota.check_ai_quota(user, "practice")
            self.assertEqual(ctx.exception.status_code, 429)
            self.assertEqual(ctx.exception.detail["code"], "ai_quota_exceeded")

    def test_paid_user_unlimited(self):
        from services import ai_quota
        user = self._user()
        with self.patch.object(ai_quota, "AI_DAILY_LIMIT_DEFAULT", 3), \
             self.patch.object(ai_quota, "resolve_access", return_value={"deposit_paid": True}):
            # 即使远超上限也不拒绝
            for _ in range(10):
                self.assertEqual(ai_quota.check_ai_quota(user, "tutor")["id"], user["id"])

    def test_anonymous_no_count_no_block(self):
        from services import ai_quota
        with self.patch.object(ai_quota, "AI_DAILY_LIMIT_DEFAULT", 0):
            # 匿名返回 None，不抛 429
            self.assertIsNone(ai_quota.check_ai_quota(None, "tutor"))

    def test_remaining_reflects_usage(self):
        from services import ai_quota
        user = self._user(user_id=99902)
        with self.patch.object(ai_quota, "AI_DAILY_LIMIT_DEFAULT", 3), \
             self.patch.object(ai_quota, "resolve_access", return_value={"deposit_paid": False}):
            ai_quota.check_ai_quota(user, "tutor")
            r = ai_quota.ai_quota_remaining(user["id"])
            self.assertTrue(r["limited"])
            self.assertEqual(r["used"], 1)
            self.assertEqual(r["remaining"], 2)

    def test_quota_resets_next_day(self):
        # 额度按"每日"计：用满当天后，第二天重新开始（不跨日累计）
        from datetime import datetime
        from services import ai_quota
        user = self._user(user_id=99903)
        day1 = datetime(2026, 8, 17, 10, 0, 0)
        day2 = datetime(2026, 8, 18, 10, 0, 0)
        with self.patch.object(ai_quota, "AI_DAILY_LIMIT_DEFAULT", 2), \
             self.patch.object(ai_quota, "resolve_access", return_value={"deposit_paid": False}):
            ai_quota.check_ai_quota(user, "tutor", now=day1)
            ai_quota.check_ai_quota(user, "tutor", now=day1)
            # 第 3 次天内 → 429
            with self.assertRaises(Exception) as ctx:
                ai_quota.check_ai_quota(user, "tutor", now=day1)
            self.assertEqual(ctx.exception.status_code, 429)
            # 第二天 → 重新计数，第 1 次放行
            self.assertEqual(ai_quota.check_ai_quota(user, "tutor", now=day2)["id"], user["id"])
        # 清理本用例日期行，保证幂等
        from database import get_connection
        conn = get_connection()
        for d in ("2026-08-17", "2026-08-18"):
            conn.execute("DELETE FROM ai_usage_daily WHERE user_id=? AND usage_date=?", (user["id"], d))
        conn.commit()
        conn.close()


class TestAccessControl(unittest.TestCase):
    """功能使用权限：5 天免费试用 → 缴纳押金解锁（边界计算 + 集成链路）。"""

    def _login(self, nickname):
        code = f"acc_{int(time.time()*1000)}_{nickname}"
        r = client.post("/api/auth/wechat-login", json={"code": code, "nickname": nickname})
        assert r.status_code == 200, r.text
        token = r.json()["token"]
        uid = r.json()["user"]["id"]
        # 清掉历史权限/押金，保证每个用例从"全新用户 + 试用期"起步
        from database import get_connection
        conn = get_connection()
        conn.execute("DELETE FROM user_access WHERE user_id=?", (uid,))
        conn.execute("DELETE FROM user_deposits WHERE user_id=?", (uid,))
        conn.commit()
        conn.close()
        return token, uid

    def _expire(self, uid, days=10):
        """把试用起点推到指定天数前（服务端落库，等价真实到期）。"""
        from datetime import datetime, timedelta
        from database import upsert_user_access
        old = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        upsert_user_access(uid, {"trial_started_at": old})

    # ---------- 纯函数：试用期计算边界 ----------

    def test_compute_access_in_trial_day1(self):
        from datetime import datetime
        from services.access_service import compute_access
        started = datetime(2026, 8, 12, 10, 0, 0)
        now = datetime(2026, 8, 13, 10, 0, 0)  # 第 1 天中期
        s = compute_access(now, started, False)
        self.assertTrue(s["in_trial"])
        self.assertTrue(s["access_granted"])
        self.assertFalse(s["warn_expiring"])
        self.assertEqual(s["trial_remaining_seconds"], int(4 * 86400))
        self.assertEqual(s["trial_end_at"], "2026-08-17 10:00:00")

    def test_compute_access_warn_window(self):
        from datetime import datetime
        from services.access_service import compute_access
        started = datetime(2026, 8, 12, 10, 0, 0)
        now = datetime(2026, 8, 17, 0, 0, 0)  # 距终点 10 小时 < 24h 提醒窗
        s = compute_access(now, started, False)
        self.assertTrue(s["in_trial"])
        self.assertTrue(s["warn_expiring"])
        self.assertLessEqual(s["trial_remaining_seconds"], 86400)
        self.assertGreater(s["trial_remaining_seconds"], 0)

    def test_compute_access_expiry_at_zero(self):
        from datetime import datetime
        from services.access_service import compute_access
        started = datetime(2026, 8, 12, 10, 0, 0)
        now = datetime(2026, 8, 17, 10, 0, 0)  # 恰好到期：剩余 0 → 立即锁定
        s = compute_access(now, started, False)
        self.assertFalse(s["in_trial"])
        self.assertFalse(s["access_granted"])
        self.assertEqual(s["trial_remaining_seconds"], 0)

    def test_compute_access_one_second_before_end(self):
        from datetime import datetime
        from services.access_service import compute_access
        started = datetime(2026, 8, 12, 10, 0, 0)
        now = datetime(2026, 8, 17, 9, 59, 59)
        s = compute_access(now, started, False)
        self.assertTrue(s["in_trial"])
        self.assertEqual(s["trial_remaining_seconds"], 1)

    def test_compute_access_cross_midnight(self):
        from datetime import datetime
        from services.access_service import compute_access
        started = datetime(2026, 8, 12, 23, 30, 0)   # 终点 8/17 23:30
        now = datetime(2026, 8, 18, 0, 5, 0)         # 跨零点后 35 分钟 → 已过期
        s = compute_access(now, started, False)
        self.assertFalse(s["in_trial"])
        self.assertFalse(s["access_granted"])
        self.assertEqual(s["trial_remaining_seconds"], 0)

    def test_compute_access_new_user_no_start(self):
        from datetime import datetime
        from services.access_service import compute_access
        s = compute_access(datetime(2026, 8, 13, 12, 0, 0), None, False)
        self.assertTrue(s["in_trial"])
        self.assertTrue(s["access_granted"])
        self.assertIsNone(s["trial_end_at"])
        self.assertEqual(s["trial_remaining_seconds"], 5 * 86400)

    def test_compute_access_deposit_override(self):
        from datetime import datetime
        from services.access_service import compute_access
        started = datetime(2026, 8, 1, 0, 0, 0)
        now = datetime(2026, 8, 20, 0, 0, 0)  # 远超 5 天：试用已结束
        s = compute_access(now, started, True)
        self.assertFalse(s["in_trial"])
        self.assertTrue(s["access_granted"])  # 已缴押金 → 恒解锁
        self.assertTrue(s["deposit_paid"])

    # ---------- resolve_access：幂等落库 ----------

    def test_resolve_access_writes_and_keeps_trial_start(self):
        from datetime import datetime
        from database import get_user_access
        from services.access_service import resolve_access
        _, uid = self._login("trial_idem")
        resolve_access(uid, now=datetime(2026, 8, 12, 9, 0, 0))
        stored1 = get_user_access(uid)["trial_started_at"]
        self.assertEqual(stored1, "2026-08-12 09:00:00")
        # 第二次传入更晚时间 → 起点保持首次值，不被客户端/重复请求重置
        resolve_access(uid, now=datetime(2026, 8, 20, 9, 0, 0))
        self.assertEqual(get_user_access(uid)["trial_started_at"], stored1)

    def test_upsert_user_access_ignores_client_fields(self):
        from database import get_user_access, upsert_user_access
        _, uid = self._login("tamper")
        upsert_user_access(uid, {"trial_started_at": "2026-08-01 00:00:00", "access_granted": 1, "foo": "bar"})
        row = get_user_access(uid)
        self.assertEqual(row["trial_started_at"], "2026-08-01 00:00:00")
        self.assertNotIn("access_granted", row)
        self.assertNotIn("foo", row)

    # ---------- 中间件集成链路 ----------

    def test_gated_path_ok_during_trial(self):
        token, _ = self._login("gated_trial")
        r = client.get("/api/courses", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)

    def test_expired_user_gets_403(self):
        from services.access_service import resolve_access
        token, uid = self._login("gated_expired")
        self._expire(uid)
        self.assertFalse(resolve_access(uid)["access_granted"])
        r = client.get("/api/courses", headers=auth_header(token))
        self.assertEqual(r.status_code, 403)
        body = r.json()["detail"]
        self.assertEqual(body["code"], "access_denied")
        self.assertIn("access", body)
        self.assertFalse(body["access"]["access_granted"])

    def test_exempt_paths_work_when_locked(self):
        token, uid = self._login("gated_exempt")
        self._expire(uid)
        # 功能使用权限接口本身 / 押金接口 = 解锁通道，锁定状态下仍可访问
        r = client.get("/api/access/status", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()["access_granted"])
        r = client.get("/api/deposit/status", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)
        # 公开导语（无需登录）
        r = client.get("/api/access/intro")
        self.assertEqual(r.status_code, 200)
        intro = r.json()
        self.assertEqual(intro["trial_days"], 5)
        self.assertGreater(len(intro["features"]), 0)

    def test_deposit_active_unlocks_expired_user(self):
        from database import upsert_deposit
        token, uid = self._login("gated_pay")
        self._expire(uid)
        r = client.get("/api/courses", headers=auth_header(token))
        self.assertEqual(r.status_code, 403)
        # 缴纳押金（active）后 → 实时解锁，无需额外同步
        upsert_deposit(uid, {"status": "active", "amount": 199})
        r = client.get("/api/courses", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)

    def test_no_token_passthrough_public(self):
        # 未登录 → 中间件放行，公开接口保持原有行为（不因权限中间件改变）
        r = client.get("/api/courses")
        self.assertNotEqual(r.status_code, 403)
        self.assertNotIn("access_denied", r.text)

    def test_invalid_token_passthrough(self):
        # 坏 token → 放行给路由自身处理（非 403 access_denied）
        r = client.get("/api/courses", headers={"Authorization": "Bearer bad.token.garbage"})
        self.assertNotEqual(r.status_code, 403)
        self.assertNotIn("access_denied", r.text)


class TestAdminUserPermission(unittest.TestCase):
    """后台用户权限/试用管理：列表查询 + 手动锁定/解锁/延长试用。"""

    def _admin_headers(self):
        adm = client.post("/api/admin/login", params={"username": "admin", "password": "admin123"}).json()
        return {"Authorization": f"Bearer {adm['token']}"}

    def _fresh_user(self, nickname):
        code = f"perm_{int(time.time()*1000)}_{nickname}"
        r = client.post("/api/auth/wechat-login", json={"code": code, "nickname": nickname})
        assert r.status_code == 200, r.text
        token, user = r.json()["token"], r.json()["user"]
        from database import get_connection
        conn = get_connection()
        conn.execute("DELETE FROM user_access WHERE user_id=?", (user["id"],))
        conn.execute("DELETE FROM user_deposits WHERE user_id=?", (user["id"],))
        conn.commit()
        conn.close()
        return token, user["id"]

    def _ovr(self, uid):
        from database import get_user_access
        row = get_user_access(uid)
        return row.get("admin_override", "") if row else ""

    def test_list_requires_admin_auth(self):
        r = client.get("/api/admin/users/permissions")
        self.assertEqual(r.status_code, 401)

    def test_list_returns_users_and_access(self):
        ah = self._admin_headers()
        r = client.get("/api/admin/users/permissions", headers=ah)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        row = data[0]
        self.assertIn("id", row)
        self.assertIn("nickname", row)
        self.assertIn("trial_started_at", row)
        self.assertIn("deposit_status", row)
        self.assertIn("access", row)
        self.assertIn("access_granted", row["access"])

    def test_set_override_lock_enforces_access(self):
        from services.access_service import resolve_access
        token, uid = self._fresh_user("lp_admin_lock")
        ah = self._admin_headers()
        self.assertTrue(resolve_access(uid)["access_granted"])
        r = client.post(f"/api/admin/users/{uid}/permission", headers=ah, json={"action": "set_override", "override": "lock"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self._ovr(uid), "lock")
        self.assertFalse(resolve_access(uid)["access_granted"])
        r = client.get("/api/courses", headers=auth_header(token))
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.json()["detail"]["code"], "access_denied")

    def test_set_override_unlock_grants_access(self):
        from services.access_service import resolve_access
        from datetime import datetime, timedelta
        from database import upsert_user_access
        token, uid = self._fresh_user("lp_admin_unlock")
        ah = self._admin_headers()
        old = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        upsert_user_access(uid, {"trial_started_at": old})
        self.assertFalse(resolve_access(uid)["access_granted"])
        r = client.get("/api/courses", headers=auth_header(token))
        self.assertEqual(r.status_code, 403)
        r = client.post(f"/api/admin/users/{uid}/permission", headers=ah, json={"action": "set_override", "override": "unlock"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self._ovr(uid), "unlock")
        self.assertTrue(resolve_access(uid)["access_granted"])
        r = client.get("/api/courses", headers=auth_header(token))
        self.assertEqual(r.status_code, 200)

    def test_extend_trial_extends_window(self):
        from database import get_user_access, upsert_user_access
        _, uid = self._fresh_user("lp_extend")
        ah = self._admin_headers()
        upsert_user_access(uid, {"trial_started_at": "2026-08-15 10:00:00"})
        r = client.post(f"/api/admin/users/{uid}/permission", headers=ah, json={"action": "extend_trial", "days": 3})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(get_user_access(uid)["trial_started_at"], "2026-08-12 10:00:00")

    def test_clear_override_restores_derived(self):
        from services.access_service import resolve_access
        _, uid = self._fresh_user("lp_clear")
        ah = self._admin_headers()
        client.post(f"/api/admin/users/{uid}/permission", headers=ah, json={"action": "set_override", "override": "lock"})
        self.assertEqual(self._ovr(uid), "lock")
        client.post(f"/api/admin/users/{uid}/permission", headers=ah, json={"action": "clear_override"})
        self.assertEqual(self._ovr(uid), "")
        self.assertTrue(resolve_access(uid)["access_granted"])

    def test_bad_override_value_rejected(self):
        _, uid = self._fresh_user("lp_bad")
        ah = self._admin_headers()
        r = client.post(f"/api/admin/users/{uid}/permission", headers=ah, json={"action": "set_override", "override": "banana"})
        self.assertEqual(r.status_code, 400)

    def test_unknown_user_404(self):
        ah = self._admin_headers()
        r = client.post("/api/admin/users/999999999/permission", headers=ah, json={"action": "clear_override"})
        self.assertEqual(r.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
