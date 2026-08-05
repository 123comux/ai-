"""AI-powered assessment service using BERT classifier."""

import json
from pathlib import Path
from typing import Optional

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from config import PROCESSED_DIR

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# Lazy-loaded model
_model_cache = None


def _load_model():
    """Load BERT assessment model (cached)."""
    global _model_cache
    if _model_cache is not None:
        return _model_cache

    model_dir = MODELS_DIR / "assessment"
    if not model_dir.exists():
        raise FileNotFoundError(f"Assessment model not found: {model_dir}. Run training first.")

    # Load label mapping
    with open(model_dir / "label_map.json", "r", encoding="utf-8") as f:
        label_map = json.load(f)

    tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
    model = AutoModelForSequenceClassification.from_pretrained(str(model_dir))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()

    _model_cache = {
        "tokenizer": tokenizer,
        "model": model,
        "device": device,
        "label_map": label_map,
    }
    return _model_cache


def analyze_content(text: str) -> dict:
    """Analyze student's question/content to determine knowledge domain.

    Args:
        text: Student's question or content text

    Returns:
        Analysis result with predicted topic, confidence, and recommendations
    """
    cache = _load_model()
    tokenizer = cache["tokenizer"]
    model = cache["model"]
    device = cache["device"]
    label_map = cache["label_map"]

    # Tokenize
    encoding = tokenizer(
        text,
        truncation=True,
        padding="max_length",
        max_length=256,
        return_tensors="pt",
    ).to(device)

    # Predict
    with torch.no_grad():
        outputs = model(**encoding)
        probs = torch.softmax(outputs.logits, dim=-1)
        pred_id = probs.argmax(dim=-1).item()
        confidence = probs[0][pred_id].item()

    # Map to label
    id_to_topic = label_map["id_to_topic"]
    topic_labels_cn = label_map["topic_labels_cn"]

    topic_key = id_to_topic.get(str(pred_id), "other")
    topic_cn = topic_labels_cn.get(topic_key, "其他")

    # Get all probabilities
    all_probs = {}
    for idx, prob in enumerate(probs[0]):
        t_key = id_to_topic.get(str(idx), "other")
        t_cn = topic_labels_cn.get(t_key, "其他")
        all_probs[t_cn] = round(prob.item(), 4)

    # Sort by probability
    sorted_probs = dict(sorted(all_probs.items(), key=lambda x: x[1], reverse=True))

    return {
        "text": text[:200],
        "predicted_topic": topic_cn,
        "topic_key": topic_key,
        "confidence": round(confidence, 4),
        "all_topics": sorted_probs,
        "recommendation": _get_recommendation(topic_key, confidence),
    }


def _get_recommendation(topic_key: str, confidence: float) -> str:
    """Get learning recommendation based on predicted topic."""
    recommendations = {
        "machine_learning": "建议学习机器学习基础课程，包括监督学习、无监督学习和模型评估",
        "deep_learning": "建议学习深度学习课程，重点掌握神经网络、CNN和Transformer",
        "data_science": "建议学习数据科学课程，包括数据分析和可视化",
        "programming": "建议加强编程基础，学习Python和数据结构",
        "math_stats": "建议补充数学基础，学习概率论和线性代数",
        "other": "建议先进行AI基础入门，了解机器学习的基本概念",
    }
    return recommendations.get(topic_key, "建议从AI基础课程开始学习")


def get_model_info() -> dict:
    """Get assessment model info."""
    cache = _load_model()
    return {
        "model_type": "BERT Classifier (bert-base-chinese)",
        "num_labels": len(cache["label_map"]["topic_to_id"]),
        "device": str(cache["device"]),
        "labels": cache["label_map"]["topic_labels_cn"],
    }
