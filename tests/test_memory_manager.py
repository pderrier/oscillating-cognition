"""Tests for memory_manager module."""
import os
import json
import tempfile
import pytest
from unittest.mock import patch


@pytest.fixture
def temp_memory_dir(tmp_path):
    """Create temporary memory and scratch directories."""
    memory_dir = tmp_path / "memory"
    scratch_dir = tmp_path / "scratch"
    memory_dir.mkdir()
    scratch_dir.mkdir()

    # Patch config paths
    with patch('memory_manager.MEMORY_DIR', str(memory_dir)), \
         patch('memory_manager.SCRATCH_DIR', str(scratch_dir)), \
         patch('memory_manager.CRYSTALLIZED_FILE', str(memory_dir / "crystallized.json")), \
         patch('memory_manager.OPEN_KNOTS_FILE', str(memory_dir / "open_knots.json")), \
         patch('memory_manager.SCRATCH_FILE', str(scratch_dir / "last_cycle.json")):
        yield {
            "memory_dir": memory_dir,
            "scratch_dir": scratch_dir,
            "crystallized_file": memory_dir / "crystallized.json",
            "open_knots_file": memory_dir / "open_knots.json",
            "scratch_file": scratch_dir / "last_cycle.json"
        }


def test_load_crystallized_empty(temp_memory_dir):
    """Loading from non-existent file should return empty list."""
    from memory_manager import load_crystallized
    result = load_crystallized()
    assert result == []


def test_save_and_load_crystallized(temp_memory_dir):
    """Save and load crystallized memory."""
    from memory_manager import save_crystallized, load_crystallized

    data = [{"content": "Test model 1"}, {"content": "Test model 2"}]
    save_crystallized(data)

    loaded = load_crystallized()
    assert loaded == data


def test_append_crystallized(temp_memory_dir):
    """Append to crystallized memory."""
    from memory_manager import append_crystallized, load_crystallized

    append_crystallized(["Model A"])
    append_crystallized(["Model B", "Model C"])

    loaded = load_crystallized()
    assert len(loaded) == 3
    assert loaded[0]["content"] == "Model A"
    assert loaded[1]["content"] == "Model B"
    assert loaded[2]["content"] == "Model C"


def test_load_open_knots_empty(temp_memory_dir):
    """Loading from non-existent file should return empty list."""
    from memory_manager import load_open_knots
    result = load_open_knots()
    assert result == []


def test_add_open_knots(temp_memory_dir):
    """Add open knots."""
    from memory_manager import add_open_knots, load_open_knots, get_knot_count

    add_open_knots(["Knot 1"])
    assert get_knot_count() == 1

    add_open_knots(["Knot 2", "Knot 3"])
    assert get_knot_count() == 3

    knots = load_open_knots()
    assert knots[0]["content"] == "Knot 1"


def test_scratch_memory(temp_memory_dir):
    """Test scratch memory operations."""
    from memory_manager import write_scratch, load_scratch, clear_scratch

    # Initially empty
    assert load_scratch() == {}

    # Write and load
    data = {"cycle": 1, "artifacts": ["a", "b"]}
    write_scratch(data)
    assert load_scratch() == data

    # Clear
    clear_scratch()
    assert load_scratch() == {}


def test_build_context(temp_memory_dir):
    """Test context building."""
    from memory_manager import build_context, append_crystallized, add_open_knots

    append_crystallized(["Model X"])
    add_open_knots(["Tension Y"])

    ctx = build_context()
    assert len(ctx["crystallized"]) == 1
    assert len(ctx["open_knots"]) == 1
    assert ctx["crystallized"][0]["content"] == "Model X"
    assert ctx["open_knots"][0]["content"] == "Tension Y"


def test_initialize_memory(temp_memory_dir):
    """Test memory initialization."""
    from memory_manager import initialize_memory, load_crystallized, load_open_knots

    initialize_memory()

    # Should create empty files
    assert load_crystallized() == []
    assert load_open_knots() == []
