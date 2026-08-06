"""
Data enrichment pipeline - reads seed data and adds frontend-oriented display fields.

Generates:
  - enriched_courses.json        (with coverImg, category, isFree, progress, etc.)
  - enriched_projects.json       (with coverImg, stepCount, status, isFree, etc.)
  - enriched_learning_paths.json (with currentWeek, node status/progress, etc.)
  - ability_report.json          (能力报告)
  - learning_records.json        (学习记录 - 过去30天)
  - job_matching.json            (岗位对标)
  - learning_stats.json          (学习统计)
  - videos.json                  (课程视频数据)

Usage:
    python -m backend.data_pipeline.enrich_data
"""

import json
import sys
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PROCESSED_DIR

random.seed(42)

# ============================================================
# Chinese translations for topics/categories
# ============================================================

TOPIC_CN = {
    "Machine Learning": "机器学习",
    "Deep Learning": "深度学习",
    "Large Language Models": "大语言模型",
    "Natural Language Processing": "自然语言处理",
    "Data Science": "数据科学",
    "Python": "Python编程",
    "Computer Vision": "计算机视觉",
    "Reinforcement Learning": "强化学习",
}

CATEGORY_MAP = {
    "Machine Learning": "机器学习",
    "Deep Learning": "深度学习",
    "Large Language Models": "大模型",
    "Natural Language Processing": "自然语言处理",
    "Data Science": "数据分析",
    "Python": "编程基础",
    "Computer Vision": "计算机视觉",
    "Reinforcement Learning": "强化学习",
}

DIFFICULTY_CN = {
    "beginner": "入门",
    "intermediate": "进阶",
    "advanced": "高级",
}

# Course Chinese titles and descriptions
COURSE_CN = {
    "course-0": {
        "title": "机器学习入门",
        "description": "掌握监督学习、无监督学习、模型评估核心方法",
        "category": "机器学习",
        "isFree": True,
    },
    "course-1": {
        "title": "深度学习与神经网络",
        "description": "CNN、RNN、Transformer 架构原理与实践",
        "category": "深度学习",
        "isFree": False,
    },
    "course-2": {
        "title": "大模型应用开发",
        "description": "Prompt Engineering、RAG、Agent 开发实战",
        "category": "大模型",
        "isFree": False,
    },
    "course-3": {
        "title": "自然语言处理实战",
        "description": "文本预处理、词嵌入、序列模型全流程",
        "category": "自然语言处理",
        "isFree": True,
    },
    "course-4": {
        "title": "数据分析与可视化",
        "description": "Pandas、Matplotlib、Seaborn 数据分析和可视化",
        "category": "数据分析",
        "isFree": True,
    },
    "course-5": {
        "title": "Python 编程基础",
        "description": "从零开始学习 Python 语法、数据结构与算法",
        "category": "编程基础",
        "isFree": True,
    },
    "course-6": {
        "title": "计算机视觉入门",
        "description": "图像处理、目标检测、图像分割技术",
        "category": "计算机视觉",
        "isFree": False,
    },
    "course-7": {
        "title": "强化学习基础",
        "description": "Q-learning、DQN、Policy Gradients 原理与实践",
        "category": "强化学习",
        "isFree": True,
    },
}

