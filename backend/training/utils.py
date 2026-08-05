"""Common utilities for data preparation and training."""

import json
from pathlib import Path
from typing import Optional

# Project paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BACKEND_DIR / "data" / "raw"
PROCESSED_DIR = BACKEND_DIR / "data" / "processed"
MODELS_DIR = BACKEND_DIR / "models"

# Ensure model directories exist
for d in [MODELS_DIR / "tutor", MODELS_DIR / "assessment", MODELS_DIR / "recommender"]:
    d.mkdir(parents=True, exist_ok=True)


def load_jsonl(filepath: Path) -> list[dict]:
    """Load a JSONL file (one JSON object per line)."""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def save_jsonl(records: list[dict], filepath: Path) -> None:
    """Save records to a JSONL file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_json(filepath: Path) -> list[dict]:
    """Load a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, filepath: Path) -> None:
    """Save data to a JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---- AI topic classification (keyword-based) ----

AI_KEYWORDS = {
    "machine_learning": [
        "machine learning", "ml", "regression", "classification", "clustering",
        "supervised", "unsupervised", "random forest", "decision tree",
        "svm", "knn", "cross validation", "overfitting", "underfitting",
        "bias", "variance", "feature engineering", "scikit-learn", "sklearn",
        "梯度下降", "机器学习", "回归", "分类", "聚类", "过拟合",
    ],
    "deep_learning": [
        "deep learning", "neural network", "cnn", "rnn", "lstm", "transformer",
        "attention", "bert", "gpt", "embedding", "backpropagation",
        "convolutional", "recurrent", "gradient", "epoch", "batch normalization",
        "pytorch", "tensorflow", "keras", "深度学习", "神经网络",
        "卷积", "循环", "注意力", "反向传播",
    ],
    "data_science": [
        "data science", "pandas", "numpy", "matplotlib", "visualization",
        "data analysis", "data cleaning", "eda", "statistics",
        "r-squared", "mse", "correlation", "distribution", "outlier",
        "数据科学", "数据分析", "数据可视化", "统计",
    ],
    "programming": [
        "python", "java", "javascript", "c++", "function", "class",
        "object", "array", "dictionary", "list", "loop", "condition",
        "error", "exception", "debug", "api", "json", "sql",
        "编程", "代码", "函数", "变量", "循环",
    ],
    "math_stats": [
        "probability", "statistics", "linear algebra", "calculus",
        "derivative", "integral", "matrix", "vector", "eigenvalue",
        "normal distribution", "bayes", "hypothesis testing", "p-value",
        "概率", "统计", "线性代数", "微积分", "矩阵",
    ],
}

TOPIC_LABELS = {
    "machine_learning": "机器学习",
    "deep_learning": "深度学习",
    "data_science": "数据科学",
    "programming": "编程基础",
    "math_stats": "数学统计",
}


def classify_topic(text: str) -> str:
    """Classify text into an AI topic based on keyword matching.

    Returns one of: machine_learning, deep_learning, data_science, programming, math_stats, other
    """
    text_lower = text.lower()
    scores = {}
    for topic, keywords in AI_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[topic] = score

    if not scores:
        return "other"

    return max(scores, key=scores.get)


def classify_difficulty(interaction_count: int) -> str:
    """Classify difficulty based on interaction count.

    - < 5 interactions: beginner (simple questions)
    - 5-10 interactions: intermediate
    - > 10 interactions: advanced (complex multi-step problems)
    """
    if interaction_count < 5:
        return "beginner"
    elif interaction_count <= 10:
        return "intermediate"
    else:
        return "advanced"
