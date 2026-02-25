import tiktoken
import numpy as np
from config import (
    TC_MIN_KNOTS, TC_COMPRESSION_TARGET, TC_NOVELTY_THRESHOLD,
    TC_FORCED_DIVERGENCE_TEMP, DG_TEMPERATURE
)
from memory_manager import get_knot_count


class TensionController:
    """Controls the balance between chaos and structure."""

    def __init__(self):
        self.history = []  # Track novelty scores for diminishing returns detection
        self.current_dg_temp = DG_TEMPERATURE
        self.forced_divergence = False
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4o")
        except Exception:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def compute_compression_delta(self, raw_text: str, compressed_text: str) -> float:
        """
        Compute compression ratio.
        Returns: ratio of compressed to raw tokens (lower = more compression)
        """
        raw_tokens = len(self.tokenizer.encode(raw_text))
        compressed_tokens = len(self.tokenizer.encode(compressed_text))

        if raw_tokens == 0:
            return 1.0

        return compressed_tokens / raw_tokens

    def compute_novelty_score(self, text: str, history_texts: list[str] = None) -> float:
        """
        Compute lexical diversity as novelty heuristic.
        Returns: score between 0 and 1 (higher = more novel)
        """
        if not text:
            return 0.0

        words = text.lower().split()
        if not words:
            return 0.0

        # Type-token ratio (unique words / total words)
        unique_words = set(words)
        ttr = len(unique_words) / len(words)

        # If we have history, compute overlap penalty
        if history_texts:
            history_words = set()
            for h in history_texts[-5:]:  # Last 5 cycles
                history_words.update(h.lower().split())

            if history_words:
                overlap = len(unique_words & history_words) / len(unique_words)
                novelty = ttr * (1 - overlap * 0.5)  # Penalize overlap
            else:
                novelty = ttr
        else:
            novelty = ttr

        return min(1.0, max(0.0, novelty))

    def get_knot_preservation_score(self) -> int:
        """Return count of active open knots."""
        return get_knot_count()

    def compute_metrics(self, cycle_data: dict) -> dict:
        """
        Compute all tension metrics for the current cycle.

        Args:
            cycle_data: Dict with 'raw_artifacts', 'compressed_models', 'history'

        Returns:
            Dict with compression_delta, novelty_score, knot_count
        """
        raw_text = " ".join(
            a.get("content", "") for a in cycle_data.get("raw_artifacts", [])
        )
        compressed_text = " ".join(cycle_data.get("compressed_models", []))

        compression_delta = self.compute_compression_delta(raw_text, compressed_text)

        novelty = self.compute_novelty_score(
            raw_text,
            cycle_data.get("history", [])
        )
        self.history.append(novelty)

        knot_count = self.get_knot_preservation_score()

        return {
            "compression_delta": compression_delta,
            "novelty_score": novelty,
            "knot_count": knot_count
        }

    def get_adjustments(self, metrics: dict) -> dict:
        """
        Determine parameter adjustments based on metrics.

        Returns:
            Dict with temperature, forced_divergence flag, recommendations
        """
        adjustments = {
            "temperature": self.current_dg_temp,
            "forced_divergence": False,
            "recommendations": []
        }

        # Check knot preservation
        if metrics["knot_count"] < TC_MIN_KNOTS:
            adjustments["forced_divergence"] = True
            adjustments["temperature"] = TC_FORCED_DIVERGENCE_TEMP
            adjustments["recommendations"].append(
                "TRIGGER: No open knots - forcing chaos injection"
            )
            self.forced_divergence = True
        else:
            self.forced_divergence = False

        # Check compression
        if metrics["compression_delta"] < 0.2:
            adjustments["recommendations"].append(
                "WARNING: High compression - system may be becoming rigid"
            )
            adjustments["temperature"] = min(1.1, self.current_dg_temp + 0.1)
        elif metrics["compression_delta"] > 0.8:
            adjustments["recommendations"].append(
                "WARNING: Low compression - system may be producing noise"
            )
            adjustments["temperature"] = max(0.7, self.current_dg_temp - 0.1)

        # Check novelty
        if metrics["novelty_score"] < TC_NOVELTY_THRESHOLD:
            adjustments["recommendations"].append(
                "WARNING: Low novelty detected"
            )

        self.current_dg_temp = adjustments["temperature"]

        return adjustments

    def detect_diminishing_returns(self, window: int = None) -> bool:
        """
        Check if recent cycles show diminishing returns.

        Returns:
            True if last N cycles all have novelty below threshold
        """
        from config import DIMINISHING_RETURNS_CYCLES
        if window is None:
            window = DIMINISHING_RETURNS_CYCLES

        if len(self.history) < window:
            return False

        recent = self.history[-window:]
        return all(n < TC_NOVELTY_THRESHOLD for n in recent)

    def get_state(self) -> dict:
        """Return current controller state for logging."""
        return {
            "current_temperature": self.current_dg_temp,
            "forced_divergence": self.forced_divergence,
            "novelty_history": self.history[-10:],
            "knot_count": self.get_knot_preservation_score()
        }
