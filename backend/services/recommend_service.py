"""Course recommendation service using TF-IDF model."""

import json
import joblib
from pathlib import Path
from typing import Optional

from sklearn.metrics.pairwise import cosine_similarity

from config import PROCESSED_DIR

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# Lazy-loaded model
_model_cache = None


def _load_model():
    """Load TF-IDF model (cached)."""
    global _model_cache
    if _model_cache is not None:
        return _model_cache

    model_path = MODELS_DIR / "recommender" / "tfidf_model.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Recommender model not found: {model_path}. Run training first.")

    _model_cache = joblib.load(model_path)
    return _model_cache


def recommend_courses(
    interest: str,
    limit: int = 10,
    topic: Optional[str] = None,
) -> list[dict]:
    """Recommend courses based on user interest.

    Args:
        interest: User's interest text (e.g., "deep learning neural network")
        limit: Max number of recommendations
        topic: Optional topic filter

    Returns:
        List of recommended items with similarity scores
    """
    model = _load_model()
    vectorizer = model["vectorizer"]
    tfidf_matrix = model["tfidf_matrix"]
    metadata = model["metadata"]

    # Vectorize the query
    query_vec = vectorizer.transform([interest])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

    # Sort by score
    ranked_indices = scores.argsort()[::-1]

    results = []
    for idx in ranked_indices:
        if scores[idx] <= 0:
            continue

        meta = metadata[idx]
        if topic and meta.get("topic", "").lower() != topic.lower():
            continue

        results.append({
            "id": meta["id"],
            "title": meta["title"],
            "topic": meta["topic"],
            "source": meta["source"],
            "difficulty": meta["difficulty"],
            "score": float(scores[idx]),
        })

        if len(results) >= limit:
            break

    return results


def get_model_info() -> dict:
    """Get recommender model info."""
    model = _load_model()
    return {
        "total_items": len(model["metadata"]),
        "matrix_shape": list(model["tfidf_matrix"].shape),
        "model_type": "TF-IDF + Cosine Similarity",
    }
