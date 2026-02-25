"""Tests for embeddings module."""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock


def test_cosine_similarity_identical():
    """Identical vectors should have similarity 1.0."""
    from embeddings import cosine_similarity

    vec = [1.0, 2.0, 3.0, 4.0]
    assert cosine_similarity(vec, vec) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal():
    """Orthogonal vectors should have similarity 0.0."""
    from embeddings import cosine_similarity

    vec1 = [1.0, 0.0, 0.0]
    vec2 = [0.0, 1.0, 0.0]
    assert cosine_similarity(vec1, vec2) == pytest.approx(0.0)


def test_cosine_similarity_opposite():
    """Opposite vectors should have similarity -1.0."""
    from embeddings import cosine_similarity

    vec1 = [1.0, 2.0, 3.0]
    vec2 = [-1.0, -2.0, -3.0]
    assert cosine_similarity(vec1, vec2) == pytest.approx(-1.0)


def test_cosine_similarity_zero_vector():
    """Zero vector should return 0.0 similarity."""
    from embeddings import cosine_similarity

    vec1 = [1.0, 2.0, 3.0]
    vec2 = [0.0, 0.0, 0.0]
    assert cosine_similarity(vec1, vec2) == 0.0


def test_compute_novelty_score_empty_history():
    """First item should have novelty 1.0."""
    from embeddings import compute_novelty_score

    text_embedding = [1.0, 0.0, 0.0]
    novelty = compute_novelty_score("test", [], text_embedding)
    assert novelty == 1.0


def test_compute_novelty_score_identical():
    """Identical embedding should have novelty near 0."""
    from embeddings import compute_novelty_score

    text_embedding = [1.0, 2.0, 3.0]
    history = [text_embedding]  # Same embedding

    novelty = compute_novelty_score("test", history, text_embedding)
    assert novelty == pytest.approx(0.0, abs=0.01)


def test_compute_novelty_score_different():
    """Very different embedding should have high novelty."""
    from embeddings import compute_novelty_score

    text_embedding = [1.0, 0.0, 0.0]
    history = [[0.0, 1.0, 0.0]]  # Orthogonal

    novelty = compute_novelty_score("test", history, text_embedding)
    assert novelty == pytest.approx(1.0)


def test_compute_novelty_scores_batch():
    """Test batch novelty computation."""
    from embeddings import compute_novelty_scores_batch

    with patch('embeddings.get_embeddings_batch') as mock_get:
        mock_get.return_value = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],  # Same as first
        ]

        history = [[1.0, 0.0, 0.0]]  # First pattern already in history

        scores = compute_novelty_scores_batch(
            ["text1", "text2", "text3"],
            history
        )

        assert len(scores) == 3
        assert scores[0] == pytest.approx(0.0, abs=0.01)  # Same as history
        assert scores[1] == pytest.approx(1.0)  # Orthogonal
        assert scores[2] == pytest.approx(0.0, abs=0.01)  # Same as history


def test_is_novel():
    """Test novelty threshold check."""
    from embeddings import is_novel

    # High novelty should pass
    with patch('embeddings.compute_novelty_score', return_value=0.8):
        assert is_novel("text", [], threshold=0.15) is True

    # Low novelty should fail
    with patch('embeddings.compute_novelty_score', return_value=0.1):
        assert is_novel("text", [], threshold=0.15) is False


def test_embedding_cache(tmp_path):
    """Test embedding cache operations."""
    from embeddings import EmbeddingCache

    cache_file = tmp_path / "test_cache.json"
    cache = EmbeddingCache(cache_file)

    # Initially empty
    assert cache.get("test") is None

    # Set and get
    embedding = [1.0, 2.0, 3.0]
    cache.set("test", embedding)
    assert cache.get("test") == embedding

    # Persistence
    cache2 = EmbeddingCache(cache_file)
    assert cache2.get("test") == embedding

    # Clear
    cache.clear()
    assert cache.get("test") is None


def test_get_embedding_empty_text():
    """Empty text should return zero vector."""
    from embeddings import get_embedding, EMBEDDING_DIMENSIONS

    result = get_embedding("")
    assert len(result) == EMBEDDING_DIMENSIONS
    assert all(v == 0.0 for v in result)

    result = get_embedding("   ")
    assert all(v == 0.0 for v in result)


def test_get_embedding_with_mock_api():
    """Test get_embedding with mocked API."""
    from embeddings import get_embedding

    mock_response = MagicMock()
    mock_response.data = [MagicMock()]
    mock_response.data[0].embedding = [0.1, 0.2, 0.3]

    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = mock_response

    # Patch OpenAI at the openai module level (where it's imported from)
    with patch('embeddings.OPENAI_API_KEY', 'test-key'), \
         patch('openai.OpenAI', return_value=mock_client), \
         patch('embeddings.get_cache') as mock_cache:

        mock_cache.return_value.get.return_value = None

        result = get_embedding("test text", use_cache=False)

        assert result == [0.1, 0.2, 0.3]
        mock_client.embeddings.create.assert_called_once()


def test_get_embedding_uses_cache():
    """Test that cache is used when available."""
    from embeddings import get_embedding

    cached_embedding = [0.5, 0.5, 0.5]

    with patch('embeddings.get_cache') as mock_cache:
        mock_cache.return_value.get.return_value = cached_embedding

        result = get_embedding("cached text")

        assert result == cached_embedding
        # Should not call API
        mock_cache.return_value.set.assert_not_called()
