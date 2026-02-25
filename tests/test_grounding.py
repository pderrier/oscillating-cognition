"""Tests for grounding module."""
import pytest
from unittest.mock import patch, MagicMock


def test_build_user_prompt_with_all_inputs():
    """Test prompt building with all inputs."""
    from grounding import build_user_prompt

    seed = "improve CI/CD reliability"
    crystallized = [
        {"content": "Insight about pipelines"},
        {"content": "Insight about testing"}
    ]
    knots = [
        {"content": "Tension between speed and safety"}
    ]

    prompt = build_user_prompt(seed, crystallized, knots)

    assert "improve CI/CD reliability" in prompt
    assert "Insight about pipelines" in prompt
    assert "Insight about testing" in prompt
    assert "Tension between speed and safety" in prompt


def test_build_user_prompt_empty_inputs():
    """Test prompt building with empty inputs."""
    from grounding import build_user_prompt

    prompt = build_user_prompt("test seed", [], [])

    assert "test seed" in prompt
    assert "(none)" in prompt


def test_parse_grounding_valid():
    """Test parsing valid grounding JSON."""
    from grounding import parse_grounding
    import json

    content = json.dumps({
        "actions": [{"description": "Do X", "rationale": "Because Y", "effort": "low"}],
        "experiments": [],
        "questions": [{"description": "Ask Z?", "rationale": "To understand", "effort": "medium"}],
        "synthesis": "Summary here"
    })

    result = parse_grounding(content)

    assert len(result["actions"]) == 1
    assert result["actions"][0]["description"] == "Do X"
    assert result["synthesis"] == "Summary here"


def test_parse_grounding_invalid():
    """Test parsing invalid JSON returns empty dict."""
    from grounding import parse_grounding

    result = parse_grounding("not valid json")
    assert result == {}


def test_parse_grounding_extracts_from_text():
    """Test extracting JSON from surrounding text."""
    from grounding import parse_grounding
    import json

    inner = {"actions": [{"description": "Test"}], "synthesis": "Ok"}
    content = f'Here is the result: {json.dumps(inner)} end.'

    result = parse_grounding(content)
    assert result["synthesis"] == "Ok"


def test_format_grounding_result():
    """Test formatting grounding result for display."""
    from grounding import format_grounding_result

    result = {
        "synthesis": "This is the summary",
        "actions": [
            {"description": "Do something", "rationale": "Because", "effort": "low"}
        ],
        "experiments": [
            {"description": "Test hypothesis", "rationale": "To validate", "effort": "medium"}
        ],
        "questions": [
            {"description": "Ask someone", "rationale": "To learn", "effort": "high"}
        ]
    }

    formatted = format_grounding_result(result)

    assert "## Synthesis" in formatted
    assert "This is the summary" in formatted
    assert "## Actions" in formatted
    assert "[low] Do something" in formatted
    assert "## Experiments" in formatted
    assert "[medium] Test hypothesis" in formatted
    assert "## Questions" in formatted
    assert "[high] Ask someone" in formatted


def test_ground_requires_seed():
    """Test that ground requires a seed topic."""
    from grounding import ground, GroundingError

    with pytest.raises(GroundingError) as exc_info:
        ground("", [], [])

    assert "Seed topic is required" in str(exc_info.value)


def test_ground_with_mock_api():
    """Test ground with mocked API."""
    from grounding import ground
    import json

    mock_response = json.dumps({
        "actions": [{"description": "Action 1", "rationale": "R1", "effort": "low"}],
        "experiments": [],
        "questions": [],
        "synthesis": "Test synthesis"
    })

    with patch('grounding.chat_completion', return_value=mock_response):
        result = ground(
            "test seed",
            [{"content": "insight 1"}],
            [{"content": "knot 1"}]
        )

    assert result["synthesis"] == "Test synthesis"
    assert len(result["actions"]) == 1


def test_ground_sets_defaults():
    """Test that ground sets default values for missing fields."""
    from grounding import ground
    import json

    # Response missing some fields
    mock_response = json.dumps({
        "synthesis": "Only synthesis"
    })

    with patch('grounding.chat_completion', return_value=mock_response):
        result = ground("seed", [{"content": "x"}], [])

    assert result["actions"] == []
    assert result["experiments"] == []
    assert result["questions"] == []
    assert result["synthesis"] == "Only synthesis"
