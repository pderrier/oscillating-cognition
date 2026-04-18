"""
Baseline condition: 3-pass iterative refinement using standard prompting,
followed by the same grounding prompt used by oscillation.

Equal effort to oscillation: 3 generation passes + 1 grounding pass.
Equal output format: actions, experiments, questions, synthesis.
"""
import json
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import chat_completion

logger = logging.getLogger(__name__)

PASS1_PROMPT = """You are a creative thinker exploring a topic in depth.

## TOPIC
{seed}

Generate 5 distinct ideas, perspectives, or arguments about this topic. Be creative, specific, and non-obvious. Mix concrete proposals with speculative thinking.

Output a JSON object:
{{
  "ideas": [
    {{"id": 1, "content": "...", "type": "proposal|hypothesis|critique|reframing"}},
    ...
  ]
}}
"""

PASS2_PROMPT = """You are a critical analyst reviewing ideas generated about a topic.

## TOPIC
{seed}

## IDEAS FROM PREVIOUS PASS
{previous_ideas}

Your job:
1. Critique each idea — what's strong, what's weak, what's missing?
2. Compress the best insights into sharper formulations
3. Identify 1-2 new ideas that emerge from the critique
4. Note any unresolved tensions or contradictions you find interesting

Output a JSON object:
{{
  "refined_ideas": [
    {{"id": 1, "content": "...", "rationale": "why this survived critique"}},
    ...
  ],
  "new_ideas": [
    {{"id": "new_1", "content": "...", "emerged_from": "which original ideas sparked this"}}
  ],
  "tensions": ["..."]
}}
"""

PASS3_PROMPT = """You are synthesizing a multi-pass exploration of a topic into final output.

## TOPIC
{seed}

## REFINED IDEAS (from critique pass)
{refined_ideas}

## TENSIONS IDENTIFIED
{tensions}

Produce a final synthesis:
1. Your strongest 5 ideas/positions on this topic
2. Any unresolved questions worth preserving
3. A 2-3 sentence synthesis connecting your best ideas

Output a JSON object:
{{
  "final_ideas": [
    {{"content": "...", "confidence": "high|medium|low"}},
    ...
  ],
  "open_questions": ["..."],
  "synthesis": "..."
}}
"""

# Grounding prompt — same structure as oscillation's grounding phase
GROUNDING_PROMPT = """You are transforming abstract insights into actionable proposals within the context of the original topic.

## INPUT

You will receive:
- The original TOPIC that started the exploration
- INSIGHTS: ideas and compressed models from the exploration
- OPEN QUESTIONS: unresolved tensions and questions

## OUTPUT FORMAT

Output a JSON object with these fields:
- "actions": array of things to do or try (max 5)
- "experiments": array of hypotheses to test or validate (max 3)
- "questions": array of questions to investigate or ask (max 5)
- "synthesis": a 2-3 sentence summary connecting insights to the topic

Each action/experiment/question must have:
- "description": what to do
- "rationale": which insight(s) it builds on
- "effort": "low", "medium", or "high"

## RULES

1. Every proposal MUST connect back to the original topic
2. Mix of concrete and abstract recommendations is fine
3. Experiments should have some way to evaluate success/failure
4. Questions can be open-ended or specific
5. NO meta-commentary about the system or generation process
6. Connect abstract insights to the topic's domain

Output only the JSON object, no other text.
"""


