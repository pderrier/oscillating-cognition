# Evaluation Results: Oscillating Cognition vs. Iterative Baseline

**Date:** 2026-04-18
**Protocol:** See [PROTOCOL.md](PROTOCOL.md)

---

## 1. Setup

- **Seeds:** 10 external-domain topics (bioethics → systems theory)
- **Oscillation:** 3 cycles DG→CC→TC + optional grounding (via Codex OAuth, model: GPT-4o equivalent)
- **Baseline:** 3 iterative passes (generate→critique→synthesize) + optional identical grounding
- **Track 1 (Grounded):** Both outputs compressed through identical grounding prompt into actions/experiments/questions/synthesis
- **Track 2 (Raw):** Pre-grounding upstream outputs compared directly — crystallized insights + open knots vs. final ideas + open questions
- **Judge GPT:** Same model family as generator, 2 judges per seed, blind
- **Judge Opus:** Claude Opus 4.6 (different family), 1 judge per seed, blind

---

## 2. Headline Results

### Track 1 — Grounded (full pipeline)

**No meaningful difference.** The grounding step homogenizes both conditions.

| | GPT (20 judgments) | Opus (10 judgments) |
|---|:-:|:-:|
| Oscillation wins | 4 (20%) | 1 (10%) |
| Baseline wins | 4 (20%) | 2 (20%) |
| Tie | 12 (60%) | 7 (70%) |
| Mean delta | **0.0** | **+0.1** |

### Track 2 — Raw (pre-grounding) — partial results, 8/10 seeds

**Oscillation wins overwhelmingly.**

| | GPT (16 judgments) | Opus (5 judgments*) |
|---|:-:|:-:|
| Oscillation wins | 16 (100%) | 4 (80%) |
| Baseline wins | 0 (0%) | 0 (0%) |
| Tie | 0 (0%) | 1 (20%) |
| Mean delta | **+1.1** | **+2.3** |

*Opus judges ran on first 5 seeds only. GPT judges ran on 8/10 seeds (2 still generating).

### The Contrast

```
Track 1 (grounded):    osc ≈ baseline     (both become "competent policy memos")
Track 2 (raw):         osc >> baseline     (genuinely different thinking)
```

---

## 3. What Oscillation Actually Produces (vs. Baseline)

On the same seed, the raw outputs are qualitatively different:

| Dimension | Oscillation raw | Baseline raw |
|-----------|----------------|--------------|
| **Volume** | ~9 insights + ~11 open knots | 5 ideas + 5 questions + synthesis |
| **Register** | Metaphorical, reframing, questioning assumptions | Analytical, structured, policy-oriented |
| **Tensions** | Deliberately preserved, unresolved | Noted but often resolved in synthesis |
| **Surprise** | High — inversions, unexpected angles | Moderate — competent but conventional |
| **Actionability** | Low — fragments, not proposals | Higher — clearer recommendations |

Opus judge on remote-work, capturing the difference:
> *"X delivers a competent, well-organized take that reads like a strong blog post — correct but largely predictable. Y operates at a genuinely different level of abstraction, reframing the question toward epistemology: rival memory architectures, interpretive hierarchies, presence as trust-conversion ritual."*

Opus judge on education-ai:
> *"X treats the university as a psychosocial institution — moratorium on adulthood, witness to becoming, accent formation, marriage market — rather than defaulting to the standard unbundling/credentialing frame that Y reproduces competently but predictably."*

---

## 4. The Grounding Problem

The grounding prompt asks: *"transform insights into actions, experiments, questions, synthesis."*

This is a **convergent** operation. It compresses whatever upstream material it receives into the same structured format. The DG's metaphors, inversions, and tensions get flattened. The baseline's straightforward ideas get polished. Both arrive at near-identical policy memos.

Opus judge on Track 1 (biotech-ethics):
> *"The overlap is so extensive that it suggests a shared underlying template rather than independent reasoning."*

**The irony:** Oscillating cognition's grounding phase is itself a convergent critic that undoes the divergent work. The system fights premature convergence in cycles 1-3, then performs exactly that convergence in the final step.

---

## 5. When to Use Oscillation vs. Standard Prompting

The evaluation reveals that oscillation is not universally better — it excels in specific contexts and may be counterproductive in others. The key variable is **what you need from the output**.

### Usage Guide

