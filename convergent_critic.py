import json
from openai import OpenAI
from config import (
    OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL,
    CC_TEMPERATURE, CC_MAX_TOKENS,
    CC_PROMPT_FILE
)
from memory_manager import get_knot_count


def load_prompt() -> str:
    """Load the convergent critic system prompt."""
    with open(CC_PROMPT_FILE, "r") as f:
        return f.read()


def critique(artifacts: list[dict], context: dict) -> dict:
    """
    Critique artifacts and produce compressed output.

    Args:
        artifacts: List of artifacts from divergent generator
        context: Dict with 'crystallized' and 'open_knots' lists

    Returns:
        Dict with selected, rejected, compressed_models, new_open_knots,
        next_probe_directions, no_add
    """
    client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)

    system_prompt = load_prompt()

    user_prompt = build_user_prompt(artifacts, context)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=CC_TEMPERATURE,
        max_tokens=CC_MAX_TOKENS,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content
    result = parse_critique(content)

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
