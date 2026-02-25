"""Tests for MCP server tools."""
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.fixture
def mock_memory(tmp_path):
    """Setup mock memory directories."""
    memory_dir = tmp_path / "memory"
    scratch_dir = tmp_path / "scratch"
    memory_dir.mkdir()
    scratch_dir.mkdir()

    patches = {
        'config.MEMORY_DIR': str(memory_dir),
        'config.SCRATCH_DIR': str(scratch_dir),
        'config.CRYSTALLIZED_FILE': str(memory_dir / "crystallized.json"),
        'config.OPEN_KNOTS_FILE': str(memory_dir / "open_knots.json"),
        'config.SCRATCH_FILE': str(scratch_dir / "last_cycle.json"),
    }

    return patches, memory_dir, scratch_dir


@pytest.fixture
def mock_openai():
    """Mock OpenAI API responses."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "artifacts": [
            {"id": "test1", "type": "hypothesis", "content": "Test artifact"}
        ]
    })

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    return mock_client


def test_parse_artifacts_valid_json():
    """Test parsing valid artifact JSON."""
    from divergent_generator import parse_artifacts

    # Direct array
    content = '[{"type": "hypothesis", "content": "Test"}]'
    result = parse_artifacts(content)
    assert len(result) == 1
    assert result[0]["content"] == "Test"

    # Wrapped in object
    content = '{"artifacts": [{"type": "metaphor", "content": "Metaphor test"}]}'
    result = parse_artifacts(content)
    assert len(result) == 1
    assert result[0]["type"] == "metaphor"


def test_parse_artifacts_invalid_json():
    """Test parsing invalid JSON returns empty list."""
    from divergent_generator import parse_artifacts

    result = parse_artifacts("not valid json at all")
    assert result == []

    result = parse_artifacts("")
    assert result == []


def test_parse_artifacts_extracts_from_text():
    """Test extracting JSON from surrounding text."""
    from divergent_generator import parse_artifacts

    content = 'Here are the artifacts: [{"type": "idea", "content": "Extracted"}] end.'
    result = parse_artifacts(content)
    assert len(result) == 1
    assert result[0]["content"] == "Extracted"


def test_parse_critique_valid():
    """Test parsing valid critique JSON."""
    from convergent_critic import parse_critique

    content = json.dumps({
        "selected": ["id1"],
        "compressed_models": ["Model 1"],
        "new_open_knots": ["Knot 1"]
    })

    result = parse_critique(content)
    assert result["selected"] == ["id1"]
    assert result["compressed_models"] == ["Model 1"]


def test_parse_critique_invalid():
    """Test parsing invalid critique returns empty dict."""
    from convergent_critic import parse_critique

    result = parse_critique("invalid json")
    assert result == {}


@pytest.mark.asyncio
async def test_reset_cognition_tool(tmp_path):
    """Test reset_cognition clears memory."""
    memory_dir = tmp_path / "memory"
    scratch_dir = tmp_path / "scratch"
    memory_dir.mkdir()
    scratch_dir.mkdir()

    # Create some files
    (memory_dir / "crystallized.json").write_text("[]")
    (memory_dir / "open_knots.json").write_text("[]")

    # Patch at config level (where mcp_server imports from)
    import config
    original_memory = config.MEMORY_DIR
    original_scratch = config.SCRATCH_DIR
    original_cryst = config.CRYSTALLIZED_FILE
    original_knots = config.OPEN_KNOTS_FILE
    original_scratch_file = config.SCRATCH_FILE

    try:
        config.MEMORY_DIR = str(memory_dir)
        config.SCRATCH_DIR = str(scratch_dir)
        config.CRYSTALLIZED_FILE = str(memory_dir / "crystallized.json")
        config.OPEN_KNOTS_FILE = str(memory_dir / "open_knots.json")
        config.SCRATCH_FILE = str(scratch_dir / "last_cycle.json")

        # Reimport to pick up patched values
        import importlib
        import mcp_server
        importlib.reload(mcp_server)

        result = await mcp_server.call_tool("reset_cognition", {})

        assert len(result) == 1
        data = json.loads(result[0].text)
        assert "Memory cleared" in data["status"]
    finally:
        # Restore original values
        config.MEMORY_DIR = original_memory
        config.SCRATCH_DIR = original_scratch
        config.CRYSTALLIZED_FILE = original_cryst
        config.OPEN_KNOTS_FILE = original_knots
        config.SCRATCH_FILE = original_scratch_file


def test_build_user_prompt_with_seed():
    """Test user prompt includes seed topic."""
    from divergent_generator import build_user_prompt

    context = {
        "crystallized": [],
        "open_knots": [],
        "seed_topic": "consciousness and recursion"
    }

    prompt = build_user_prompt(context)
    assert "consciousness and recursion" in prompt
    assert "SEED TOPIC" in prompt


def test_build_user_prompt_with_context():
    """Test user prompt includes existing memory."""
    from divergent_generator import build_user_prompt

    context = {
        "crystallized": [{"content": "Existing model"}],
        "open_knots": [{"content": "Unresolved tension"}],
    }

    prompt = build_user_prompt(context)
    assert "Existing model" in prompt
    assert "Unresolved tension" in prompt


def test_critique_build_prompt():
    """Test critique prompt building."""
    from convergent_critic import build_user_prompt

    artifacts = [
        {"id": "a1", "type": "hypothesis", "content": "Test hypothesis"}
    ]
    context = {
        "crystallized": [{"content": "Prior model"}],
        "open_knots": []
    }

    with patch('convergent_critic.get_knot_count', return_value=0):
        prompt = build_user_prompt(artifacts, context)

    assert "Test hypothesis" in prompt
    assert "Prior model" in prompt
    assert "a1" in prompt
