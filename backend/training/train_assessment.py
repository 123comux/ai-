"""Train BERT classifier for ability assessment (topic classification)."""

import os
import sys
import json
import random
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set proxy for downloading model
os.environ.setdefault("HTTPS_PROXY", "socks5://127.0.0.1:17890")
os.environ.setdefault("HTTP_PROXY", "socks5://127.0.0.1:17890")
os.environ.setdefault("ALL_PROXY", "socks5://127.0.0.1:17890")
os.environ.setdefault("HF_TOKEN", os.getenv("HF_TOKEN", ""))

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from torch.utils.data import Dataset

from training.utils import PROCESSED_DIR, MODELS_DIR, TOPIC_LABELS

# Topic labels (6 classes including "other")
TOPIC_LIST = ["machine_learning", "deep_learning", "data_science", "programming", "math_stats", "other"]
TOPIC_TO_ID = {t: i for i, t in enumerate(TOPIC_LIST)}

MODEL_NAME = "bert-base-chinese"
MAX_LENGTH = 256


class AssessmentDataset(Dataset):
    """Dataset for topic classification."""

    def __init__(self, records: list[dict], tokenizer):
        self.records = records
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        r = self.records[idx]
        text = r["text"]
        label = TOPIC_TO_ID.get(r["topic_label"], TOPIC_TO_ID["other"])

        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH,
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels": torch.tensor(label, dtype=torch.long),
        }


def load_train_val_data():
    """Load training and validation data."""
    train_path = PROCESSED_DIR / "assessment_train.jsonl"
    val_path = PROCESSED_DIR / "assessment_val.jsonl"

    train_records = []
    with open(train_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                train_records.append(json.loads(line))

    val_records = []
    with open(val_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                val_records.append(json.loads(line))

    return train_records, val_records


def compute_accuracy(eval_pred):
    """Compute accuracy metric."""
    predictions, labels = eval_pred
    preds = np.argmax(predictions, axis=-1)
    acc = (preds == labels).mean()
    return {"accuracy": acc}


def train_assessment(
    epochs: int = 5,
    batch_size: int = 16,
    learning_rate: float = 2e-5,
    sample_limit: int = None,
):
    """Train BERT classifier for topic classification.

    Args:
        epochs: Number of training epochs
        batch_size: Training batch size
        learning_rate: Learning rate
        sample_limit: If set, only use this many samples (for quick testing)
    """
    print(f"[Assessment] Loading data...")
    train_records, val_records = load_train_val_data()

    if sample_limit:
        train_records = train_records[:sample_limit]
        val_records = val_records[:sample_limit // 5]
        print(f"[Assessment] Using limited samples: {len(train_records)} train, {len(val_records)} val")

    print(f"[Assessment] Train: {len(train_records)}, Val: {len(val_records)}")

    # Print label distribution
    from collections import Counter
    train_dist = Counter(r["topic_label"] for r in train_records)
    print(f"[Assessment] Train label distribution: {dict(train_dist)}")

    print(f"[Assessment] Loading tokenizer and model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(TOPIC_LIST),
        id2label={i: t for t, i in TOPIC_TO_ID.items()},
        label2id=TOPIC_TO_ID,
    )

    # Move to GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    print(f"[Assessment] Using device: {device}")

    # Create datasets
    train_dataset = AssessmentDataset(train_records, tokenizer)
    val_dataset = AssessmentDataset(val_records, tokenizer)

    # Training arguments
    output_dir = MODELS_DIR / "assessment"
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        greater_is_better=True,
        logging_steps=50,
        save_total_limit=2,
        report_to="none",
        dataloader_num_workers=0,
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_accuracy,
    )

    # Train
    print(f"\n[Assessment] Starting training...")
    trainer.train()

    # Evaluate
    print(f"\n[Assessment] Final evaluation:")
    results = trainer.evaluate()
    print(f"  Results: {results}")

    # Save model
    print(f"\n[Assessment] Saving model to {output_dir}")
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    # Save label mapping
    label_map = {
        "topic_to_id": TOPIC_TO_ID,
        "id_to_topic": {i: t for t, i in TOPIC_TO_ID.items()},
        "topic_labels_cn": TOPIC_LABELS,
    }
    with open(output_dir / "label_map.json", "w", encoding="utf-8") as f:
        json.dump(label_map, f, ensure_ascii=False, indent=2)

    print(f"\n[Assessment] ✅ Training complete! Accuracy: {results.get('eval_accuracy', 0):.4f}")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--sample-limit", type=int, default=None, help="Limit samples for quick test")
    args = parser.parse_args()

    train_assessment(
        epochs=args.epochs,
        batch_size=args.batch_size,
        sample_limit=args.sample_limit,
    )
