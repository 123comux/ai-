"""
Dataset download module.

Downloads three datasets relevant to AI talent training:
1. FineWeb-Edu - Educational web content (HuggingFace)
2. QVAC Genesis - Educational synthetic pre-training data (HuggingFace)
3. StudyChat - Student-LLM tutoring interactions (HuggingFace)

Usage:
    python -m backend.data_pipeline.download
    python -m backend.data_pipeline.download --datasets studychat  # specific only
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Use Clash SOCKS5 proxy for HuggingFace access (set before importing datasets)
# If VPN is not running, fallback to hf-mirror.com
os.environ.setdefault('HTTPS_PROXY', 'socks5://127.0.0.1:17890')
os.environ.setdefault('HTTP_PROXY', 'socks5://127.0.0.1:17890')
os.environ.setdefault('ALL_PROXY', 'socks5://127.0.0.1:17890')

from tqdm import tqdm

# Add parent dir to path for config import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DIR, FIREWEB_EDU_MAX_ROWS, QVAC_GENESIS_MAX_ROWS, STUDYCHAT_MAX_ROWS


def download_studychat(max_rows: int = STUDYCHAT_MAX_ROWS) -> Path:
    """Download StudyChat - student-LLM tutoring interactions. (~16K rows, ~few MB)"""
    print("[Download] StudyChat: student-LLM tutoring interactions...")
    try:
        from datasets import load_dataset
    except ImportError:
        raise ImportError("Run: pip install datasets")

    out_dir = RAW_DIR / "studychat"
    out_dir.mkdir(parents=True, exist_ok=True)

    dataset = load_dataset("wmcnicho/StudyChat", split="train", trust_remote_code=True)
    total = min(len(dataset), max_rows)

    records = []
    for i in tqdm(range(total), desc="StudyChat"):
        row = dataset[i]
        records.append({
            "id": f"studychat-{i}",
            "prompt": str(row.get("prompt", "")),
            "response": str(row.get("response", "")),
            "topic": str(row.get("topic", "")),
            "chat_title": str(row.get("chatTitle", "")),
            "chat_id": str(row.get("chatId", "")),
            "timestamp": str(row.get("timestamp", "")),
            "semester": str(row.get("semester", "")),
            "interaction_count": int(row.get("interactionCount", 0)),
        })

    out_path = out_dir / "studychat.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"  ✓ Saved {len(records)} records → {out_path}")
    return out_path


def download_fineweb_edu(max_rows: int = FIREWEB_EDU_MAX_ROWS) -> Path:
    """Download FineWeb-Edu sample-10BT (subset)."""
    print("[Download] FineWeb-Edu: educational web content (sample-10BT, first 5000 rows)...")
    try:
        from datasets import load_dataset
    except ImportError:
        raise ImportError("Run: pip install datasets")

    out_dir = RAW_DIR / "fineweb-edu"
    out_dir.mkdir(parents=True, exist_ok=True)

    dataset = load_dataset(
        "HuggingFaceFW/fineweb-edu",
        "sample-10BT",
        split="train",
        trust_remote_code=True,
        streaming=True,
    )

    records = []
    for i, row in tqdm(enumerate(dataset), desc="FineWeb-Edu", total=max_rows):
        if i >= max_rows:
            break
        records.append({
            "id": f"fineweb-edu-{i}",
            "text": str(row.get("text", "")),
            "url": str(row.get("url", "")),
            "score": float(row.get("score", 0)),
            "language": str(row.get("language", "")),
        })

    out_path = out_dir / "fineweb_edu_sample.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"  ✓ Saved {len(records)} records → {out_path}")
    return out_path


def download_qvac_genesis(max_rows: int = QVAC_GENESIS_MAX_ROWS) -> Path:
    """Download QVAC Genesis I (sample)."""
    print("[Download] QVAC Genesis I: educational synthetic data (sample)...")
    try:
        from datasets import load_dataset
    except ImportError:
        raise ImportError("Run: pip install datasets")

    out_dir = RAW_DIR / "qvac-genesis"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Try loading Genesis I
    try:
        dataset = load_dataset(
            "qvac/Genesis-I",
            split="train",
            trust_remote_code=True,
            streaming=True,
        )
    except Exception:
        print("  ! QVAC Genesis-I not found on HF, trying Genesis-II...")
        dataset = load_dataset(
            "qvac/Genesis-II",
            split="train",
            trust_remote_code=True,
            streaming=True,
        )

    records = []
    for i, row in tqdm(enumerate(dataset), desc="QVAC Genesis", total=max_rows):
        if i >= max_rows:
            break
        records.append({
            "id": f"qvac-genesis-{i}",
            "subject": str(row.get("subject", "")),
            "question": str(row.get("question", "")),
            "solution": str(row.get("solution", "")),
            "reasoning": str(row.get("reasoning", "")),
        })

    out_path = out_dir / "qvac_genesis_sample.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"  ✓ Saved {len(records)} records → {out_path}")
    return out_path


def download_all():
    start = time.time()
    print("=" * 60)
    print("Starting dataset download for AI Talent Training Pipeline")
    print("=" * 60)

    download_studychat()
    download_fineweb_edu()
    download_qvac_genesis()

    elapsed = time.time() - start
    print(f"\n All downloads completed in {elapsed:.1f}s")
    print(f"  Raw data saved to: {RAW_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", nargs="+", choices=["studychat", "fineweb-edu", "qvac-genesis", "all"], default=["all"])
    args = parser.parse_args()

    if "all" in args.datasets:
        download_all()
    else:
        if "studychat" in args.datasets:
            download_studychat()
        if "fineweb-edu" in args.datasets:
            download_fineweb_edu()
        if "qvac-genesis" in args.datasets:
            download_qvac_genesis()