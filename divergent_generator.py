import json
import uuid
from openai import OpenAI
from config import (
    OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL,
    DG_TEMPERATURE, DG_MAX_TOKENS, DG_ARTIFACT_COUNT,
    DG_PROMPT_FILE
)


def load_prompt() -> str:
    """Load the divergent generator system prompt."""
    with open(DG_PROMPT_FILE, "r") as f:
        return f.read()


def generate(context: dict, temperature: float = None, artifact_count: int = None) -> list[dict]:
    """
    Generate divergent artifacts from the given context.

    Args:
        context: Dict with 'crystallized' and 'open_knots' lists
        temperature: Override default temperature (for forced divergence)
        artifact_count: Override default artifact count

    Returns:
        List of artifact dicts with id, type, content, novelty_estimate
    """
    if temperature is None:
        temperature = DG_TEMPERATURE
    if artifact_count is None:
        artifact_count = DG_ARTIFACT_COUNT

    client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)

    system_prompt = load_prompt().format(artifact_count=artifact_count)

    user_prompt = build_user_prompt(context)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=DG_MAX_TOKENS,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content
    artifacts = parse_artifacts(content)

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
