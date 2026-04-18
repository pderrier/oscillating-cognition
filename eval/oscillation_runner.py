"""
Oscillation condition: run the full DG → CC → TC loop for N cycles.
Wraps the orchestrator with isolated memory (temp dir) to avoid polluting main state.
"""
import json
import logging
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


def run_oscillation(seed: str, cycles: int = 3, model: str = None, skip_grounding: bool = False, grounding_mode: str = None) -> dict:
    """
    Run oscillating cognition on a seed with isolated memory.

    Uses a temp directory for memory/scratch so we don't pollute the main state.

    Returns:
        Dict with crystallized insights, open knots, metrics, and cycle details.
    """
    with tempfile.TemporaryDirectory(prefix="osc_eval_") as tmpdir:
        mem_dir = os.path.join(tmpdir, "memory")
        scratch_dir = os.path.join(tmpdir, "scratch")
        os.makedirs(mem_dir, exist_ok=True)
        os.makedirs(scratch_dir, exist_ok=True)

        # Patch config paths to use temp directory
        import config
        patches = {
            "config.MEMORY_DIR": mem_dir,
            "config.SCRATCH_DIR": scratch_dir,
            "config.CRYSTALLIZED_FILE": os.path.join(mem_dir, "crystallized.json"),
            "config.OPEN_KNOTS_FILE": os.path.join(mem_dir, "open_knots.json"),
            "config.SCRATCH_FILE": os.path.join(scratch_dir, "last_cycle.json"),
        }

        # Also patch memory_manager's imported copies
        import memory_manager
        original_values = {}
        for attr in ["MEMORY_DIR", "SCRATCH_DIR", "CRYSTALLIZED_FILE",
                      "OPEN_KNOTS_FILE", "SCRATCH_FILE"]:
            original_values[attr] = getattr(memory_manager, attr, None)

        try:
            # Apply patches
            for attr, val in [
                ("MEMORY_DIR", mem_dir),
                ("SCRATCH_DIR", scratch_dir),
                ("CRYSTALLIZED_FILE", os.path.join(mem_dir, "crystallized.json")),
                ("OPEN_KNOTS_FILE", os.path.join(mem_dir, "open_knots.json")),
                ("SCRATCH_FILE", os.path.join(scratch_dir, "last_cycle.json")),
            ]:
                setattr(config, attr, val)
                if hasattr(memory_manager, attr):
                    setattr(memory_manager, attr, val)

            # Also override model if specified
            original_model = config.OPENAI_MODEL
            if model:
                config.OPENAI_MODEL = model

            # Reset codex singleton so each trial gets a fresh thread
            import codex_client
            if codex_client._server is not None:
                codex_client._server.stop()
                codex_client._server = None

            from orchestrator import Orchestrator
            from grounding import ground
            from memory_manager import load_crystallized, load_open_knots

            logger.info(f"[OSCILLATION] Running {cycles} cycles — seed={seed[:50]}...")

            orch = Orchestrator(seed_topic=seed, max_cycles=cycles)
            summary = orch.run()

            crystallized = load_crystallized()
            open_knots = load_open_knots()

            # Run grounding phase (optional)
            grounding_result = {}
            if not skip_grounding:
                mode_label = f" (mode={grounding_mode})" if grounding_mode else ""
                logger.info(f"[OSCILLATION] Running grounding phase{mode_label}...")
                try:
                    ground_kwargs = {}
                    if grounding_mode:
                        ground_kwargs["mode"] = grounding_mode
                    grounding_result = ground(seed, crystallized, open_knots, **ground_kwargs)
                except Exception as e:
                    logger.warning(f"Grounding failed: {e}")

                grounding_result.setdefault("actions", [])
                grounding_result.setdefault("experiments", [])
                grounding_result.setdefault("questions", [])
                grounding_result.setdefault("synthesis", "")

            result = {
                "seed": seed,
                "summary": summary,
                "crystallized": crystallized,
                "open_knots": open_knots,
                "final": grounding_result,
            }

            return result

        finally:
            # Restore original values
            for attr, val in original_values.items():
                if val is not None:
                    setattr(memory_manager, attr, val)
                    setattr(config, attr, val)
            if model:
                config.OPENAI_MODEL = original_model
