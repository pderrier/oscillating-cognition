"""
Mode-specific blind judge: evaluates two anonymous grounded outputs using
criteria tailored to each grounding mode (essay, strategy, hypotheses, provocations).

Each mode has its own judge prompt with 5 mode-specific criteria scored 1-10.
"""
import json
import logging
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import chat_completion

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mode-specific judge prompts
# ---------------------------------------------------------------------------

JUDGE_PROMPT_ESSAY = """You are an impartial evaluator of essay quality. You will compare two essay outlines produced from the same topic by two different methods (you don't know which).

## TOPIC
{seed}

## OUTPUT X
{output_x}

## OUTPUT Y
{output_y}

## EVALUATION CRITERIA

Score each output (X and Y) on a 1-10 scale for each criterion:

1. **Narrative voice** — Does the outline have a distinctive voice and point of view, or does it read like a committee wrote it?
2. **Tension as structure** — Are unresolved tensions used as load-bearing rhetorical structure, or are they flattened into neat resolutions?
3. **Originality of framing** — Does the essay reframe the topic in a surprising way, or does it rehash standard positions?
4. **Would you keep reading** — Based on this outline, how compelling would the finished essay be? Would a busy reader keep going past the first section?
5. **Intellectual honesty** — Does the essay confront the hardest parts of the topic, or does it dodge them with hedging and both-sidesism?

Then provide:
- A brief qualitative comparison (3-5 sentences)
- Your overall preference: X, Y, or tie

Output ONLY a JSON object:
{{
  "scores": {{
    "X": {{"narrative_voice": N, "tension_as_structure": N, "originality_of_framing": N, "would_you_keep_reading": N, "intellectual_honesty": N}},
    "Y": {{"narrative_voice": N, "tension_as_structure": N, "originality_of_framing": N, "would_you_keep_reading": N, "intellectual_honesty": N}}
  }},
  "qualitative": "...",
  "preference": "X" | "Y" | "tie"
}}
"""

JUDGE_PROMPT_STRATEGY = """You are an impartial evaluator of strategic thinking quality. You will compare two sets of strategic options produced from the same topic by two different methods (you don't know which).

## TOPIC
{seed}

## OUTPUT X
{output_x}

## OUTPUT Y
{output_y}

## EVALUATION CRITERIA

Score each output (X and Y) on a 1-10 scale for each criterion:

1. **Non-obviousness of options** — Are the strategic options genuinely distinct and surprising, or are they variants of the safe/default choice?
2. **Clarity of tradeoffs** — Does each option clearly articulate what it sacrifices, or does it pretend to have no downsides?
3. **Actionability** — Could a decision-maker act on these options within a real organization, or are they too abstract?
4. **Risk awareness** — Does the output honestly confront the risks and failure modes of each option?
5. **Decision-readiness** — After reading this, is a decision-maker closer to making a real choice, or just more confused?

Then provide:
- A brief qualitative comparison (3-5 sentences)
- Your overall preference: X, Y, or tie

Output ONLY a JSON object:
{{
  "scores": {{
    "X": {{"non_obviousness": N, "clarity_of_tradeoffs": N, "actionability": N, "risk_awareness": N, "decision_readiness": N}},
    "Y": {{"non_obviousness": N, "clarity_of_tradeoffs": N, "actionability": N, "risk_awareness": N, "decision_readiness": N}}
  }},
  "qualitative": "...",
  "preference": "X" | "Y" | "tie"
}}
"""

JUDGE_PROMPT_HYPOTHESES = """You are an impartial evaluator of research hypothesis quality. You will compare two sets of hypotheses produced from the same topic by two different methods (you don't know which).

## TOPIC
{seed}

## OUTPUT X
{output_x}

## OUTPUT Y
{output_y}

## EVALUATION CRITERIA

Score each output (X and Y) on a 1-10 scale for each criterion:

1. **Falsifiability** — Are the hypotheses stated precisely enough that they could be clearly confirmed or disconfirmed?
2. **Originality** — Do the hypotheses probe unexpected angles, or do they test what everyone already assumes?
3. **Test protocol quality** — Are the proposed test methods practical, well-specified, and appropriate for the claim?
4. **Connection to source tensions** — Do the hypotheses clearly emerge from specific tensions or insights, or do they seem invented from thin air?
5. **Research value** — If these hypotheses were tested, would the results advance understanding of the topic in a meaningful way?

Then provide:
- A brief qualitative comparison (3-5 sentences)
- Your overall preference: X, Y, or tie

Output ONLY a JSON object:
{{
  "scores": {{
    "X": {{"falsifiability": N, "originality": N, "test_protocol_quality": N, "connection_to_tensions": N, "research_value": N}},
    "Y": {{"falsifiability": N, "originality": N, "test_protocol_quality": N, "connection_to_tensions": N, "research_value": N}}
  }},
  "qualitative": "...",
  "preference": "X" | "Y" | "tie"
}}
"""

