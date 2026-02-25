import json
import uuid
import logging
from config import (
    DG_TEMPERATURE, DG_MAX_TOKENS, DG_ARTIFACT_COUNT,
    DG_PROMPT_FILE
)
from api_client import chat_completion, APIClientError

logger = logging.getLogger(__name__)


class GenerationError(Exception):
    """Error during artifact generation."""
    pass


def load_prompt() -> str:
    """Load the divergent generator system prompt."""
    try:
        with open(DG_PROMPT_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise GenerationError(f"DG prompt file not found: {DG_PROMPT_FILE}")
    except IOError as e:
        raise GenerationError(f"Error reading DG prompt file: {e}")


def generate(context: dict, temperature: float = None, artifact_count: int = None) -> list[dict]:
    """
    Generate divergent artifacts from the given context.

    Args:
        context: Dict with 'crystallized' and 'open_knots' lists
        temperature: Override default temperature (for forced divergence)
        artifact_count: Override default artifact count

    Returns:
        List of artifact dicts with id, type, content, novelty_estimate

    Raises:
        GenerationError: If generation fails after retries
    """
    if temperature is None:
        temperature = DG_TEMPERATURE
    if artifact_count is None:
        artifact_count = DG_ARTIFACT_COUNT

    system_prompt = load_prompt().format(artifact_count=artifact_count)
    user_prompt = build_user_prompt(context)

    try:
        content = chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=DG_MAX_TOKENS,
            json_response=True
        )
    except APIClientError as e:
        logger.error(f"Divergent generation failed: {e}")
        raise GenerationError(f"API call failed: {e}") from e

    artifacts = parse_artifacts(content)

    if not artifacts:
        logger.warning("No artifacts parsed from response, returning empty list")

    # Ensure unique IDs
    for artifact in artifacts:
        if "id" not in artifact or not artifact["id"]:
            artifact["id"] = f"dg_{uuid.uuid4().hex[:8]}"

    return artifacts


def build_user_prompt(context: dict) -> str:
    """Build the user prompt from context."""
    parts = []

    if context.get("crystallized"):
        parts.append("## CRYSTALLIZED MEMORY (existing compressed structures)")
        for i, item in enumerate(context["crystallized"][-5:]):  # Last 5
            parts.append(f"{i+1}. {item.get('content', str(item))}")
    else:
        parts.append("## CRYSTALLIZED MEMORY\n(empty - this is the first cycle)")

    parts.append("")

    if context.get("open_knots"):
        parts.append("## OPEN KNOTS (unresolved tensions to engage with)")
        for i, knot in enumerate(context["open_knots"]):
            parts.append(f"{i+1}. {knot.get('content', str(knot))}")
    else:
        parts.append("## OPEN KNOTS\n(none yet - generate material that creates tension)")

    if context.get("seed_topic"):
        parts.append(f"\n## SEED TOPIC\n{context['seed_topic']}")

    if context.get("probe_directions"):
        parts.append("\n## SUGGESTED PROBE DIRECTIONS")
        for direction in context["probe_directions"]:
            parts.append(f"- {direction}")

    parts.append("\nGenerate divergent artifacts now.")

    return "\n".join(parts)


def parse_artifacts(content: str) -> list[dict]:
    """Parse LLM response into artifact list."""
    try:
        data = json.loads(content)
        # Handle both direct array and wrapped object
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            if "artifacts" in data:
                return data["artifacts"]
            # Maybe the dict itself is a single artifact
            if "type" in data and "content" in data:
                return [data]
        return []
    except json.JSONDecodeError:
        # Try to extract JSON array from response
        import re
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return []