# Project Chinese titles and descriptions
PROJECT_CN = {
    "project-0": {
        "title": "图像分类 CNN 项目",
        "description": "使用 PyTorch 构建 CIFAR-10 图像分类器，实现数据增强、批归一化和 Dropout",
        "isFree": True,
        "price": 0,
        "status": "available",
    },
    "project-1": {
        "title": "BERT 情感分析系统",
        "description": "微调 BERT 模型进行电影评论情感分类，实现完整训练与评估流程",
        "isFree": True,
        "price": 0,
        "status": "available",
    },
    "project-2": {
        "title": "RAG 知识库问答系统",
        "description": "使用 LangChain、ChromaDB 构建检索增强生成系统，实现文档分块、嵌入和查询",
        "isFree": False,
        "price": 399,
        "status": "locked",
    },
    "project-3": {
        "title": "客户流失预测系统",
        "description": "构建 ML 流水线预测客户流失，包含 EDA、特征工程、模型选择和 FastAPI 部署",
        "isFree": True,
        "price": 0,
        "status": "available",
    },
    "project-4": {
        "title": "实时目标检测系统",
        "description": "实现 YOLOv8 实时视频流目标检测，优化推理速度并使用 Docker 部署",
        "isFree": False,
        "price": 299,
        "status": "locked",
    },
    "project-5": {
        "title": "大模型微调实战",
        "description": "使用 LoRA 微调 LLaMA 模型，实现自定义指令跟随数据集的训练与推理",
        "isFree": False,
        "price": 499,
        "status": "locked",
    },
    "project-6": {
        "title": "时间序列预测系统",
        "description": "基于 LSTM 的股票价格/天气预测，包含数据预处理、模型训练和可视化",
        "isFree": True,
        "price": 0,
        "status": "available",
    },
    "project-7": {
        "title": "推荐系统 Demo",
        "description": "使用矩阵分解和神经方法构建协同过滤推荐系统",
        "isFree": True,
        "price": 0,
        "status": "available",
    },
    "project-8": {
        "title": "AI 聊天机器人",
        "description": "使用 LangChain 构建带记忆和工具调用的对话式 AI 聊天机器人",
        "isFree": True,
        "price": 0,
        "status": "available",
    },
    "project-9": {
        "title": "数据 ETL 流水线",
        "description": "构建自动化 ETL 流水线，实现数据提取、转换和加载，包含数据验证和监控",
        "isFree": True,
        "price": 0,
        "status": "available",
    },
}

# Learning path Chinese titles and descriptions
PATH_CN = {
    "path-0": {
        "direction": "AI 工程师",
        "title": "AI 工程师学习路径",
    },
    "path-1": {
        "direction": "机器学习工程师",
        "title": "机器学习工程师学习路径",
    },
    "path-2": {
        "direction": "数据科学家",
        "title": "数据科学家学习路径",
    },
    "path-3": {
        "direction": "AI 后端开发工程师",
        "title": "AI 后端开发工程师学习路径",
    },
}

# ============================================================
# Helper functions
# ============================================================

