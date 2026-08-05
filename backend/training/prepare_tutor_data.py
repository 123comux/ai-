"""Prepare StudyChat data for AI tutor fine-tuning (ChatML format)."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from training.utils import load_jsonl, save_jsonl, RAW_DIR, PROCESSED_DIR


def prepare_tutor_data(
    source_path: Path = None,
    output_path: Path = None,
    min_prompt_len: int = 10,
    max_prompt_len: int = 2000,
    max_response_len: int = 2000,
) -> int:
    """Convert StudyChat prompt-response pairs into ChatML training format.

    Args:
        source_path: Path to studychat.jsonl
        output_path: Path to output tutor_train.jsonl
        min_prompt_len: Minimum prompt length (chars) to keep
        max_prompt_len: Maximum prompt length (chars) to keep
        max_response_len: Maximum response length (chars) to keep

    Returns:
        Number of training samples written
    """
    if source_path is None:
        source_path = RAW_DIR / "studychat" / "studychat.jsonl"
    if output_path is None:
        output_path = PROCESSED_DIR / "tutor_train.jsonl"

    print(f"[Tutor Data] Loading from {source_path}")
    records = load_jsonl(source_path)
    print(f"[Tutor Data] Loaded {len(records)} raw records")

    # Filter and convert
    train_data = []
    skipped = 0

    for r in records:
        prompt = r.get("prompt", "").strip()
        response = r.get("response", "").strip()

        # Filter out too short or too long
        if len(prompt) < min_prompt_len or len(prompt) > max_prompt_len:
            skipped += 1
            continue
        if len(response) < 20 or len(response) > max_response_len:
            skipped += 1
            continue

        # Convert to ChatML format (Qwen2.5 format)
        messages = [
            {"role": "system", "content": "You are a helpful AI tutor specialized in machine learning, deep learning, and data science. Answer questions clearly and concisely."},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response},
        ]

        train_data.append({
            "id": r.get("id", ""),
            "messages": messages,
        })

    print(f"[Tutor Data] Filtered out {skipped} records (too short/long)")
    print(f"[Tutor Data] Writing {len(train_data)} training samples to {output_path}")

    save_jsonl(train_data, output_path)

    # Print sample
    if train_data:
        sample = train_data[0]
        print(f"\n[Tutor Data] Sample (first record):")
        for msg in sample["messages"]:
            print(f"  [{msg['role']}] {msg['content'][:100]}...")

    return len(train_data)


if __name__ == "__main__":
    count = prepare_tutor_data()
    print(f"\n✓ Done! {count} training samples prepared.")
