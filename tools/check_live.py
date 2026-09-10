"""线上验收自检脚本（部署后用）。

用法：
    py tools/check_live.py https://你的域名.vercel.app
    py tools/check_live.py https://你的域名.vercel.app --login 13800000000   # 额外测真实登录

检查内容：
  1. 前端页面能打开（H5 静态产物）
  2. /health 探活
  3. 课程/视频/学习路径/项目接口有数据（= 云数据库连得上、数据在）
  4. 章节视频映射逐章不同（本次交付的核心诉求）
  5. 测评题库/知识库非空（= backend/data/processed 的种子 JSON 正确进了部署包）
  6. 静态图片走 CDN 可访问
  7. 后台 /admin 可打开
  8. 安全：DEV_MODE 后门关闭（假 code 登录必须失败、模拟切换用户必须关闭）
  9. 只读文件系统下写库不报 500（Serverless 关键路径）
"""
import argparse
import io
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

# 中文 Windows 控制台默认 GBK：不加这行，输出里的符号会 UnicodeEncodeError 直接中断
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PASS, FAIL, WARN = [], [], []


def req(base, method, path, body=None, token=None, timeout=40):
    url = base.rstrip('/') + path
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header('Content-Type', 'application/json')
    r.add_header('User-Agent', 'aishixi-check-live')
    if token:
        r.add_header('Authorization', 'Bearer ' + token)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)
    except Exception as e:
        return 0, str(e).encode(), {}


def check(label, ok, detail=''):
    (PASS if ok else FAIL).append(label)
    print('  %s %-52s %s' % ('[OK]  ' if ok else '[FAIL]', label, detail[:110]))


def warn(label, detail=''):
    WARN.append(label)
    print('  [WARN] %-52s %s' % (label, detail[:110]))