def load_json(filename):
    path = PROCESSED_DIR / filename
    if not path.exists():
        print(f"  ⚠ File not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filename, data):
    path = PROCESSED_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ {filename} ({len(data) if isinstance(data, list) else 'object'}) → {path}")


def gen_cover(seed_id):
    return f"https://picsum.photos/seed/{seed_id}/300/200"


# ============================================================
# 1. Enrich courses
# ============================================================

def enrich_courses(courses):
    enriched = []
    for c in courses:
        cid = c["id"]
        cn_info = COURSE_CN.get(cid, {})
        total_minutes = sum(ch.get("duration_minutes", 0) for ch in c.get("chapters", []))
        num_lessons = len(c.get("chapters", []))
        # Simulate progress: some courses have progress, some don't
        progress = random.choice([0, 0, 0, 20, 45, 60, 80, 100])

        enriched.append({
            "id": cid,
            "title": cn_info.get("title", c["title"]),
            "enTitle": c["title"],
            "description": cn_info.get("description", c["description"]),
            "enDescription": c["description"],
            "coverImg": gen_cover(cid),
            "duration": total_minutes,
            "lessons": num_lessons,
            "progress": progress,
            "category": cn_info.get("category", CATEGORY_MAP.get(c.get("topic", ""), c.get("topic", ""))),
            "isFree": cn_info.get("isFree", True),
            "topic": c.get("topic", ""),
            "difficulty": c.get("difficulty", "intermediate"),
            "estimated_hours": c.get("estimated_hours", 0),
            "source": c.get("source", ""),
            "chapters": c.get("chapters", []),
        })
    return enriched


# ============================================================
# 2. Enrich projects
# ============================================================

def enrich_projects(projects):
    enriched = []
    for p in projects:
        pid = p["id"]
        cn_info = PROJECT_CN.get(pid, {})
        step_count = random.randint(4, 10)
        progress = 0
        status = cn_info.get("status", "available")
        if status == "available" and random.random() < 0.3:
            status = random.choice(["in_progress", "completed"])
            progress = random.randint(30, 100) if status == "in_progress" else 100

        enriched.append({
            "id": pid,
            "title": cn_info.get("title", p["title"]),
            "enTitle": p["title"],
            "description": cn_info.get("description", p["description"]),
            "enDescription": p["description"],
            "coverImg": gen_cover(pid),
            "techStack": p.get("tech_stack", []),
            "difficulty": p.get("difficulty", "intermediate"),
            "estimatedHours": p.get("estimated_hours", 0),
            "stepCount": step_count,
            "status": status,
            "progress": progress,
            "isFree": cn_info.get("isFree", True),
            "price": cn_info.get("price", 0),
            "topics_covered": p.get("topics_covered", []),
            "source": p.get("source", ""),
        })
    return enriched


# ============================================================
# 3. Enrich learning paths
# ============================================================

def enrich_learning_paths(paths, courses, projects):
    # Build lookup maps
    course_titles = {c["id"]: c["title"] for c in courses}
    project_titles = {p["id"]: p["title"] for p in projects}

    enriched = []
    now = datetime.now()
    week_start = now - timedelta(days=now.weekday() * 7)

    for i, lp in enumerate(paths):
        lpid = lp["id"]
        cn_info = PATH_CN.get(lpid, {})
        current_week = random.randint(0, max(1, lp.get("total_weeks", 8) - 2))

        nodes = []
        for node in lp.get("nodes", []):
            nid = node["id"]
            node_type = node.get("type", "course")
            item_ids = node.get("items", [])

            # Determine status based on position
            node_idx = lp["nodes"].index(node)
            total_nodes = len(lp["nodes"])
            if node_idx < current_week:
                node_status = "completed"
                node_progress = 100
            elif node_idx == current_week:
                node_status = "current"
                node_progress = random.randint(30, 80)
            else:
                node_status = "locked"
                node_progress = 0

            # Get courseId for course-type nodes
            course_id = None
            if node_type == "course" and item_ids:
                course_id = item_ids[0]
            elif node_type == "project" and item_ids:
                course_id = None

            # Node title
            base_title = node.get("title", "")
            if node_type == "course" and course_id and course_id in course_titles:
                base_title = course_titles[course_id]

            nodes.append({
                "id": nid,
                "title": base_title,
                "type": node_type,
                "status": node_status,
                "progress": node_progress,
                "courseId": course_id,
            })

        # Created at a few weeks ago
        created_at = (week_start - timedelta(weeks=lp.get("total_weeks", 8) - current_week)).strftime("%Y-%m-%d")

        enriched.append({
            "id": lpid,
            "direction": cn_info.get("direction", lp.get("direction", "")),
            "title": cn_info.get("title", lp.get("title", "")),
            "totalWeeks": lp.get("total_weeks", 0),
            "currentWeek": current_week,
            "nodes": nodes,
            "createdAt": created_at,
        })

    return enriched


# ============================================================
# 4. Generate ability report
# ============================================================

def generate_ability_report():
    dimensions = [
        {"label": "Python 基础", "score": 75, "maxScore": 100},
        {"label": "数学基础", "score": 60, "maxScore": 100},
        {"label": "机器学习", "score": 45, "maxScore": 100},
        {"label": "深度学习", "score": 35, "maxScore": 100},
        {"label": "大模型应用", "score": 50, "maxScore": 100},
        {"label": "项目经验", "score": 30, "maxScore": 100},
    ]
    overall = int(sum(d["score"] for d in dimensions) / len(dimensions))

    level = "初级"
    if overall >= 80:
        level = "高级"
    elif overall >= 50:
        level = "中级"

    return {
        "overallScore": overall,
        "level": level,
        "dimensions": dimensions,
        "strengths": ["Python 语法基础扎实", "基本数据结构和算法掌握较好"],
        "weaknesses": ["深度学习理论薄弱", "缺少真实项目经验", "大模型应用实践不足"],
        "recommendedDirection": "大模型应用开发",
        "estimatedHours": 120,
    }


# ============================================================
# 5. Generate learning records (past 30 days)
# ============================================================

def generate_learning_records():
    records = []
    today = datetime.now()
    for i in range(30):
        day = today - timedelta(days=29 - i)
        # Simulate some days without study
        if random.random() < 0.15:
            continue
        duration = random.randint(20, 120)
        lessons = max(1, round(duration / 25))
        exercises = max(1, round(duration / 6))
        records.append({
            "date": day.strftime("%m-%d"),
            "duration": duration,
            "lessonsCompleted": lessons,
            "exercisesDone": exercises,
        })
    return records


# ============================================================
# 6. Generate job matching data
# ============================================================

def generate_job_matching(courses, projects):
    course_titles = [c["title"] for c in courses]
    project_titles = [p["title"] for p in projects]

    # Pick some course/project titles for recommendations
    rec_courses = random.sample(course_titles, min(3, len(course_titles)))
    rec_projects = random.sample(project_titles, min(2, len(project_titles)))

    return {
        "jobTitle": "AI 应用开发实习生",
        "company": "某科技公司",
        "matchScore": 68,
        "requiredSkills": [
            {"name": "Python", "mastered": True},
            {"name": "大模型 API 调用", "mastered": True},
            {"name": "RAG 系统", "mastered": False},
            {"name": "Agent 开发", "mastered": False},
            {"name": "SQL", "mastered": True},
            {"name": "数据结构与算法", "mastered": True},
        ],
        "gapSkills": ["RAG 系统搭建", "Agent 智能体开发", "微服务架构"],
        "recommendedCourses": rec_courses[:2],
        "recommendedProjects": rec_projects[:2],
    }


# ============================================================
# 7. Generate learning stats
# ============================================================

def generate_learning_stats():
    return {
        "learningDays": 18,
        "totalHours": 36,
        "completedProjects": 2,
        "completedLessons": 15,
    }


# ============================================================
# 8. Generate videos data
# ============================================================

def generate_videos(courses):
    """Generate video entries for each chapter of each course."""
    video_urls = [
        "https://www.w3schools.com/html/mov_bbb.mp4",
        "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4",
    ]
    videos = []
    vid_counter = 1

    for course in courses:
        cid = course["id"]
        for chapter in course.get("chapters", []):
            ch_id = chapter["id"]
            url = video_urls[(vid_counter - 1) % len(video_urls)]
            duration_seconds = chapter.get("duration_minutes", 45) * 60
            videos.append({
                "id": f"video-{vid_counter}",
                "title": chapter.get("title", f"Chapter {vid_counter}"),
                "description": chapter.get("content_summary", ""),
                "url": url,
                "coverUrl": gen_cover(f"video-{vid_counter}"),
                "duration": duration_seconds,
                "chapter": ch_id,
                "courseId": cid,
            })
            vid_counter += 1

    return videos


# ============================================================
# Main
# ============================================================

def run():
    print("=" * 60)
    print("Enriching seed data with frontend display fields")
    print("=" * 60)

    # Load existing seed data
    courses = load_json("courses.json")
    projects = load_json("projects.json")
    learning_paths = load_json("learning_paths.json")

    if not courses:
        print("  ⚠ No courses found. Run seed_data first.")
        return
    if not projects:
        print("  ⚠ No projects found. Run seed_data first.")
        return
    if not learning_paths:
        print("  ⚠ No learning paths found. Run seed_data first.")
        return

    # Enrich data
    enriched_courses = enrich_courses(courses)
    enriched_projects = enrich_projects(projects)
    enriched_paths = enrich_learning_paths(learning_paths, enriched_courses, enriched_projects)

    # Generate new data
    ability_report = generate_ability_report()
    learning_records = generate_learning_records()
    job_matching = generate_job_matching(enriched_courses, enriched_projects)
    learning_stats = generate_learning_stats()
    videos = generate_videos(courses)

    # Save all enriched data
    save_json("enriched_courses.json", enriched_courses)
    save_json("enriched_projects.json", enriched_projects)
    save_json("enriched_learning_paths.json", enriched_paths)
    save_json("ability_report.json", ability_report)
    save_json("learning_records.json", learning_records)
    save_json("job_matching.json", job_matching)
    save_json("learning_stats.json", learning_stats)
    save_json("videos.json", videos)

    print("\n" + "=" * 60)
    print("Enrichment complete!")
    print(f"  Courses: {len(enriched_courses)} enriched")
    print(f"  Projects: {len(enriched_projects)} enriched")
    print(f"  Learning paths: {len(enriched_paths)} enriched")
    print(f"  Videos: {len(videos)} generated")
    print(f"  Learning records: {len(learning_records)} days")
    print("=" * 60)


if __name__ == "__main__":
    run()