def run_baseline(seed: str, temperature: float = 0.7, model: str = None, skip_grounding: bool = False) -> dict:
    """
    Run 3-pass iterative refinement + grounding on a seed topic.

    Returns:
        Dict with all passes and grounded final output.
    """
    # Reset codex singleton so each trial gets a fresh thread
    try:
        import codex_client
        if codex_client._server is not None:
            codex_client._server.stop()
            codex_client._server = None
    except ImportError:
        pass

    result = {"seed": seed, "passes": []}

    # Pass 1: Generate
    logger.info(f"[BASELINE] Pass 1: Generate — seed={seed[:50]}...")
    pass1_raw = chat_completion(
        messages=[{"role": "user", "content": PASS1_PROMPT.format(seed=seed)}],
        temperature=temperature,
        max_tokens=2000,
        model=model,
        json_response=True
    )
    pass1 = _safe_parse(pass1_raw)
    result["passes"].append({"pass": 1, "type": "generate", "output": pass1})

    # Pass 2: Critique and refine
    logger.info("[BASELINE] Pass 2: Critique and refine...")
    ideas_text = json.dumps(pass1.get("ideas", []), indent=2)
    pass2_raw = chat_completion(
        messages=[{"role": "user", "content": PASS2_PROMPT.format(
            seed=seed,
            previous_ideas=ideas_text
        )}],
        temperature=0.5,
        max_tokens=2000,
        model=model,
        json_response=True
    )
    pass2 = _safe_parse(pass2_raw)
    result["passes"].append({"pass": 2, "type": "critique", "output": pass2})

    # Pass 3: Synthesize
    logger.info("[BASELINE] Pass 3: Synthesize...")
    refined_text = json.dumps(
        pass2.get("refined_ideas", []) + pass2.get("new_ideas", []),
        indent=2
    )
    tensions_text = json.dumps(pass2.get("tensions", []), indent=2)
    pass3_raw = chat_completion(
        messages=[{"role": "user", "content": PASS3_PROMPT.format(
            seed=seed,
            refined_ideas=refined_text,
            tensions=tensions_text
        )}],
        temperature=0.5,
        max_tokens=2000,
        model=model,
        json_response=True
    )
    pass3 = _safe_parse(pass3_raw)
    result["passes"].append({"pass": 3, "type": "synthesize", "output": pass3})

    # Pass 4: Grounding (optional — same format as oscillation's grounding phase)
    if not skip_grounding:
        logger.info("[BASELINE] Pass 4: Grounding...")
        insights = pass3.get("final_ideas", [])
        questions = pass3.get("open_questions", [])

        grounding_user = _build_grounding_input(seed, insights, questions)
        grounding_raw = chat_completion(
            messages=[
                {"role": "system", "content": GROUNDING_PROMPT},
                {"role": "user", "content": grounding_user}
            ],
            temperature=0.5,
            max_tokens=2000,
            model=model,
            json_response=True
        )
        grounding = _safe_parse(grounding_raw)
        grounding.setdefault("actions", [])
        grounding.setdefault("experiments", [])
        grounding.setdefault("questions", [])
        grounding.setdefault("synthesis", "")
        result["passes"].append({"pass": 4, "type": "grounding", "output": grounding})
        result["final"] = grounding
    else:
        # Raw output = pass 3 synthesis
        result["final"] = {
            "ideas": [i.get("content", str(i)) for i in pass3.get("final_ideas", [])],
            "open_questions": pass3.get("open_questions", []),
            "synthesis": pass3.get("synthesis", "")
        }

    return result


def _build_grounding_input(seed: str, insights: list, questions: list) -> str:
    parts = [f"## ORIGINAL TOPIC\n{seed}\n"]

    if insights:
        parts.append("## INSIGHTS")
        for i, item in enumerate(insights, 1):
            content = item.get("content", str(item)) if isinstance(item, dict) else str(item)
            parts.append(f"{i}. {content}")
    else:
        parts.append("## INSIGHTS\n(none)")

    parts.append("")

    if questions:
        parts.append("## OPEN QUESTIONS (unresolved tensions)")
        for i, q in enumerate(questions, 1):
            parts.append(f"{i}. {q}")
    else:
        parts.append("## OPEN QUESTIONS\n(none)")

    parts.append("\nGround these insights into actionable proposals for the topic.")
    return "\n".join(parts)


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
        logger.warning(f"Failed to parse response: {raw[:200]}...")
        return {"raw": raw}
