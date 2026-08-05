"""
Preprocessing pipeline.

Extracts AI/ML/CS specific content from raw datasets and structures it
into knowledge base entries, assessment questions, courses, and projects.

Usage:
    python -m backend.data_pipeline.preprocess
"""

import json
import re
import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DIR, PROCESSED_DIR

# ---- AI/ML/CS topic keywords (for filtering) ----
AI_TOPIC_KEYWORDS = [
    # Machine Learning
    r"\bmachine learning\b", r"\bdeep learning\b", r"\bneural network", r"\bCNN\b", r"\bRNN\b",
    r"\btransformer\b", r"\battention mechanism", r"\bbackpropagation", r"\bgradient descent",
    r"\breinforcement learning", r"\bsupervised learning", r"\bunsupervised learning",
    r"\bregression\b", r"\bclassification\b", r"\bclustering\b", r"\bdimensionality reduction",
    r"\bPCA\b", r"\bt-SNE\b", r"\bautoencoder", r"\bGAN\b", r"\bdiffusion model",
    # AI / LLM
    r"\bartificial intelligence", r"\blarge language model", r"\bLLM\b",
    r"\bGPT\b", r"\bBERT\b", r"\bT5\b", r"\bprompt engineering", r"\bfine.?tun",
    r"\bRAG\b", r"\bretrieval augmented", r"\bagent\b", r"\bmulti.?modal",
    # Data Science
    r"\bdata science", r"\bdata mining", r"\bstochastic", r"\bstatistical",
    r"\bprobability\b", r"\bbayesian", r"\bhypothesis test",
    # Python / Programming
    r"\bpython\b", r"\btensorflow\b", r"\bpytorch\b", r"\bscikit.?learn",
    r"\bnumpy\b", r"\bpandas\b", r"\bjupyter\b", r"\bAPI\b", r"\bREST\b",
    r"\balgorithm\b", r"\bdata structure", r"\btime complexity", r"\bspace complexity",
    # General CS
    r"\bcomputer science", r"\bsoftware engineering", r"\bdevops\b",
    r"\bcloud computing", r"\bdocker\b", r"\bkubernetes\b", r"\bCI/CD\b",
    r"\bmicroservice", r"\bSQL\b", r"\bNoSQL\b", r"\bdatabase\b",
]

AI_TOPIC_PATTERN = re.compile("|".join(AI_TOPIC_KEYWORDS), re.IGNORECASE)


def is_ai_related(text: str) -> bool:
    """Check if text contains AI/ML/CS keywords."""
    return bool(AI_TOPIC_PATTERN.search(text))