JUDGE_PROMPT_PROVOCATIONS = """You are an impartial evaluator of provocation quality for workshop facilitation. You will compare two sets of provocative questions produced from the same topic by two different methods (you don't know which).

## TOPIC
{seed}

## OUTPUT X
{output_x}

## OUTPUT Y
{output_y}

## EVALUATION CRITERIA

Score each output (X and Y) on a 1-10 scale for each criterion:

1. **Discomfort level** — Would these questions make people in a room genuinely uncomfortable, or could they be brushed off easily?
2. **Precision** — Do the questions target specific assumptions or beliefs, or are they vaguely contrarian?
3. **Resistance to platitudes** — Is it impossible to answer these questions with a corporate cliche or safe generality?
4. **Ability to unstick a group** — Would these questions break a stalled conversation open and force new thinking?
5. **Source insight quality** — Are the provocations rooted in genuine insights, or are they contrarian for shock value?

Then provide:
- A brief qualitative comparison (3-5 sentences)
- Your overall preference: X, Y, or tie

Output ONLY a JSON object:
{{
  "scores": {{
    "X": {{"discomfort_level": N, "precision": N, "resistance_to_platitudes": N, "ability_to_unstick": N, "source_insight_quality": N}},
    "Y": {{"discomfort_level": N, "precision": N, "resistance_to_platitudes": N, "ability_to_unstick": N, "source_insight_quality": N}}
  }},
  "qualitative": "...",
  "preference": "X" | "Y" | "tie"
}}
"""

MODE_JUDGE_PROMPTS = {
    "essay": JUDGE_PROMPT_ESSAY,
    "strategy": JUDGE_PROMPT_STRATEGY,
    "hypotheses": JUDGE_PROMPT_HYPOTHESES,
    "provocations": JUDGE_PROMPT_PROVOCATIONS,
}

MODE_CRITERIA = {
    "essay": [
        "narrative_voice", "tension_as_structure", "originality_of_framing",
        "would_you_keep_reading", "intellectual_honesty"
    ],
    "strategy": [
        "non_obviousness", "clarity_of_tradeoffs", "actionability",
        "risk_awareness", "decision_readiness"
    ],
    "hypotheses": [
        "falsifiability", "originality", "test_protocol_quality",
        "connection_to_tensions", "research_value"
    ],
    "provocations": [
        "discomfort_level", "precision", "resistance_to_platitudes",
        "ability_to_unstick", "source_insight_quality"
    ],
}


def _format_output(output: dict) -> str:
    """Format a grounded output dict as readable text for the judge."""
    return json.dumps(output, indent=2, ensure_ascii=False)


def judge_mode_blind(
    mode: str,
    seed: str,
    output_a: dict,
    output_b: dict,
    model: str = None
) -> dict:
    """
    Blind evaluation of two grounded outputs using mode-specific criteria.
    Randomly assigns X/Y labels to prevent position bias.

    Args:
        mode: Grounding mode (essay, strategy, hypotheses, provocations)
        seed: The topic both outputs explored
        output_a: First output (oscillation grounding result)
        output_b: Second output (baseline grounding result)
        model: Optional model override for judge

    Returns:
        Dict with scores, preference, mapping, and which method was X/Y
    """
    if mode not in MODE_JUDGE_PROMPTS:
        raise ValueError(f"Unknown mode '{mode}'. Must be one of: {list(MODE_JUDGE_PROMPTS.keys())}")

    # Randomize assignment to prevent position bias
    coin = random.random() > 0.5
    if coin:
        x_output, y_output = output_a, output_b
        x_method, y_method = "oscillation", "baseline"
    else:
        x_output, y_output = output_b, output_a
        x_method, y_method = "baseline", "oscillation"

    prompt_template = MODE_JUDGE_PROMPTS[mode]
    prompt = prompt_template.format(
        seed=seed,
        output_x=_format_output(x_output),
        output_y=_format_output(y_output),
    )

    # Reset codex singleton so judge gets a fresh thread
    try:
        import codex_client
        if codex_client._server is not None:
            codex_client._server.stop()
            codex_client._server = None
    except ImportError:
        pass

    logger.info(f"[JUDGE-{mode.upper()}] Evaluating seed={seed[:50]}... (X={x_method}, Y={y_method})")

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
    result["mode"] = mode

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
