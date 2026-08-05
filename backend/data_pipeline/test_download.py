"""Quick download test - just 50 rows to verify the pipeline works."""
import os
import sys
import time
from pathlib import Path

os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')

from datasets import load_dataset
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import RAW_DIR


def download_fineweb_edu_sample(n=50):
    """Download just 50 rows of FineWeb-Edu to test."""
    print(f"[Test] Downloading {n} rows of FineWeb-Edu...")
    out_dir = RAW_DIR / "fineweb-edu"
    out_dir.mkdir(parents=True, exist_ok=True)

    ds = load_dataset(
        'HuggingFaceFW/fineweb-edu',
        'sample-10BT',
        split='train',
        trust_remote_code=True,
        streaming=True,
    )

    records = []
    for i, row in enumerate(tqdm(ds, total=n, desc="FineWeb-Edu")):
        if i >= n:
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
            f.write(__import__('json').dumps(r, ensure_ascii=False) + "\n")

    size_kb = out_path.stat().st_size / 1024
    print(f"  OK - saved {len(records)} rows ({size_kb:.1f} KB) -> {out_path}")
    return out_path


if __name__ == '__main__':
    start = time.time()
    download_fineweb_edu_sample(50)
    print(f"\nDone in {time.time()-start:.1f}s")
