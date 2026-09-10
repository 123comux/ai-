"""把章节 → 视频 的精确映射写入数据库与 processed 数据（可重复执行）。

用法：cd backend && python apply_video_mapping.py

做三件事：
1. cms.db → courses.chapters[*].video_bv / video_page（章节页播放器读这两个字段）；
2. cms.db → videos 表：把 24 条占位记录换成真实合集的对应分P，并绑上章节 id；
   全部章节都缺素材的课程（全部 PENDING）则置空并停用，视频页显示「暂无视频」；
3. data/processed/videos.json 同步（保持 JSON 与 DB 一致）。

映射来源：data_pipeline/video_mapping.py（由已评审的 docs/video-mapping-draft.md 生成）。
"""
import json
import os
import sqlite3
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from data_pipeline.video_mapping import VIDEO_MAP, PENDING, player_url  # noqa: E402

DB_PATH = os.path.join(BASE, "data", "cms.db")
VIDEOS_JSON = os.path.join(BASE, "data", "processed", "videos.json")


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # ---------- 1) 课程章节 ----------
    mapped = pending = untouched = 0
    first_chapter_of_course = {}
    for row in conn.execute("SELECT id, chapters FROM courses"):
        course_id = row["id"]
        chapters = json.loads(row["chapters"] or "[]")
        for ch in chapters:
            cid = ch.get("id")
            if cid in VIDEO_MAP:
                bv, page = VIDEO_MAP[cid]
                ch["video_bv"], ch["video_page"] = bv, page
                mapped += 1
                first_chapter_of_course.setdefault(course_id, (cid, ch.get("title", ""), bv, page))
            elif cid in PENDING:
                ch["video_bv"], ch["video_page"] = "", 1
                pending += 1
            else:
                untouched += 1
        conn.execute("UPDATE courses SET chapters=? WHERE id=?",
                     (json.dumps(chapters, ensure_ascii=False), course_id))
    conn.commit()
    print(f"[chapters] 精确映射 {mapped} 条 / 待补充 {pending} 条 / 未覆盖 {untouched} 条")

    # ---------- 2) videos 表 ----------
    video_rows = conn.execute("SELECT id, course_id, title FROM videos").fetchall()
    updated = disabled = 0
    for v in video_rows:
        hit = first_chapter_of_course.get(v["course_id"])
        if hit:
            cid, ch_title, bv, page = hit
            conn.execute(
                "UPDATE videos SET url=?, chapter=?, subtitle=?, is_active=1 WHERE id=?",
                (player_url(bv, page), cid, f"{bv} P{page} · 对应章节：{ch_title}", v["id"]),
            )
            updated += 1
        else:
            conn.execute(
                "UPDATE videos SET url='', chapter='', subtitle='视频待补充（现有素材暂无对应内容）', is_active=0 WHERE id=?",
                (v["id"],),
            )
            disabled += 1
    conn.commit()
    print(f"[videos]   已换成真实分P {updated} 条 / 停用（缺素材）{disabled} 条")

    # ---------- 3) 同步 videos.json ----------
    if os.path.exists(VIDEOS_JSON):
        with open(VIDEOS_JSON, "r", encoding="utf-8") as f:
            videos = json.load(f)
        for item in videos:
            hit = first_chapter_of_course.get(item.get("courseId"))
            if hit:
                cid, ch_title, bv, page = hit
                item["url"] = player_url(bv, page)
                item["chapter"] = cid
                item["subtitle"] = f"{bv} P{page} · 对应章节：{ch_title}"
            else:
                item["url"] = ""
                item["chapter"] = ""
                item["subtitle"] = "视频待补充（现有素材暂无对应内容）"
        with open(VIDEOS_JSON, "w", encoding="utf-8") as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)
        print(f"[json]     videos.json 已同步 {len(videos)} 条")

    # ---------- 4) 校验 ----------
    distinct_bv = set()
    page_gt1 = 0
    empty = 0
    total = 0
    for row in conn.execute("SELECT chapters FROM courses"):
        for ch in json.loads(row["chapters"] or "[]"):
            total += 1
            if ch.get("video_bv"):
                distinct_bv.add(ch["video_bv"])
                if int(ch.get("video_page") or 1) > 1:
                    page_gt1 += 1
            else:
                empty += 1
    print(f"[verify]   章节 {total} 个｜有视频 {total - empty}｜无视频(待补) {empty}"
          f"｜不同 BV {len(distinct_bv)}｜分P>1 的章节 {page_gt1}")
    conn.close()


if __name__ == "__main__":
    main()