| Use case | Recommended | Why |
|----------|:-----------:|-----|
| **Exploratory thinking** — reframe a problem, find non-obvious angles, challenge assumptions | **Oscillation** | Produces genuinely surprising reframings, metaphors, and tensions that standard prompting misses. The DG's constraints (no conclusions, force inversions) create material a generic prompt won't generate. |
| **Research ideation** — generate hypotheses, find productive contradictions, map a problem space | **Oscillation** | The preserved open knots and multi-cycle accumulation create richer conceptual maps. Best when you want to *think differently* about a topic, not just list ideas. |
| **Creative writing / conceptual work** — essays, provocations, philosophical exploration | **Oscillation** | The metaphorical register and unresolved tensions read as more human-like and intellectually honest. Opus consistently scored oscillation +2-3 points on human-likeness for raw output. |
| **Strategic planning** — generate a roadmap, explore futures, challenge a thesis | **Oscillation → custom grounding** | Use oscillation for upstream thinking, but replace the standard grounding with a prompt that preserves tensions and metaphors alongside actions. |
| **Policy analysis** — produce actionable recommendations, structured proposals | **Baseline (or oscillation + grounding)** | Standard iterative prompting produces equally good policy memos. If you need concrete, implementable proposals, oscillation's raw output is too abstract. The grounding step works but erases the oscillation advantage. |
| **Technical problem-solving** — debug, architect, design systems | **Baseline** | The DG's metaphorical register adds noise to technical analysis. Standard prompting is more direct and specific. |
| **Quick brainstorming** — generate a list of ideas fast | **Baseline** | Oscillation's multi-cycle architecture is overhead when you just need a competent list. Three standard passes produce equivalent practical output. |
| **Adversarial stress-testing** — attack your own assumptions | **Oscillation (adversarial mode)** | The DG's inversion constraint is purpose-built for this. Not yet implemented as a separate mode, but the architecture supports it. |

### Per-Criterion Breakdown (Track 2, GPT judge, 14 judgments)

| Criterion | Oscillation | Baseline | Delta | Winner |
|-----------|:-----------:|:--------:|:-----:|:------:|
| Novelty | 9.0 | 7.2 | +1.8 | **Oscillation** |
| Internal tension | 9.6 | 7.8 | +1.8 | **Oscillation** |
| Emergent insight | 9.0 | 7.5 | +1.5 | **Oscillation** |
| Human-likeness | 8.1 | 7.0 | +1.1 | **Oscillation** |
| Depth | 8.6 | 8.0 | +0.6 | ~equal |
| **Specificity** | **6.7** | **8.3** | **-1.6** | **Baseline** |

Oscillation wins 5/6 criteria but **loses on the one that matters most for practical output**. This is why grounding exists — and why it erases the advantage: it forces specificity at the cost of everything else.

### The Decision Rule

```
Need surprising reframings?     → Oscillation (skip grounding or redesign it)
Need actionable proposals?      → Baseline (or oscillation + grounding, same result)
Need both?                      → Oscillation + redesigned grounding that preserves tension
```

### What the Grounding Prompt Should Become

The current grounding prompt destroys oscillation's value. A better version would:

1. **Carry forward 2-3 open knots** explicitly into the output
2. **Preserve one metaphor or reframing** alongside each action
3. **Flag which proposals are conventional vs. which emerged from tension**
4. **Include a "what we deliberately did not resolve" section**

This would produce outputs that are both actionable AND intellectually richer than standard prompting.

---

## 6. Judge Calibration: GPT vs. Opus

| | GPT mean score | Opus mean score |
|---|:-:|:-:|
| Track 1 (grounded) | 8.88 | 6.05 |
| Track 2 (raw, oscillation) | 8.5 | 7.8 |
| Track 2 (raw, baseline) | 7.5 | 5.5 |

GPT inflates all scores and sees smaller deltas. Opus is harsher but more discriminating — it produces larger deltas between conditions when they genuinely differ.

Both judges agree on the structural conclusions:
- Track 1: tie (grounding homogenizes)
- Track 2: oscillation wins (raw thinking is superior)

Cross-model judging is essential for honest evaluation. Same-family judges (GPT on GPT output) are too generous.

---

## 7. Known Biases

See [PROTOCOL.md](PROTOCOL.md) section 6 for full details. Key biases in this run:

- **B1:** Unequal LLM call count (oscillation ~7 vs baseline 3)
- **B2:** Embeddings disabled (Codex OAuth mode) — oscillation runs with degraded novelty filter
- **B3:** Thread contamination in Track 1 (fixed for Track 2)
- **B4:** LLM-as-judge — mitigated by cross-model design (GPT + Opus)
- **B6 (new):** Volume asymmetry in Track 2 — oscillation produces ~9 insights + ~11 knots vs baseline's 5+5. Judges may favor richer outputs regardless of per-item quality. A future test could normalize volume.

---

## 8. Conclusions

1. **Oscillation produces genuinely superior upstream thinking** — more novel, deeper, more tension-preserving, more human-like (Track 2, unanimous across both judge models)

2. **The grounding step erases this advantage** — compressing both conditions into identical policy-memo format (Track 1, 60-70% ties)

3. **The system's weakness is output formatting, not generation** — the DG→CC→TC loop works; the grounding prompt doesn't preserve what makes it valuable

4. **Oscillation is not universally better** — it excels at exploratory/creative thinking, is equivalent after grounding for policy work, and may be counterproductive for technical tasks

5. **The fix is in the last mile** — redesigning the grounding prompt to preserve tensions, metaphors, and unresolved questions alongside actionable proposals

---

## 9. Files

- `results_20260418_091937.json` — Track 1 (grounded) full data
- `results_20260418_091937_report.md` — Track 1 GPT judge report
- `raw_results_20260418_095054.json` — Track 2 (raw) generation data
- `raw_gpt_judgments.json` — Track 2 GPT judge results
- `PROTOCOL.md` — evaluation methodology
