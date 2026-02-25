import json
import logging
from config import CC_TEMPERATURE, CC_MAX_TOKENS, CC_PROMPT_FILE
from memory_manager import get_knot_count
from api_client import chat_completion, APIClientError

logger = logging.getLogger(__name__)


class CritiqueError(Exception):
    """Error during critique."""
    pass


def load_prompt() -> str:
    """Load the convergent critic system prompt."""
    try:
        with open(CC_PROMPT_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise CritiqueError(f"CC prompt file not found: {CC_PROMPT_FILE}")
    except IOError as e:
        raise CritiqueError(f"Error reading CC prompt file: {e}")


def critique(artifacts: list[dict], context: dict) -> dict:
    """
    Critique artifacts and produce compressed output.

    Args:
        artifacts: List of artifacts from divergent generator
        context: Dict with 'crystallized' and 'open_knots' lists

    Returns:
        Dict with selected, rejected, compressed_models, new_open_knots,
        next_probe_directions, no_add

    Raises:
        CritiqueError: If critique fails after retries
    """
    system_prompt = load_prompt()
    user_prompt = build_user_prompt(artifacts, context)

    try:
        content = chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=CC_TEMPERATURE,
            max_tokens=CC_MAX_TOKENS,
            json_response=True
        )
    except APIClientError as e:
        logger.error(f"Critique failed: {e}")
        raise CritiqueError(f"API call failed: {e}") from e

    result = parse_critique(content)

    if not result:
        logger.warning("Empty critique result, using defaults")

    # Ensure required fields
    result.setdefault("selected", [])
    result.setdefault("rejected", [])
    result.setdefault("compressed_models", [])
    result.setdefault("new_open_knots", [])
    result.setdefault("next_probe_directions", [])
    result.setdefault("no_add", False)

    return result


def build_user_prompt(artifacts: list[dict], context: dict) -> str:
    """Build the user prompt for critique."""
    parts = []

    parts.append("## ARTIFACTS TO EVALUATE")
    for artifact in artifacts:
        parts.append(f"\n### Artifact: {artifact.get('id', 'unknown')}")
        parts.append(f"Type: {artifact.get('type', 'unknown')}")
        parts.append(f"Content: {artifact.get('content', '')}")
        parts.append(f"Novelty estimate: {artifact.get('novelty_estimate', 'N/A')}")

    parts.append("\n---")

    if context.get("crystallized"):
        parts.append("\n## EXISTING CRYSTALLIZED MEMORY")
        for i, item in enumerate(context["crystallized"][-5:]):
            parts.append(f"{i+1}. {item.get('content', str(item))}")
    else:
        parts.append("\n## EXISTING CRYSTALLIZED MEMORY\n(empty)")

    knot_count = get_knot_count()
    parts.append(f"\n## OPEN KNOTS (current count: {knot_count})")
    if context.get("open_knots"):
        for i, knot in enumerate(context["open_knots"]):
            parts.append(f"{i+1}. {knot.get('content', str(knot))}")
    else:
        parts.append("(none - YOU MUST create at least 1 new open knot)")

    parts.append("\nEvaluate and compress now.")

    return "\n".join(parts)


def parse_critique(content: str) -> dict:
    """Parse LLM response into critique result."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON object from response
        import re
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {}