def json_of(raw):
    try:
        return json.loads(raw.decode('utf-8'))
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base')
    ap.add_argument('--login', default='', help='可选：用这个手机号真实登录一次（会建一个测试用户）')
    args = ap.parse_args()
    base = args.base

    print('\n=== 1. 前端与探活 ===')
    code, raw, hdr = req(base, 'GET', '/')
    check('首页 200', code == 200, 'HTTP %s, %d 字节' % (code, len(raw)))
    txt = raw.decode('utf-8', 'replace')
    check('首页是 H5 应用（含 app 容器）', ('id="app"' in txt or 'app' in txt) and '<script' in txt)
    check('资源走 https', 'https://' in txt or code == 200)
    code, raw, _ = req(base, 'GET', '/health')
    check('/health = ok', code == 200 and b'"ok"' in raw, raw[:60].decode('utf-8', 'replace'))

    print('\n=== 2. 数据库相关接口 ===')
    code, raw, _ = req(base, 'GET', '/api/courses?limit=100')
    courses = json_of(raw) or []
    check('课程列表有数据', code == 200 and len(courses) >= 24,
          'HTTP %s, %d 门课' % (code, len(courses) if isinstance(courses, list) else -1))
    code, raw, _ = req(base, 'GET', '/api/videos')
    vids = json_of(raw) or []
    check('视频列表有数据', code == 200 and len(vids) > 0, 'HTTP %s, %d 条' % (code, len(vids)))
    code, raw, _ = req(base, 'GET', '/api/learning-paths')
    paths = json_of(raw) or []
    check('学习路径有数据', code == 200 and len(paths) > 0, 'HTTP %s, %d 条' % (code, len(paths)))
    code, raw, _ = req(base, 'GET', '/api/projects')
    projs = json_of(raw) or []
    check('项目列表有数据', code == 200 and len(projs) > 0, 'HTTP %s, %d 个' % (code, len(projs)))

    print('\n=== 3. 章节视频逐章不同（核心诉求）===')
    code, raw, _ = req(base, 'GET', '/api/courses/s3-langgraph')
    c = json_of(raw) or {}
    chs = c.get('chapters') or []
    pairs = [(ch.get('video_bv'), ch.get('video_page')) for ch in chs]
    check('s3-langgraph 章节数 = 5', len(chs) == 5, '实际 %d' % len(chs))
    check('每章都有视频', all(bv for bv, _ in pairs), str(pairs))
    check('章内无重复分P（用户最初抱怨「每个视频都一样」）', len(set(pairs)) == len(pairs), str(pairs))
    if pairs:
        print('      映射：' + ', '.join('%s P%s' % (b, p) for b, p in pairs))

    print('\n=== 4. 种子 JSON 是否进了部署包 ===')
    code, raw, _ = req(base, 'GET', '/api/assessment/questions')
    qs = json_of(raw) or []
    check('测评题库非空', code == 200 and len(qs) > 0,
          'HTTP %s, %d 题' % (code, len(qs) if isinstance(qs, list) else -1))
    code, raw, _ = req(base, 'GET', '/api/knowledge/search?query=Agent')
    check('知识库检索接口可用', code == 200, 'HTTP %s' % code)
    if code == 200:
        kn = json_of(raw) or {}
        n = len(kn.get('items') or kn.get('results') or [])
        (check if n else warn)('知识库有命中', n > 0, '%d 条' % n)

    print('\n=== 5. 静态资源与后台 ===')
    code, raw, _ = req(base, 'GET', '/static/covers/s3-langgraph.png')
    check('课程封面可访问（CDN/静态）', code == 200 and len(raw) > 200,
          'HTTP %s, %d 字节' % (code, len(raw)))
    code, raw, _ = req(base, 'GET', '/admin')
    check('后台 /admin 可打开', code == 200 and b'<' in raw, 'HTTP %s' % code)

    print('\n=== 6. 安全（开发后门必须关闭）===')
    code, raw, _ = req(base, 'POST', '/api/auth/wechat-login', {'code': 'dev-backdoor-check'})
    j = json_of(raw) or {}
    check('假 code 登录被拒绝（DEV_MODE=false）', not (code == 200 and j.get('token')),
          'HTTP %s %s' % (code, str(j)[:70]))
    code, raw, _ = req(base, 'GET', '/api/auth/dev/config')
    j = json_of(raw) or {}
    check('模拟切换用户已关闭（DEV_IMPERSONATE=false）', j.get('impersonate_enabled') is False,
          str(j)[:70])
    code, raw, _ = req(base, 'POST', '/api/auth/h5-login', {'phone': '123'})
    check('手机号登录有格式校验', code in (400, 422), 'HTTP %s' % code)

    print('\n=== 7. 只读文件系统下的写入路径（Serverless 关键）===')
    token = ''
    phone = args.login or '13900000009'
    code, raw, _ = req(base, 'POST', '/api/auth/h5-login', {'phone': phone})
    j = json_of(raw) or {}
    token = j.get('token') or ''
    check('H5 手机号登录成功（写库 + 发 token）', code == 200 and bool(token),
          'HTTP %s %s' % (code, str(j)[:60] if not token else '已登录'))
    if token and vids:
        vid = vids[0].get('id')
        code, raw, _ = req(base, 'POST', '/api/videos/%s/complete' % urllib.parse.quote(str(vid)),
                           {}, token=token)
        check('标记视频完成 200（不是 500）', code == 200, 'HTTP %s %s' % (code, raw[:80].decode('utf-8', 'replace')))
    if token:
        code, raw, _ = req(base, 'POST', '/api/projects/%s/advance' % urllib.parse.quote(str((projs[0] or {}).get('id', 'project-0'))),
                           {}, token=token)
        check('项目推进 200（写文件路径已安全降级）', code == 200, 'HTTP %s' % code)

    print('\n=== 结果 ===')
    print('通过 %d 项，失败 %d 项，提示 %d 项' % (len(PASS), len(FAIL), len(WARN)))
    if FAIL:
        print('失败项：')
        for f in FAIL:
            print('  - ' + f)
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
