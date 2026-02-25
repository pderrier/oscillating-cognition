"""Tests for config module - verify absolute paths work correctly."""
import os
from pathlib import Path


def test_base_dir_is_absolute():
    """BASE_DIR should be an absolute path."""
    from config import BASE_DIR
    assert BASE_DIR.is_absolute(), f"BASE_DIR should be absolute, got: {BASE_DIR}"


def test_base_dir_exists():
    """BASE_DIR should point to existing directory."""
    from config import BASE_DIR
    assert BASE_DIR.exists(), f"BASE_DIR does not exist: {BASE_DIR}"


def test_file_paths_are_absolute():
    """All file paths should be absolute."""
    from config import (
        MEMORY_DIR, SCRATCH_DIR, PROMPTS_DIR,
        CRYSTALLIZED_FILE, OPEN_KNOTS_FILE, SCRATCH_FILE,
        DG_PROMPT_FILE, CC_PROMPT_FILE
    )

    paths = [
        ("MEMORY_DIR", MEMORY_DIR),
        ("SCRATCH_DIR", SCRATCH_DIR),
        ("PROMPTS_DIR", PROMPTS_DIR),
        ("CRYSTALLIZED_FILE", CRYSTALLIZED_FILE),
        ("OPEN_KNOTS_FILE", OPEN_KNOTS_FILE),
        ("SCRATCH_FILE", SCRATCH_FILE),
        ("DG_PROMPT_FILE", DG_PROMPT_FILE),
        ("CC_PROMPT_FILE", CC_PROMPT_FILE),
    ]

    for name, path in paths:
        assert os.path.isabs(path), f"{name} should be absolute, got: {path}"


def test_prompt_files_exist():
    """Prompt files should exist."""
    from config import DG_PROMPT_FILE, CC_PROMPT_FILE

    assert os.path.exists(DG_PROMPT_FILE), f"DG prompt not found: {DG_PROMPT_FILE}"
    assert os.path.exists(CC_PROMPT_FILE), f"CC prompt not found: {CC_PROMPT_FILE}"


def test_paths_inside_base_dir():
    """All paths should be inside BASE_DIR."""
    from config import (
        BASE_DIR, MEMORY_DIR, SCRATCH_DIR, PROMPTS_DIR,
        CRYSTALLIZED_FILE, OPEN_KNOTS_FILE, SCRATCH_FILE,
        DG_PROMPT_FILE, CC_PROMPT_FILE
    )

    base = str(BASE_DIR)
    paths = [MEMORY_DIR, SCRATCH_DIR, PROMPTS_DIR,
             CRYSTALLIZED_FILE, OPEN_KNOTS_FILE, SCRATCH_FILE,
             DG_PROMPT_FILE, CC_PROMPT_FILE]

    for path in paths:
        assert path.startswith(base), f"Path {path} should be inside {base}"
