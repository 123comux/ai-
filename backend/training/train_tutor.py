"""Fine-tune Qwen2.5-1.5B-Instruct with LoRA for AI tutor."""

import os
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set proxy for downloading model
os.environ.setdefault("HTTPS_PROXY", "socks5://127.0.0.1:17890")
os.environ.setdefault("HTTP_PROXY", "socks5://127.0.0.1:17890")
os.environ.setdefault("ALL_PROXY", "socks5://127.0.0.1:17890")

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import (
    LoraConfig,
    get_peft_model,
    TaskType,
    prepare_model_for_kbit_training,
)
from torch.utils.data import Dataset

from training.utils import PROCESSED_DIR, MODELS_DIR

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
MAX_SEQ_LENGTH = 1024


class TutorDataset(Dataset):
    """Dataset for causal LM fine-tuning with ChatML format."""

    def __init__(self, records: list[dict], tokenizer, max_length: int = MAX_SEQ_LENGTH):
        self.records = records
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        r = self.records[idx]
        messages = r["messages"]

        # Use apply_chat_template to format as ChatML
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )

        # Tokenize without padding (dynamic padding handled by data collator)
        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding=False,
        )

        # Return as lists (not tensors) for the data collator to handle
        return {
            "input_ids": encoding["input_ids"],
            "attention_mask": encoding["attention_mask"],
        }


def load_tutor_data(sample_limit: int = None):
    """Load tutor training data."""
    data_path = PROCESSED_DIR / "tutor_train.jsonl"
    records = []
    with open(data_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    if sample_limit:
        records = records[:sample_limit]

    return records


def train_tutor(
    epochs: int = 3,
    batch_size: int = 2,
    gradient_accumulation: int = 4,
    learning_rate: float = 2e-4,
    lora_rank: int = 8,
    lora_alpha: int = 16,
    sample_limit: int = None,
    max_seq_length: int = MAX_SEQ_LENGTH,
):
    """Fine-tune Qwen2.5-1.5B-Instruct with QLoRA.

    Args:
        epochs: Number of training epochs
        batch_size: Per-device batch size
        gradient_accumulation: Gradient accumulation steps
        learning_rate: Learning rate
        lora_rank: LoRA rank
        lora_alpha: LoRA alpha
        sample_limit: If set, only use this many samples
        max_seq_length: Maximum sequence length
    """
    print(f"[Tutor] Loading training data...")
    records = load_tutor_data(sample_limit)
    print(f"[Tutor] {len(records)} training samples")

    # Split 90/10 for train/eval
    split_idx = int(len(records) * 0.9)
    train_records = records[:split_idx]
    eval_records = records[split_idx:]
    print(f"[Tutor] Train: {len(train_records)}, Eval: {len(eval_records)}")

    print(f"\n[Tutor] Loading tokenizer: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"[Tutor] Loading model with 4bit quantization...")
    from transformers import BitsAndBytesConfig

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        trust_remote_code=True,
        device_map="auto",
    )

    # Prepare model for kbit training
    model = prepare_model_for_kbit_training(model)

    # LoRA configuration
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=lora_rank,
        lora_alpha=lora_alpha,
        lora_dropout=0.05,
        bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Create datasets
    train_dataset = TutorDataset(train_records, tokenizer, max_seq_length)
    eval_dataset = TutorDataset(eval_records, tokenizer, max_seq_length)

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    # Training arguments
    output_dir = MODELS_DIR / "tutor"
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation,
        learning_rate=learning_rate,
        weight_decay=0.01,
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_steps=20,
        save_total_limit=2,
        report_to="none",
        dataloader_num_workers=0,
        fp16=True,
        gradient_checkpointing=True,
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
    )

    # Train
    print(f"\n[Tutor] Starting LoRA fine-tuning...")
    print(f"[Tutor] Effective batch size: {batch_size * gradient_accumulation}")
    print(f"[Tutor] Steps per epoch: {len(train_records) // (batch_size * gradient_accumulation)}")
    trainer.train()

    # Evaluate
    print(f"\n[Tutor] Final evaluation:")
    results = trainer.evaluate()
    print(f"  Results: {results}")

    # Save LoRA adapter
    print(f"\n[Tutor] Saving LoRA adapter to {output_dir}")
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    # Test generation
    print(f"\n[Tutor] Testing generation...")
    test_questions = [
        "What is gradient descent?",
        "How does cross validation work?",
        "Explain neural networks simply.",
    ]

    model.eval()
    for q in test_questions:
        messages = [
            {"role": "system", "content": "You are a helpful AI tutor specialized in machine learning, deep learning, and data science."},
            {"role": "user", "content": q},
        ]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
            )

        response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        print(f"\n  Q: {q}")
        print(f"  A: {response[:200]}")

    print(f"\n[Tutor] ✅ Training complete!")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune Qwen2.5-1.5B for AI tutoring")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--lora-rank", type=int, default=8)
    parser.add_argument("--sample-limit", type=int, default=None, help="Limit samples for quick test")
    parser.add_argument("--max-seq-length", type=int, default=1024)
    args = parser.parse_args()

    train_tutor(
        epochs=args.epochs,
        batch_size=args.batch_size,
        gradient_accumulation=args.grad_accum,
        learning_rate=args.lr,
        lora_rank=args.lora_rank,
        sample_limit=args.sample_limit,
        max_seq_length=args.max_seq_length,
    )
