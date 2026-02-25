"""
Embedding-based novelty scoring.

Detects semantic repetition by comparing new artifacts against history
using vector embeddings and cosine similarity.
"""
import json
import logging
import os
from pathlib import Path
from typing import Optional
import numpy as np

from config import BASE_DIR, OPENAI_API_KEY, OPENAI_BASE_URL

logger = logging.getLogger(__name__)

# Embedding model (small, fast, cheap)
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = 1536  # text-embedding-3-small default

# Cache file for embeddings
EMBEDDINGS_CACHE_FILE = BASE_DIR / "memory" / "embeddings_cache.json"

# Thresholds
SIMILARITY_THRESHOLD = 0.85  # Above this = too similar (repetition)
NOVELTY_REJECTION_THRESHOLD = 0.15  # Below this novelty score = reject


class EmbeddingCache:
    """Cache for embeddings to avoid redundant API calls."""

    def __init__(self, cache_file: Path = EMBEDDINGS_CACHE_FILE):
        self.cache_file = cache_file
        self.cache: dict[str, list[float]] = {}
        self._load()

    def _load(self):
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    self.cache = json.load(f)
                logger.debug(f"Loaded {len(self.cache)} cached embeddings")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load embedding cache: {e}")
                self.cache = {}

    def _save(self):
        """Save cache to disk."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)

    def get(self, text: str) -> Optional[list[float]]:
        """Get cached embedding for text."""
        # Use hash of text as key (text itself might be too long)
        key = str(hash(text))
        return self.cache.get(key)

    def set(self, text: str, embedding: list[float]):
        """Cache embedding for text."""
        key = str(hash(text))
        self.cache[key] = embedding
        self._save()

    def clear(self):
        """Clear the cache."""
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()


# Global cache instance
_cache = None


def get_cache() -> EmbeddingCache:
    """Get or create the global embedding cache."""
    global _cache
    if _cache is None:
        _cache = EmbeddingCache()
    return _cache


def get_embedding(text: str, use_cache: bool = True) -> list[float]:
    """
    Get embedding vector for text.

    Args:
        text: Text to embed
        use_cache: Whether to use cached embeddings

    Returns:
        Embedding vector as list of floats
    """
    if not text or not text.strip():
        # Return zero vector for empty text
        return [0.0] * EMBEDDING_DIMENSIONS

    cache = get_cache()

    # Check cache
    if use_cache:
        cached = cache.get(text)
        if cached is not None:
            return cached

    # Call API
    from openai import OpenAI

    if not OPENAI_API_KEY:
        logger.warning("No API key for embeddings, returning zero vector")
        return [0.0] * EMBEDDING_DIMENSIONS

    try:
        client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
        )
        embedding = response.data[0].embedding

        # Cache result
        if use_cache:
            cache.set(text, embedding)

        return embedding

    except Exception as e:
        logger.error(f"Failed to get embedding: {e}")
        return [0.0] * EMBEDDING_DIMENSIONS


def get_embeddings_batch(texts: list[str], use_cache: bool = True) -> list[list[float]]:
    """
    Get embeddings for multiple texts efficiently.

    Args:
        texts: List of texts to embed
        use_cache: Whether to use cached embeddings

    Returns:
        List of embedding vectors
    """
    if not texts:
        return []

    cache = get_cache()
    results = [None] * len(texts)
    texts_to_fetch = []
    indices_to_fetch = []

    # Check cache for each text
    for i, text in enumerate(texts):
        if not text or not text.strip():
            results[i] = [0.0] * EMBEDDING_DIMENSIONS
        elif use_cache:
            cached = cache.get(text)
            if cached is not None:
                results[i] = cached
            else:
                texts_to_fetch.append(text)
                indices_to_fetch.append(i)
        else:
            texts_to_fetch.append(text)
            indices_to_fetch.append(i)

    # Fetch missing embeddings in batch
    if texts_to_fetch:
        from openai import OpenAI

        if not OPENAI_API_KEY:
            logger.warning("No API key for embeddings")
            for i in indices_to_fetch:
                results[i] = [0.0] * EMBEDDING_DIMENSIONS
        else:
            try:
                client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
                response = client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=texts_to_fetch,
                )

                for j, emb_data in enumerate(response.data):
                    idx = indices_to_fetch[j]
                    embedding = emb_data.embedding
                    results[idx] = embedding

                    if use_cache:
                        cache.set(texts_to_fetch[j], embedding)

            except Exception as e:
                logger.error(f"Failed to get batch embeddings: {e}")
                for i in indices_to_fetch:
                    if results[i] is None:
                        results[i] = [0.0] * EMBEDDING_DIMENSIONS

    return results


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Returns:
        Similarity score between -1 and 1 (1 = identical)
    """
    a_arr = np.array(a)
    b_arr = np.array(b)

    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a_arr, b_arr) / (norm_a * norm_b))


def compute_novelty_score(
    text: str,
    history_embeddings: list[list[float]],
    text_embedding: Optional[list[float]] = None
) -> float:
    """
    Compute novelty score for text against history.

    Args:
        text: New text to evaluate
        history_embeddings: List of embeddings for historical texts
        text_embedding: Pre-computed embedding for text (optional)

    Returns:
        Novelty score between 0 and 1 (1 = completely novel, 0 = exact repeat)
    """
    if not history_embeddings:
        return 1.0  # First item is always novel

    if text_embedding is None:
        text_embedding = get_embedding(text)

    # Find maximum similarity to any historical item
    max_similarity = 0.0
    for hist_emb in history_embeddings:
        sim = cosine_similarity(text_embedding, hist_emb)
        max_similarity = max(max_similarity, sim)

    # Novelty = 1 - max_similarity
    novelty = 1.0 - max_similarity
    return max(0.0, min(1.0, novelty))


def compute_novelty_scores_batch(
    texts: list[str],
    history_embeddings: list[list[float]]
) -> list[float]:
    """
    Compute novelty scores for multiple texts efficiently.

    Args:
        texts: List of new texts to evaluate
        history_embeddings: List of embeddings for historical texts

    Returns:
        List of novelty scores
    """
    if not texts:
        return []

    if not history_embeddings:
        return [1.0] * len(texts)

    # Get embeddings for all texts
    text_embeddings = get_embeddings_batch(texts)

    # Compute novelty for each
    scores = []
    for text_emb in text_embeddings:
        max_sim = max(cosine_similarity(text_emb, h) for h in history_embeddings)
        novelty = 1.0 - max_sim
        scores.append(max(0.0, min(1.0, novelty)))

    return scores


def is_novel(text: str, history_embeddings: list[list[float]], threshold: float = NOVELTY_REJECTION_THRESHOLD) -> bool:
    """
    Check if text is sufficiently novel compared to history.

    Args:
        text: Text to check
        history_embeddings: Historical embeddings
        threshold: Minimum novelty score to be considered novel

    Returns:
        True if novel enough, False if too similar to existing content
    """
    score = compute_novelty_score(text, history_embeddings)
    return score >= threshold
