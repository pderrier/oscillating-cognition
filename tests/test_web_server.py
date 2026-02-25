"""Tests for web_server module."""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path):
    """Create test client with mocked memory."""
    memory_dir = tmp_path / "memory"
    scratch_dir = tmp_path / "scratch"
    memory_dir.mkdir()
    scratch_dir.mkdir()

    # Create empty memory files
    (memory_dir / "crystallized.json").write_text("[]")
    (memory_dir / "open_knots.json").write_text("[]")

    import config
    original_memory = config.MEMORY_DIR
    original_scratch = config.SCRATCH_DIR
    original_cryst = config.CRYSTALLIZED_FILE
    original_knots = config.OPEN_KNOTS_FILE
    original_scratch_file = config.SCRATCH_FILE

    config.MEMORY_DIR = str(memory_dir)
    config.SCRATCH_DIR = str(scratch_dir)
    config.CRYSTALLIZED_FILE = str(memory_dir / "crystallized.json")
    config.OPEN_KNOTS_FILE = str(memory_dir / "open_knots.json")
    config.SCRATCH_FILE = str(scratch_dir / "last_cycle.json")

    # Reload modules to pick up patched config
    import importlib
    import memory_manager
    import web_server
    importlib.reload(memory_manager)
    importlib.reload(web_server)

    yield TestClient(web_server.app)

    # Restore
    config.MEMORY_DIR = original_memory
    config.SCRATCH_DIR = original_scratch
    config.CRYSTALLIZED_FILE = original_cryst
    config.OPEN_KNOTS_FILE = original_knots
    config.SCRATCH_FILE = original_scratch_file


def test_get_status_empty(client):
    """Test status endpoint with empty memory."""
    response = client.get("/api/status")
    assert response.status_code == 200

    data = response.json()
    assert data["crystallized_count"] == 0
    assert data["open_knots_count"] == 0


def test_get_insights_empty(client):
    """Test insights endpoint with empty memory."""
    response = client.get("/api/insights")
    assert response.status_code == 200
    assert response.json() == []


def test_get_knots_empty(client):
    """Test knots endpoint with empty memory."""
    response = client.get("/api/knots")
    assert response.status_code == 200
    assert response.json() == []


def test_get_raw_memory(client):
    """Test raw memory endpoint."""
    response = client.get("/api/memory/raw")
    assert response.status_code == 200

    data = response.json()
    assert "crystallized" in data
    assert "open_knots" in data


def test_root_returns_html(client):
    """Test root endpoint returns HTML."""
    response = client.get("/")
    assert response.status_code == 200
    # Should return some HTML (either index.html or fallback)
    assert "html" in response.text.lower()


def test_insights_with_data(client, tmp_path):
    """Test insights endpoint with data."""
    import json
    import config

    # Add some data
    crystallized = [
        {"content": "First insight", "cycle_added": 0},
        {"content": "Second insight", "cycle_added": 1}
    ]
    with open(config.CRYSTALLIZED_FILE, "w") as f:
        json.dump(crystallized, f)

    response = client.get("/api/insights")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["content"] == "First insight"
    assert data[0]["index"] == 0


def test_insights_with_limit(client, tmp_path):
    """Test insights endpoint with limit."""
    import json
    import config

    crystallized = [
        {"content": f"Insight {i}", "cycle_added": i}
        for i in range(10)
    ]
    with open(config.CRYSTALLIZED_FILE, "w") as f:
        json.dump(crystallized, f)

    response = client.get("/api/insights?limit=3")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3


def test_insights_with_offset(client, tmp_path):
    """Test insights endpoint with offset."""
    import json
    import config

    crystallized = [
        {"content": f"Insight {i}", "cycle_added": i}
        for i in range(10)
    ]
    with open(config.CRYSTALLIZED_FILE, "w") as f:
        json.dump(crystallized, f)

    response = client.get("/api/insights?offset=5&limit=3")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3
    assert data[0]["content"] == "Insight 5"
    assert data[0]["index"] == 5


def test_knots_with_data(client, tmp_path):
    """Test knots endpoint with data."""
    import json
    import config

    knots = [
        {"content": "Tension A", "cycle_added": 0},
        {"content": "Tension B", "cycle_added": 1}
    ]
    with open(config.OPEN_KNOTS_FILE, "w") as f:
        json.dump(knots, f)

    response = client.get("/api/knots")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["content"] == "Tension A"


def test_clear_memory(client, tmp_path):
    """Test memory clearing endpoint."""
    import json
    import config

    # Add some data first
    with open(config.CRYSTALLIZED_FILE, "w") as f:
        json.dump([{"content": "test"}], f)

    # Clear
    response = client.delete("/api/memory")
    assert response.status_code == 200
    assert response.json()["status"] == "Memory cleared"

    # Verify cleared
    response = client.get("/api/status")
    assert response.json()["crystallized_count"] == 0
