"""
Grounding phase: transform abstract insights into actionable proposals.

Takes crystallized insights and open knots, and generates concrete
actions, experiments, and questions in the context of the original seed.
"""
import json
import logging
from config import (
    CC_TEMPERATURE, CC_MAX_TOKENS,
    BASE_DIR
)
from api_client import chat_completion, APIClientError

logger = logging.getLogger(__name__)

GROUNDING_PROMPT_FILE = BASE_DIR / "prompts" / "grounding_prompt.txt"


class GroundingError(Exception):
    """Error during grounding phase."""
    pass


def load_prompt() -> str:
    """Load the grounding system prompt."""
    try:
        with open(GROUNDING_PROMPT_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise GroundingError(f"Grounding prompt file not found: {GROUNDING_PROMPT_FILE}")
    except IOError as e:
        raise GroundingError(f"Error reading grounding prompt file: {e}")


def ground(
    seed_topic: str,
    crystallized: list[dict],
    open_knots: list[dict],
    temperature: float = None
) -> dict:
    """
    Ground abstract insights into actionable proposals.

    Args:
        seed_topic: The original topic that started the exploration
        crystallized: List of crystallized insight dicts
        open_knots: List of open knot dicts
        temperature: Override temperature (default: same as CC)

    Returns:
        Dict with actions, experiments, questions, synthesis

    Raises:
        GroundingError: If grounding fails
    """
    if temperature is None:
        temperature = CC_TEMPERATURE

    if not seed_topic:
        raise GroundingError("Seed topic is required for grounding")

    system_prompt = load_prompt()
    user_prompt = build_user_prompt(seed_topic, crystallized, open_knots)

    try:
        content = chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=CC_MAX_TOKENS,
            json_response=True
        )
    except APIClientError as e:
        logger.error(f"Grounding failed: {e}")
        raise GroundingError(f"API call failed: {e}") from e

    result = parse_grounding(content)

    # Ensure required fields
    result.setdefault("actions", [])
    result.setdefault("experiments", [])
    result.setdefault("questions", [])
    result.setdefault("synthesis", "")

    return result


def build_user_prompt(
    seed_topic: str,
    crystallized: list[dict],
    open_knots: list[dict]
) -> str:
    """Build the user prompt for grounding."""
    parts = []

    parts.append(f"## ORIGINAL SEED TOPIC\n{seed_topic}")
    parts.append("")

    if crystallized:
        parts.append("## CRYSTALLIZED INSIGHTS")
        for i, item in enumerate(crystallized):
            content = item.get("content", str(item))
            parts.append(f"{i+1}. {content}")
    else:
        parts.append("## CRYSTALLIZED INSIGHTS\n(none)")

    parts.append("")

    if open_knots:
        parts.append("## OPEN KNOTS (unresolved tensions)")
        for i, knot in enumerate(open_knots):
            content = knot.get("content", str(knot))
            parts.append(f"{i+1}. {content}")
    else:
        parts.append("## OPEN KNOTS\n(none)")

    parts.append("\nGround these insights into actionable proposals for the seed topic.")

    return "\n".join(parts)


def parse_grounding(content: str) -> dict:
    """Parse LLM response into grounding result."""
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
        logger.warning("Failed to parse grounding response")
        return {}


def format_grounding_result(result: dict) -> str:
    """Format grounding result for display."""
    lines = []

    if result.get("synthesis"):
        lines.append("## Synthesis")
        lines.append(result["synthesis"])
        lines.append("")

    if result.get("actions"):
        lines.append("## Actions")
        for i, action in enumerate(result["actions"], 1):
            desc = action.get("description", str(action))
            effort = action.get("effort", "?")
            rationale = action.get("rationale", "")
            lines.append(f"{i}. [{effort}] {desc}")
            if rationale:
                lines.append(f"   → {rationale}")
        lines.append("")

    if result.get("experiments"):
        lines.append("## Experiments")
        for i, exp in enumerate(result["experiments"], 1):
            desc = exp.get("description", str(exp))
            effort = exp.get("effort", "?")
            rationale = exp.get("rationale", "")
            lines.append(f"{i}. [{effort}] {desc}")
            if rationale:
                lines.append(f"   → {rationale}")
        lines.append("")

    if result.get("questions"):
        lines.append("## Questions")
        for i, q in enumerate(result["questions"], 1):
            desc = q.get("description", str(q))
            effort = q.get("effort", "?")
            rationale = q.get("rationale", "")
            lines.append(f"{i}. [{effort}] {desc}")
            if rationale:
                lines.append(f"   → {rationale}")

    return "\n".join(lines)
