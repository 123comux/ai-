"""Course knowledge base: retrieve relevant course content for RAG.

Uses lightweight keyword/topic matching over course content (no embedding model
download needed, works offline). Returns a text context block for the LLM.
"""

import json
from pathlib import Path

from config import PROCESSED_DIR


def _load_courses() -> list[dict]:
    path = PROCESSED_DIR / "enriched_courses.json"
    if not path.exists():
        path = PROCESSED_DIR / "courses.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _all_chunks() -> list[dict]:
    """Flatten course content into (text, meta) chunks."""
    chunks = []
    for course in _load_courses():
        course_title = course.get("title", "")
        course_desc = course.get("description", "")
        if course_desc:
            chunks.append({
                "text": f"课程《{course_title}》介绍：{course_desc}",
                "meta": {"type": "课程介绍", "course": course_title},
            })
        for ch in course.get("chapters", []):
            ch_title = ch.get("title", "")
            summary = ch.get("summary", "")
            if summary:
                chunks.append({
                    "text": f"《{course_title}》章节《{ch_title}》：{summary}",
                    "meta": {"type": "章节", "course": course_title, "chapter": ch_title},
                })
            for sec in ch.get("sections", []):
                sec_title = sec.get("title", "")
                content = sec.get("content", "")
                kps = "；".join(sec.get("knowledge_points", []))
                case = sec.get("case", "")
                text = f"《{course_title}》{ch_title} · {sec_title}"
                if content:
                    text += f"\n内容：{content}"
                if kps:
                    text += f"\n核心知识点：{kps}"
                if case:
                    text += f"\n实战案例：{case}"
                chunks.append({
                    "text": text,
                    "meta": {"type": "小节", "course": course_title, "chapter": ch_title, "section": sec_title},
                })

    # 补充知识库：更详细的主题知识点（course_knowledge.json）
    extra_path = PROCESSED_DIR / "course_knowledge.json"
    if extra_path.exists():
        with open(extra_path, "r", encoding="utf-8") as f:
            extra = json.load(f)
        for item in extra:
            if isinstance(item, dict) and item.get("content"):
                keywords = item.get("keywords", [])
                # 关键词拼进文本，便于检索评分命中
                kw_text = " ".join(keywords) if keywords else ""
                chunks.append({
                    "text": (kw_text + "\n" + item["content"]).strip(),
                    "meta": {"type": "知识点", "topic": item.get("topic", ""), "keywords": keywords},
                })
    return chunks


# 中文检索关键词：把常见问题映射到课程主题
_TOPIC_ALIASES = [
    ("python", ["python", "编程", "变量", "函数", "面向对象", "语法"]),
    ("机器学习", ["机器学习", "回归", "分类", "决策树", "监督", "无监督", "模型评估"]),
    ("深度学习", ["深度学习", "神经网络", "cnn", "rnn", "transformer", "卷积", "循环"]),
    ("大模型", ["大模型", "llm", "prompt", "提示词", "rag", "agent", "微调", "lora"]),
    ("自然语言", ["nlp", "自然语言", "词向量", "bert", "文本", "分词"]),
    ("数据科学", ["数据分析", "数据科学", "pandas", "可视化", "特征工程", "统计"]),
    ("计算机视觉", ["计算机视觉", "图像", "目标检测", "opencv", "cnn"]),
    ("强化学习", ["强化学习", "q-learning", "dqn", "策略"]),
]


def _score_question(question: str, chunk_text: str, meta: dict | None = None) -> int:
    """Score how relevant a chunk is to the question (0 = not relevant)."""
    import re
    q = question.lower()
    score = 0

    # 1. 若该块是补充知识点，且问题命中其关键词 → 高分
    if meta and meta.get("keywords"):
        kw = [k.lower() for k in meta["keywords"] if k]
        if any(k in q for k in kw):
            score += 10
        # 问题字面词与关键词重合
        hit_kw = sum(1 for k in kw if k in q)
        score += hit_kw * 2

    # 2. 主题关键词命中（课程块）
    for topic, keywords in _TOPIC_ALIASES:
        if any(k in q for k in keywords):
            if any(k in chunk_text.lower() for k in keywords):
                score += 2

    # 3. 问题里的中文词（2+ 字）出现在 chunk 中
    tokens = set(re.findall(r"[一-龥]{2,}", q))
    if tokens:
        hit = sum(1 for t in tokens if t in chunk_text)
        score += hit

    return score


def retrieve_context(question: str, k: int = 4) -> str:
    """Search course knowledge base and return a text context block."""
    try:
        chunks = _all_chunks()
        scored = [(c, _score_question(question, c["text"], c.get("meta"))) for c in chunks]
        scored = [x for x in scored if x[1] > 0]
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:k]
        if not top:
            return ""
        return "\n\n".join(f"【{c['meta'].get('type', '')}】{c['text']}" for c, s in top)
    except Exception:
        return ""


def count_chunks() -> int:
    """Number of content chunks in the knowledge base."""
    return len(_all_chunks())
