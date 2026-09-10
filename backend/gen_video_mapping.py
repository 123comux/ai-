"""从已评审的映射表生成权威映射模块。

用法（在 backend/ 下执行）：
    cd backend
    py gen_video_mapping.py            # 生成 + 校验
    py gen_video_mapping.py --check    # 只校验，不写文件

数据流（单一事实来源 = 文档）：
    docs/video-mapping-draft.md   --解析-->   backend/data_pipeline/video_mapping.py

文档表格每行格式：
    | `chapter_id` | 章节标题 | `BV1xxxxxxxxx` | P12 | 分P标题 | 12m34s | 匹配说明 |
    | `chapter_id` | 章节标题 | **待补** | — | — | — | 说明 |      ← 未找到素材

校验项（任一不过即非 0 退出）：
    1. 文档中每个章节 id 只出现一次，且都归属某个 `### course-id ｜ ...` 小节；
    2. **同一门课内**不得有两个章节指向同一 (BV, 分P)——这正是用户反馈过的
       「每个视频都一样」；跨课程复用只告警（大合集服务两门课是允许的）；
    3. 若 backend/data/cms.db 存在，则章节集合必须与库里完全一致。
"""
import io
import json
import os
import re
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(ROOT, 'docs', 'video-mapping-draft.md')
OUT = os.path.join(ROOT, 'backend', 'data_pipeline', 'video_mapping.py')
DB = os.path.join(ROOT, 'backend', 'data', 'cms.db')

COURSE_RE = re.compile(r'^###\s+([a-z0-9\-]+)\s*[｜|]')
ROW_RE = re.compile(
    r'^\|\s*`([a-z0-9\-]+)`\s*\|\s*(.+?)\s*\|\s*(?:`(BV[0-9A-Za-z]+)`\s*\|\s*P(\d+)|(\*\*待补\*\*))\s*\|')

HEADER = '''"""章节 → B 站视频 的权威映射（由 docs/video-mapping-draft.md 自动生成，勿手改）。

背景：原先每门课只配一个 BV、且 video_page 恒为 1，导致同一阶段所有章节播放同一集
（用户反馈「每个视频都是一样的」）。这里逐章指定真实合集的**具体分P**。

生成方式：`cd backend && py gen_video_mapping.py`（读取已评审的映射表 md）。
覆盖情况见模块尾部 `_STATS`；未列入 VIDEO_MAP 的章节视为「视频待补充」，
会清空 video_bv，页面显示待补充提示（当前为 0 条）。
"""

from typing import Dict, List, Tuple

# 章节 id -> (B 站 BV 号, 分P 序号)
VIDEO_MAP: Dict[str, Tuple[str, int]] = {
'''

FOOT = '''

# 现有素材中确实没有对应内容、需要客户补充链接的章节（当前为空 = 已 100%% 覆盖）
PENDING: List[str] = [
%s]

# 由生成器写入，便于快速核对：{总章节数, 已映射数, 待补数}
_STATS = {"chapters": %d, "mapped": %d, "pending": %d}


def player_url(bv: str, page: int = 1) -> str:
    """可嵌入播放器的地址（含分P），视频页/章节页统一用它。"""
    return f"https://player.bilibili.com/player.html?bvid={bv}&page={page}"


def apply_video_mapping(courses: list) -> Tuple[int, int]:
    """把 VIDEO_MAP 写到课程章节上。

    - 命中映射：写入 video_bv + video_page；
    - 命中 PENDING：清空 video_bv（页面显示「视频待补充」，不再拿别的视频冒充）；
    - 两者都未命中：保持原样（交给调用方决定兜底策略）。
    返回 (已映射数, 待补充数)。
    """
    mapped = pending = 0
    for co in courses or []:
        for ch in co.get("chapters", []) or []:
            cid = ch.get("id")
            if cid in VIDEO_MAP:
                bv, page = VIDEO_MAP[cid]
                ch["video_bv"] = bv
                ch["video_page"] = page
                mapped += 1
            elif cid in PENDING:
                ch["video_bv"] = ""
                ch["video_page"] = 1
                pending += 1
    return mapped, pending
'''


def parse_md():
    with io.open(MD, encoding='utf-8') as f:
        lines = f.read().split('\n')
    rows = []
    course = None
    for ln in lines:
        m = COURSE_RE.match(ln)
        if m:
            course = m.group(1)
            continue
        m = ROW_RE.match(ln)
        if not m:
            continue
        cid, title, bv, page, pend = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        rows.append({'course': course, 'id': cid, 'title': title,
                     'bv': bv, 'page': int(page) if page else None,
                     'pending': bool(pend)})
    return rows


def validate(rows):
    errs = []
    warns = []
    seen = {}
    for r in rows:
        if r['course'] is None:
            errs.append('章节 %s 不在任何课程小节下' % r['id'])
        if r['id'] in seen:
            errs.append('章节 id 重复：%s' % r['id'])
        seen[r['id']] = r
    used = {}
    course_of = {}
    for r in rows:
        if r['pending'] or not r['bv']:
            continue
        key = (r['bv'], r['page'])
        if key in used:
            msg = '(BV,分P) 复用：%s P%s ← %s 与 %s' % (r['bv'], r['page'], used[key], r['id'])
            if course_of[key] == r['course']:
                errs.append('同一课程内 ' + msg)
            else:
                warns.append('跨课程 ' + msg)
        used[key] = r['id']
        course_of[key] = r['course']
    if os.path.exists(DB):
        con = sqlite3.connect(DB)
        db_ids = set()
        for (chapters,) in con.execute('select chapters from courses'):
            for ch in json.loads(chapters or '[]'):
                db_ids.add(ch.get('id'))
        con.close()
        only_md = set(seen) - db_ids
        only_db = db_ids - set(seen)
        if only_md:
            errs.append('文档里有、库里没有的章节：%s' % sorted(only_md))
        if only_db:
            errs.append('库里有、文档里没有的章节：%s' % sorted(only_db))
    return errs, warns, seen, used


def render(rows):
    body = []
    course = object()
    for r in rows:
        if r['course'] != course:
            course = r['course']
            body.append('    # ---- %s ----' % course)
        if r['pending']:
            continue
        body.append('    "%s": ("%s", %d),  # %s' % (r['id'], r['bv'], r['page'], r['title']))
    pending = [r['id'] for r in rows if r['pending']]
    pend_lines = ''.join('    "%s",\n' % p for p in pending)
    text = HEADER + '\n'.join(body) + '\n}' + (
        FOOT % (pend_lines, len(rows), len(rows) - len(pending), len(pending)))
    return text


def main():
    check_only = '--check' in sys.argv[1:]
    rows = parse_md()
    if not rows:
        print('未从 %s 解析到任何章节行' % MD)
        return 1
    errs, warns, seen, used = validate(rows)
    if errs:
        print('校验未通过：')
        for e in errs:
            print('  - ' + e)
        return 1
    pending = [r['id'] for r in rows if r['pending']]
    print('解析章节 %d 个（课程 %d 门）｜唯一 (BV,分P) %d 组｜待补 %d 个'
          % (len(rows), len({r['course'] for r in rows}), len(used), len(pending)))
    for w in warns:
        print('  [提示] ' + w)
    if check_only:
        print('校验通过（--check 不写文件）')
        return 0
    text = render(rows)
    old = ''
    if os.path.exists(OUT):
        with io.open(OUT, encoding='utf-8') as f:
            old = f.read()
    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('%s %s' % ('未变化：' if old == text else '已写入：', OUT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