def extract_studychat() -> list[dict]:
    """Extract AI-education content from StudyChat."""
    source = RAW_DIR / "studychat" / "studychat.jsonl"
    if not source.exists():
        print(f"  ! StudyChat raw file not found: {source}")
        return []

    records = []
    with open(source, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    # Each record is a single student-AI interaction (prompt + response)
    items = []
    for r in records:
        prompt = r.get("prompt", "")
        response = r.get("response", "")
        full_text = f"{prompt} {response}"
        topic = r.get("topic", "")
        chat_title = r.get("chat_title", "")

        if not is_ai_related(full_text):
            continue

        # Use chat title as a cleaner title if available
        title = chat_title if chat_title else prompt[:80]

        items.append({
            "id": r["id"],
            "source": "studychat",
            "topic": "AI Tutoring",
            "title": title,
            "content": f"Student: {prompt}\n\nTutor: {response[:1500]}",
            "difficulty": "intermediate",
            "tags": ["ai-tutoring", "student-interaction", "q-and-a", topic],
        })

    return items


def extract_fineweb_edu() -> list[dict]:
    """Extract AI/ML content from FineWeb-Edu."""
    source = RAW_DIR / "fineweb-edu" / "fineweb_edu_sample.jsonl"
    if not source.exists():
        print(f"  ! FineWeb-Edu raw file not found: {source}")
        return []

    items = []
    with open(source, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            text = row.get("text", "")
            if not is_ai_related(text):
                continue

            # Extract a title from first line
            first_line = text.split("\n")[0][:80]
            title = first_line if first_line else "Untitled Educational Content"

            # Determine topic
            topic = "AI/ML"
            for kw in ["python", "javascript", "java", "programming"]:
                if re.search(rf"\b{kw}\b", text, re.IGNORECASE):
                    topic = "Programming"
                    break
            for kw in ["machine learning", "deep learning", "neural network", "llm"]:
                if re.search(rf"\b{kw}\b", text, re.IGNORECASE):
                    topic = "Machine Learning"
                    break

            items.append({
                "id": row["id"],
                "source": "fineweb-edu",
                "topic": topic,
                "title": title,
                "content": text[:2000],
                "difficulty": "intermediate",
                "tags": ["educational", "web-content"],
                "url": row.get("url", ""),
            })

    return items


def extract_qvac_genesis() -> list[dict]:
    """Extract CS/AI content from QVAC Genesis."""
    source = RAW_DIR / "qvac-genesis" / "qvac_genesis_sample.jsonl"
    if not source.exists():
        print(f"  ! QVAC Genesis raw file not found: {source}")
        return []

    items = []
    with open(source, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            question = row.get("question", "")
            solution = row.get("solution", "")
            full_text = f"{question} {solution}"

            if not is_ai_related(full_text):
                continue

            subject = row.get("subject", "CS")
            items.append({
                "id": row["id"],
                "source": "qvac-genesis",
                "topic": subject,
                "title": question[:80],
                "content": f"Question: {question}\n\nSolution: {solution[:1000]}",
                "difficulty": "advanced",
                "tags": [subject, "reasoning", "problem-solving"],
            })

    return items


def generate_questions(knowledge_items: list[dict]) -> list[dict]:
    """Generate assessment questions from knowledge items."""
    questions = []
    for i, item in enumerate(knowledge_items[:200]):
        content = item["content"]
        if len(content) < 100:
            continue

        # Create a simple fill-in-the-blank style question
        sentences = content.split(". ")
        if len(sentences) < 3:
            continue

        # Pick a sentence with a key term
        for s in sentences:
            if re.search(r"\b(is|are|was|were|refers to|means|defined as)\b", s, re.IGNORECASE):
                topic = item["topic"]
                questions.append({
                    "id": f"q-{i}",
                    "question": s[:200],
                    "options": [
                        f"About {topic}",
                        "An unrelated concept",
                        "A programming technique",
                        "A mathematical formula",
                    ],
                    "correct_answer": 0,
                    "explanation": f"This is related to {topic}. {s[:200]}",
                    "topic": topic,
                    "difficulty": item["difficulty"],
                })
                break

    return questions


def run():
    """Run the full preprocessing pipeline.

    Merges real downloaded data (from raw/) with seed data (from seed_data.py)
    so the knowledge base always has rich content even when downloads are partial.
    """
    from backend.data_pipeline.seed_data import KNOWLEDGE_ITEMS, ASSESSMENT_QUESTIONS, COURSES, PROJECTS, LEARNING_PATHS

    print("=" * 60)
    print("Preprocessing: Merging real + seed data into knowledge base")
    print("=" * 60)

    # Step 1: Extract real knowledge items from downloaded raw data
    real_items = []
    real_items.extend(extract_studychat())
    real_items.extend(extract_fineweb_edu())
    real_items.extend(extract_qvac_genesis())
    print(f"\n  Real AI-related items extracted: {len(real_items)}")

    # Step 2: Merge with seed data (deduplicate by id, real data takes priority)
    seed_ids = {item["id"] for item in real_items}
    merged_items = list(real_items)  # real data first
    for item in KNOWLEDGE_ITEMS:
        if item["id"] not in seed_ids:
            merged_items.append(item)
    print(f"  Seed items added: {len(merged_items) - len(real_items)}")
    print(f"  Total knowledge items: {len(merged_items)}")

    # Save knowledge base
    kb_path = PROCESSED_DIR / "knowledge_base.json"
    with open(kb_path, "w", encoding="utf-8") as f:
        json.dump(merged_items, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Knowledge base saved → {kb_path}")

    # Step 2: Use seed assessment questions (high quality, hand-crafted)
    q_path = PROCESSED_DIR / "assessment_questions.json"
    with open(q_path, "w", encoding="utf-8") as f:
        json.dump(ASSESSMENT_QUESTIONS, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Assessment questions: {len(ASSESSMENT_QUESTIONS)} → {q_path}")

    # Step 3: Use seed courses
    courses_path = PROCESSED_DIR / "courses.json"
    with open(courses_path, "w", encoding="utf-8") as f:
        json.dump(COURSES, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Courses: {len(COURSES)} → {courses_path}")

    # Step 4: Use seed projects
    projects_path = PROCESSED_DIR / "projects.json"
    with open(projects_path, "w", encoding="utf-8") as f:
        json.dump(PROJECTS, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Projects: {len(PROJECTS)} → {projects_path}")

    # Step 5: Use seed learning paths
    paths_path = PROCESSED_DIR / "learning_paths.json"
    with open(paths_path, "w", encoding="utf-8") as f:
        json.dump(LEARNING_PATHS, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Learning paths: {len(LEARNING_PATHS)} → {paths_path}")

    print("\n Preprocessing complete! (real + seed data merged)")


if __name__ == "__main__":
    run()