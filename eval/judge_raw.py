"""
Blind judge for raw (pre-grounding) outputs.
Oscillation raw = crystallized insights + open knots
Baseline raw = final ideas + open questions + synthesis
"""
import json
import logging
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import chat_completion

logger = logging.getLogger(__name__)

JUDGE_RAW_PROMPT = """You are an impartial evaluator of idea quality. You will compare the raw thinking output of two different exploration processes on the same topic. Neither output has been polished or reformatted — you are seeing the direct products of each thinking process.

## TOPIC
{seed}

## OUTPUT X

### Insights / Compressed Ideas
{insights_x}

### Open Questions / Unresolved Tensions
{questions_x}

{synthesis_x}

---

## OUTPUT Y

### Insights / Compressed Ideas
{insights_y}

### Open Questions / Unresolved Tensions
{questions_y}

{synthesis_y}

---

## EVALUATION CRITERIA

Score each output (X and Y) on a 1-10 scale for each criterion:

1. **Novelty** — How surprising and non-obvious are the ideas? Do they go beyond conventional takes on this topic?
2. **Depth** — Do the ideas show genuine engagement with complexity, or are they surface-level?
3. **Specificity** — Are the insights concrete and precise, or vague generalities?
4. **Internal tension** — Does the output hold productive contradictions and unresolved questions, or does it flatten everything into agreement?
5. **Emergent insight** — Are there ideas that feel like MORE than the sum of obvious inputs? Unexpected reframings or combinations?
6. **Human-likeness** — Does this read like a thoughtful human thinker with genuine convictions, or like a predictable LLM generating a balanced list?

Then provide:
- A brief qualitative comparison (3-5 sentences)
- Your overall preference: X, Y, or tie
- IMPORTANT: Be rigorous and honest. If both are similar in quality, say tie.

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


def judge_raw_blind(seed, output_a, output_b, model=None):
    """Blind evaluation of two raw outputs."""
    coin = random.random() > 0.5
    if coin:
        x, y = output_a, output_b
        xm, ym = "oscillation", "baseline"
    else:
        x, y = output_b, output_a
        xm, ym = "baseline", "oscillation"

    synthesis_x = f"### Synthesis\n{x['synthesis']}" if x.get("synthesis") else ""
    synthesis_y = f"### Synthesis\n{y['synthesis']}" if y.get("synthesis") else ""

    prompt = JUDGE_RAW_PROMPT.format(
        seed=seed,
        insights_x=_fmt_list(x.get("insights", [])),
        questions_x=_fmt_list(x.get("open_knots", x.get("open_questions", []))),
        synthesis_x=synthesis_x,
        insights_y=_fmt_list(y.get("insights", [])),
        questions_y=_fmt_list(y.get("open_knots", y.get("open_questions", []))),
        synthesis_y=synthesis_y,
    )

    # Reset codex singleton for clean thread
    try:
        import codex_client
        if codex_client._server is not None:
            codex_client._server.stop()
            codex_client._server = None
    except ImportError:
        pass

    logger.info(f"[JUDGE-RAW] {seed[:50]}... (X={xm}, Y={ym})")

    raw = chat_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500,
        model=model,
        json_response=True
    )

    result = _safe_parse(raw)
    result["mapping"] = {"X": xm, "Y": ym}
    result["seed"] = seed

    pref = result.get("preference", "tie")
    if pref == "X":
        result["preferred_method"] = xm
    elif pref == "Y":
        result["preferred_method"] = ym
    else:
        result["preferred_method"] = "tie"

    scores = result.get("scores", {})
    result["scores_by_method"] = {
        xm: scores.get("X", {}),
        ym: scores.get("Y", {})
    }

    return result, prompt, xm, ym


def _fmt_list(items):
    if not items:
        return "(none)"
    return "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1))


def _safe_parse(raw):
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
