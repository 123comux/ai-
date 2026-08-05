"""Prepare StudyChat data for assessment model training (classification)."""

import sys
import random
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from training.utils import (
    load_jsonl, save_jsonl, RAW_DIR, PROCESSED_DIR,
    classify_topic, classify_difficulty, TOPIC_LABELS,
)


def prepare_assessment_data(
    source_path: Path = None,
    output_path: Path = None,
    train_ratio: float = 0.8,
) -> dict:
    """Convert StudyChat data into labeled classification dataset.

    Each record gets:
    - text: the student's prompt
    - topic_label: AI knowledge domain (5 categories + other)
    - difficulty_label: beginner / intermediate / advanced

    Returns:
        Dict with stats about the prepared data
    """
    if source_path is None:
        source_path = RAW_DIR / "studychat" / "studychat.jsonl"
    if output_path is None:
        output_path = PROCESSED_DIR / "assessment_train.jsonl"

    print(f"[Assessment Data] Loading from {source_path}")
    records = load_jsonl(source_path)
    print(f"[Assessment Data] Loaded {len(records)} raw records")

    # Label each record
    labeled = []
    for r in records:
        prompt = r.get("prompt", "").strip()
        if len(prompt) < 10:
            continue

        topic = classify_topic(prompt)
        difficulty = classify_difficulty(r.get("interaction_count", 0))

        labeled.append({
            "id": r.get("id", ""),
            "text": prompt,
            "topic_label": topic,
            "topic_label_cn": TOPIC_LABELS.get(topic, "其他"),
            "difficulty_label": difficulty,
            "interaction_count": r.get("interaction_count", 0),
        })

    print(f"[Assessment Data] {len(labeled)} labeled records")

    # Print distribution
    topic_dist = Counter(r["topic_label"] for r in labeled)
    diff_dist = Counter(r["difficulty_label"] for r in labeled)

    print(f"\n[Assessment Data] Topic distribution:")
    for t, c in topic_dist.most_common():
        print(f"  {t}: {c} ({TOPIC_LABELS.get(t, '其他')})")

    print(f"\n[Assessment Data] Difficulty distribution:")
    for d, c in diff_dist.most_common():
        print(f"  {d}: {c}")

    # Split into train/val
    random.seed(42)
    random.shuffle(labeled)
    split_idx = int(len(labeled) * train_ratio)
    train_set = labeled[:split_idx]
    val_set = labeled[split_idx:]

    print(f"\n[Assessment Data] Train: {len(train_set)}, Val: {len(val_set)}")

    # Save
    save_jsonl(train_set, PROCESSED_DIR / "assessment_train.jsonl")
    save_jsonl(val_set, PROCESSED_DIR / "assessment_val.jsonl")

    print(f"[Assessment Data] Saved to {PROCESSED_DIR}")

    return {
        "total": len(labeled),
        "train": len(train_set),
        "val": len(val_set),
        "topic_dist": dict(topic_dist),
        "difficulty_dist": dict(diff_dist),
    }


if __name__ == "__main__":
    stats = prepare_assessment_data()
    print(f"\n✓ Done! {stats['train']} train + {stats['val']} val samples prepared.")
