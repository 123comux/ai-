"""Build TF-IDF course recommender model."""

import sys
import json
import joblib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from training.utils import PROCESSED_DIR, MODELS_DIR
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_recommender(
    knowledge_path: Path = None,
    output_path: Path = None,
) -> dict:
    """Build a TF-IDF based content recommender.

    Creates a TF-IDF matrix from all knowledge base entries,
    allowing similarity-based search for course recommendations.

    Returns:
        Stats about the built model
    """
    if knowledge_path is None:
        knowledge_path = PROCESSED_DIR / "knowledge_base.json"
    if output_path is None:
        output_path = MODELS_DIR / "recommender" / "tfidf_model.joblib"

    print(f"[Recommender] Loading knowledge base from {knowledge_path}")
    with open(knowledge_path, "r", encoding="utf-8") as f:
        knowledge = json.load(f)
    print(f"[Recommender] Loaded {len(knowledge)} knowledge items")

    # Prepare documents (title + content for each item)
    documents = []
    metadata = []
    for item in knowledge:
        title = item.get("title", "")
        content = item.get("content", "")
        topic = item.get("topic", "")
        doc = f"{title} {topic} {content[:500]}"
        documents.append(doc)
        metadata.append({
            "id": item.get("id", ""),
            "title": title,
            "topic": topic,
            "source": item.get("source", ""),
            "difficulty": item.get("difficulty", ""),
        })

    # Build TF-IDF vectorizer
    print(f"[Recommender] Building TF-IDF matrix...")
    vectorizer = TfidfVectorizer(
        max_features=10000,
        stop_words="english",
        ngram_range=(1, 2),
        max_df=0.9,
        min_df=2,
    )
    tfidf_matrix = vectorizer.fit_transform(documents)
    print(f"[Recommender] Matrix shape: {tfidf_matrix.shape}")

    # Save model
    model_data = {
        "vectorizer": vectorizer,
        "tfidf_matrix": tfidf_matrix,
        "metadata": metadata,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_data, output_path)
    print(f"[Recommender] Saved to {output_path}")

    # Test: search for "machine learning"
    query_vec = vectorizer.transform(["machine learning neural network"])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = scores.argsort()[-5:][::-1]

    print(f"\n[Recommender] Test search 'machine learning neural network':")
    for idx in top_indices:
        print(f"  score={scores[idx]:.3f} | {metadata[idx]['title'][:60]}")

    return {
        "total_items": len(knowledge),
        "matrix_shape": tfidf_matrix.shape,
        "model_path": str(output_path),
    }


if __name__ == "__main__":
    stats = build_recommender()
    print(f"\n✓ Recommender built! {stats['total_items']} items, matrix {stats['matrix_shape']}")
