import json
import os
from typing import Any
from config import CRYSTALLIZED_FILE, OPEN_KNOTS_FILE, SCRATCH_FILE, MEMORY_DIR, SCRATCH_DIR


def _ensure_dirs():
    """Create memory and scratch directories if they don't exist."""
    os.makedirs(MEMORY_DIR, exist_ok=True)
    os.makedirs(SCRATCH_DIR, exist_ok=True)


def _load_json(filepath: str, default: Any = None) -> Any:
    """Load JSON file, returning default if file doesn't exist."""
    if default is None:
        default = []
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def _save_json(filepath: str, data: Any):
    """Save data to JSON file."""
    _ensure_dirs()
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# Crystallized Memory (persistent compressed structures)
def load_crystallized() -> list[dict]:
    """Load crystallized memory - compressed, validated structures."""
    return _load_json(CRYSTALLIZED_FILE, [])


def save_crystallized(data: list[dict]):
    """Save crystallized memory."""
    _save_json(CRYSTALLIZED_FILE, data)


def append_crystallized(models: list[str]):
    """Append new compressed models to crystallized memory."""
    current = load_crystallized()
    for model in models:
        current.append({
            "content": model,
            "cycle_added": len(current)
        })
    save_crystallized(current)


# Open Knots (persistent unresolved tensions)
def load_open_knots() -> list[dict]:
    """Load open knots - unresolved tensions that must be preserved."""
    return _load_json(OPEN_KNOTS_FILE, [])


def save_open_knots(data: list[dict]):
    """Save open knots."""
    _save_json(OPEN_KNOTS_FILE, data)


def add_open_knots(knots: list[str]):
    """Add new open knots."""
    current = load_open_knots()
    for knot in knots:
        current.append({
            "content": knot,
            "cycle_added": len(current)
        })
    save_open_knots(current)


def get_knot_count() -> int:
    """Return count of active open knots."""
    return len(load_open_knots())


# Scratch Memory (volatile per-cycle data)
def write_scratch(data: dict):
    """Write current cycle data to scratch."""
    _save_json(SCRATCH_FILE, data)


def load_scratch() -> dict:
    """Load last cycle scratch data."""
    return _load_json(SCRATCH_FILE, {})


def clear_scratch():
    """Clear scratch memory."""
    if os.path.exists(SCRATCH_FILE):
        os.remove(SCRATCH_FILE)


# Context Building
def build_context() -> dict:
    """Build context from crystallized memory and open knots."""
    return {
        "crystallized": load_crystallized(),
        "open_knots": load_open_knots()
    }


# Initialization
def initialize_memory():
    """Initialize empty memory files if they don't exist."""
    _ensure_dirs()
    if not os.path.exists(CRYSTALLIZED_FILE):
        save_crystallized([])
    if not os.path.exists(OPEN_KNOTS_FILE):
        save_open_knots([])
    clear_scratch()
