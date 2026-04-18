"""
Blind judge: evaluates two anonymous grounded outputs on fixed criteria.
Both outputs have the same format: actions, experiments, questions, synthesis.
Does not know which method produced which output.
"""
import json
import logging
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import chat_completion

logger = logging.getLogger(__name__)

JUDGE_PROMPT = """You are an impartial evaluator of idea quality. You will compare two grounded explorations of the same topic, produced by two different methods (you don't know which).

Both outputs went through a thinking process and were then grounded into actionable proposals.

## TOPIC
{seed}

## OUTPUT X

### Actions
{actions_x}

### Experiments
{experiments_x}

### Questions
{questions_x}

### Synthesis
{synthesis_x}

---

## OUTPUT Y

### Actions
{actions_y}

### Experiments
{experiments_y}

### Questions
{questions_y}

### Synthesis
{synthesis_y}

---

## EVALUATION CRITERIA

Score each output (X and Y) on a 1-10 scale for each criterion:

1. **Novelty** — How surprising and non-obvious are the proposals? Do they go beyond conventional takes?
2. **Depth** — Do the proposals show genuine engagement with complexity, or are they surface-level?
3. **Specificity** — Are proposals concrete enough to act on, with clear rationale?
4. **Internal tension** — Does the output hold productive contradictions, or does it flatten everything into agreement?
5. **Emergent insight** — Are there ideas that are MORE than the sum of the inputs? Unexpected combinations?
6. **Human-likeness** — Does this read like a thoughtful human exploration, or like a predictable LLM list?

Then provide:
- A brief qualitative comparison (3-5 sentences)
- Your overall preference: X, Y, or tie

Output ONLY a JSON object:
{{
  "scores": {{
    "X": {{"novelty": N, "depth": N, "specificity": N, "internal_tension": N, "emergent_insight": N, "human_likeness": N}},
    "Y": {{"novelty": N, "depth": N, "specificity": N, "internal_tension": N, "emergent_insight": N, "human_likeness": N}}
  }},
  "qualitative": "...",
  "preference": "X" | "Y" | "tie"
}}
"""


def judge_blind(
    seed: str,
    output_a: dict,
    output_b: dict,
    model: str = None
) -> dict:
    """
    Blind evaluation of two grounded outputs. Randomly assigns X/Y labels.

    Args:
        seed: The topic both outputs explored
        output_a: First output (grounding format: actions, experiments, questions, synthesis)
        output_b: Second output (same format)
        model: Optional model override for judge

    Returns:
        Dict with scores, preference, and which method was X/Y
    """
    # Randomize assignment to prevent position bias
    coin = random.random() > 0.5
    if coin:
        x_output, y_output = output_a, output_b
        x_method, y_method = "oscillation", "baseline"
    else:
        x_output, y_output = output_b, output_a
        x_method, y_method = "baseline", "oscillation"

    prompt = JUDGE_PROMPT.format(
        seed=seed,
        actions_x=_format_grounding_items(x_output.get("actions", [])),
        experiments_x=_format_grounding_items(x_output.get("experiments", [])),
        questions_x=_format_grounding_items(x_output.get("questions", [])),
        synthesis_x=x_output.get("synthesis", "(none)"),
        actions_y=_format_grounding_items(y_output.get("actions", [])),
        experiments_y=_format_grounding_items(y_output.get("experiments", [])),
        questions_y=_format_grounding_items(y_output.get("questions", [])),
        synthesis_y=y_output.get("synthesis", "(none)"),
    )

    # Reset codex singleton so judge gets a fresh thread
    try:
        import codex_client
        if codex_client._server is not None:
            codex_client._server.stop()
            codex_client._server = None
    except ImportError:
        pass

    logger.info(f"[JUDGE] Evaluating seed={seed[:50]}... (X={x_method}, Y={y_method})")

    raw = chat_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500,
        model=model,
        json_response=True
    )

    result = _safe_parse(raw)

    # Map X/Y back to method names
    result["mapping"] = {"X": x_method, "Y": y_method}
    result["seed"] = seed

    pref = result.get("preference", "tie")
    if pref == "X":
        result["preferred_method"] = x_method
    elif pref == "Y":
        result["preferred_method"] = y_method
    else:
        result["preferred_method"] = "tie"

    scores = result.get("scores", {})
    result["scores_by_method"] = {
        x_method: scores.get("X", {}),
        y_method: scores.get("Y", {})
    }

    return result


def _format_grounding_items(items: list) -> str:
    """Format actions/experiments/questions for display."""
    if not items:
        return "(none)"
    lines = []
    for i, item in enumerate(items, 1):
        if isinstance(item, dict):
            desc = item.get("description", str(item))
            effort = item.get("effort", "")
            rationale = item.get("rationale", "")
            line = f"{i}. [{effort}] {desc}" if effort else f"{i}. {desc}"
            if rationale:
                line += f"\n   Rationale: {rationale}"
            lines.append(line)
        else:
            lines.append(f"{i}. {item}")
    return "\n".join(lines)


def _safe_parse(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"raw": raw, "parse_error": True}
