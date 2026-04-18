# Evaluation Results: Oscillating Cognition vs. Iterative Baseline

**Date:** 2026-04-18
**Methodology:** [PROTOCOL.md](PROTOCOL.md) | **Model divergence analysis:** [MODEL-DIVERGENCE.md](MODEL-DIVERGENCE.md)

---

## Executive Summary

1. **Generic grounding erases oscillation's advantage** — Track 1 (policy-memo format) produces identical outputs (8.88 vs 8.88)
2. **Oscillation produces superior upstream thinking** — Track 2 (raw) wins 19/20 GPT, 4/5 Opus on novelty, tension, insight
3. **Adapted grounding preserves the advantage for creative modes** — Track 3 essay/provocations: oscillation wins unanimously
4. **Actionable modes split by judge model** — Track 3 strategy/hypotheses: GPT prefers baseline (executability), Opus prefers oscillation (originality)
5. **The disagreement between judges is itself a finding** — it reveals that "quality" contains an inherent tension between originality and actionability

---

## Track 1 — Grounded (Generic Policy Memo)

Both conditions → identical grounding → blind judge. 10 seeds, 30 judgments.

| | GPT (20) | Opus (10) |
|---|:-:|:-:|
| Oscillation wins | 4 (20%) | 1 (10%) |
| Baseline wins | 4 (20%) | 2 (20%) |
| Tie | 12 (60%) | 7 (70%) |
| **Mean score** | **8.88 vs 8.88** | **6.1 vs 6.0** |

**Finding:** The grounding step compresses both conditions into near-identical policy memos.

| Judge | Key quote |
|-------|-----------|
| Opus (biotech) | *"The overlap is so extensive that it suggests a shared underlying template rather than independent reasoning."* |
| Opus (nuclear) | *"Neither output produces a genuinely surprising or counterintuitive idea; both competently execute the same move."* |
| Opus (education) | *"Both read as competent policy-adjacent LLM output rather than like a human thinker with a distinctive angle."* |

---

## Track 2 — Raw (No Grounding)

Compare upstream thinking directly. 10 seeds, 25 judgments.

| | GPT (20) | Opus (5) |
|---|:-:|:-:|
| Oscillation wins | 19 (95%) | 4 (80%) |
| Baseline wins | 1 (5%) | 0 (0%) |
| Tie | 0 (0%) | 1 (20%) |

### Per-criterion scores (GPT, 20 judgments)

| Criterion | Oscillation | Baseline | Delta | Winner |
|-----------|:-----------:|:--------:|:-----:|:------:|
| Novelty | 9.0 | 7.2 | **+1.8** | Oscillation |
| Internal tension | 9.4 | 7.7 | **+1.8** | Oscillation |
| Emergent insight | 9.0 | 7.5 | **+1.5** | Oscillation |
| Human-likeness | 7.9 | 7.2 | **+0.8** | Oscillation |
| Depth | 8.6 | 8.0 | +0.6 | Oscillation (moderate) |
| **Specificity** | **6.5** | **8.2** | **-1.7** | **Baseline** |

### Judge quotes — what oscillation produces differently

| Seed | Judge | Quote |
|------|-------|-------|
| Biotech | Opus | *"Y [osc] finds genuinely surprising angles — unedited inheritance as also coercive, enhancement as narrative assignment preceding the person, disappointment recast as product failure — that reframe the problem rather than merely mapping it."* |
| Remote work | Opus | *"X [base] delivers a competent take that reads like a strong blog post. Y [osc] operates at a genuinely different level of abstraction: rival memory architectures, interpretive hierarchies, presence as trust-conversion ritual."* |
| Education | Opus | *"X [osc] treats the university as a psychosocial institution — moratorium on adulthood, witness to becoming, accent formation, marriage market — rather than defaulting to the standard unbundling/credentialing frame."* |
| Nuclear | Opus | *"Y [osc] surfaces structural observations about how energy choices encode political forms, how risk legibility shapes public response, and how centralization can hide inside ostensibly distributed systems."* |
| Open-source | Opus | *"X [osc] produces more varied conceptual angles — groundwater extraction as metaphor, panic-as-indicator. Y [base] is more actionable. The two are complementary more than competing."* (TIE) |

---

## Track 3 — Grounded (Mode-Specific)

4 modes × 3 seeds = 12 trials. Mode-specific grounding prompts + mode-specific judging criteria.

### Complete results table

| Mode | Seed | GPT-1 | GPT-2 | Opus | Consensus |
|------|------|:-----:|:-----:|:----:|:---------:|
| **Essay** | consciousness | osc | osc | **osc** | **unanime osc** |
| **Essay** | inequality | osc | osc | **osc** | **unanime osc** |
| **Essay** | AI art | osc | osc | **osc** | **unanime osc** |
| **Strategy** | ai-tutor | base | base | **osc** | split |
| **Strategy** | remote | — | — | — | *(invalid — Codex crash)* |
| **Strategy** | opensource | — | — | — | *(invalid — empty osc grounding)* |
| **Hypotheses** | nuclear | base | base | **osc** | split |
| **Hypotheses** | decentral. | base | base | **osc** | split |
| **Hypotheses** | remote-prod | base | base | **osc** | split |
| **Provocations** | cars | base | base | **osc** | split |
| **Provocations** | university | osc | osc | **osc** | **unanime osc** |
| **Provocations** | crispr | osc | osc | **osc** | **unanime osc** |

**Summary: 5 unanimous oscillation, 5 split (GPT→baseline, Opus→oscillation), 0 unanimous baseline.**

---

### Essay Mode — Oscillation dominates (9/9)

Opus average scores:

| Criterion | Oscillation | Baseline | Delta |
|-----------|:-----------:|:--------:|:-----:|
| Narrative voice | 8.3 | 6.0 | **+2.3** |
| Tension as structure | 8.7 | 6.3 | **+2.3** |
| Originality of framing | 8.3 | 5.3 | **+3.0** |
| Would you keep reading | 8.0 | 6.0 | **+2.0** |
| Intellectual honesty | 8.3 | 7.3 | **+1.0** |

| Seed | Judge | Quote |
|------|-------|-------|
| Consciousness | Opus | *"X's [osc] tensions genuinely destabilize the reader's footing; Y's [base] tensions organize the reader's learning. That is the difference between an essay and a textbook chapter."* |
| AI art | Opus | *"X [base] would be publishable in a generalist outlet. Y [osc] would make someone stop scrolling."* |
| Inequality | Opus | *"X [osc] earns its unresolved ending — the impossibility feels discovered through the argument. Y's [base] unresolved ending feels more like a responsible caveat."* |

Generated essays available in [generated_essays.md](generated_essays.md).

---

### Strategy Mode — Split (GPT→baseline, Opus→oscillation)

Opus scores (strat-ai-tutor):

| Criterion | Oscillation | Baseline | Winner |
|-----------|:-----------:|:--------:|:------:|
| Non-obviousness | 8 | 5 | **Oscillation** |
| Clarity of tradeoffs | 9 | 8 | **Oscillation** |
| Actionability | 5 | 8 | **Baseline** |
| Risk awareness | 7 | 6 | ~equal |
| Decision-readiness | 6 | 8 | **Baseline** |

| Judge | Quote |
|-------|-------|
| Opus | *"X [osc] optimizes for intellectual originality at the cost of executability. Y [base] optimizes for decision utility at the cost of originality."* |
| Opus | *"If the ask were 'which set do I hand to an exec team on Monday,' the answer flips to Y [base]."* |
| Opus | *"A's three options all live in the same quadrant (pedagogically contrarian). B's span a risk spectrum. You're choosing between flavors of the same bet rather than genuinely different strategic directions."* |

See [META-strategy-divergence.md](META-strategy-divergence.md) for analysis of why GPT and Opus disagree.

---

### Hypotheses Mode — Split (GPT→baseline, Opus→oscillation)

Opus scores (hyp-nuclear):

| Criterion | Oscillation | Baseline | Winner |
|-----------|:-----------:|:--------:|:------:|
| Falsifiability | 6 | 9 | **Baseline** |
| Originality | 8 | 5 | **Oscillation** |
| Test protocol quality | 6 | 8 | **Baseline** |
| Connection to tensions | 9 | 7 | **Oscillation** |
| Research value | 8 | 7 | **Oscillation** |

| Seed | Judge | Quote |
|------|-------|-------|
| Nuclear | Opus | *"X [base] would produce useful modeling results but is less likely to shift priors. Y's [osc] questions, if answered, would change how we interpret the debate itself."* |
| Decentral. | Opus | *"X [base] would produce competent, publishable results that confirm existing intuitions. Y [osc] would produce results that could actually change how researchers think."* |
| Remote-prod | Opus | *"The field is saturated with X-type [base] studies and starved for Y-type [osc] reframings."* |

---

### Provocations Mode — Mixed (2 unanimous osc, 1 split)

Opus scores (prov-crispr):

| Criterion | Oscillation | Baseline | Winner |
|-----------|:-----------:|:--------:|:------:|
| Discomfort level | 9 | 7 | **Oscillation** |
| Precision | 8 | 8 | equal |
| Resistance to platitudes | 9 | 7 | **Oscillation** |
| Ability to unstick | 9 | 7 | **Oscillation** |
| Source insight quality | 9 | 8 | **Oscillation** |

| Seed | Judge | Quote |
|------|-------|-------|
| Cars | Opus | *"Y [osc] tends to locate the uncomfortable insight one layer deeper."* |
| University | Opus | *"X [osc] asks whether universities are a diagnosable pathology and whether their survival instincts will make them actively harmful. That move is harder to deflect."* |
| CRISPR | Opus | *"X's [osc] questions assume legalization has already happened and ask what follows, which strips away the comfortable abstraction layer. Y [base] leans on familiar policy-debate framing that experienced participants can handle."* |

---

## The GPT vs. Opus Divergence

A systematic pattern across strategy, hypotheses, and one provocation seed: **GPT prefers baseline, Opus prefers oscillation, on the same outputs.**

| What GPT implicitly values | What Opus implicitly values |
|---|---|
| Actionability | Originality |
| Executability | Conceptual reframing |
| Protocol rigor | Connection to tensions |
| Decision-readiness | Research value |
| Portfolio coverage | Intellectual honesty |

Meta-judge analysis (see [META-strategy-divergence.md](META-strategy-divergence.md)):

| Finding | Quote |
|---------|-------|
| Different implicit questions | *"GPT: which output is more useful to a decision-maker? Opus: which output demonstrates stronger strategic thinking? These are not the same question."* |
| Rubric underdetermines verdict | *"Same rubric, opposite conclusions — the rubric underdetermines the verdict."* |
| Disagreement as signal | *"The disagreement itself is the most informative signal in this evaluation. A single-judge system would have presented one answer as authoritative."* |

Full analysis in [MODEL-DIVERGENCE.md](MODEL-DIVERGENCE.md).

---

## The Fundamental Tradeoff

Across all tracks, modes, and judges, oscillation consistently produces:

| More of | Less of |
|---------|---------|
| Novelty (+1.8) | Specificity (-1.7) |
| Internal tension (+1.8) | Actionability (-3.0 in strategy) |
| Emergent insight (+1.5) | Falsifiability (-3.0 in hypotheses) |
| Human-likeness (+0.8) | Decision-readiness (-2.0 in strategy) |
| Originality of framing (+3.0 in essay) | Test protocol rigor (-2.0 in hypotheses) |

This is not a bug — it is the core design tradeoff of the DG prompt, which forbids conclusions and forces metaphors/inversions.

---

## When to Use What

| Use case | Recommended | Why | Evidence |
|----------|:-----------:|-----|----------|
| Essay / thought piece | **Oscillation** | +2-3 on voice, framing, tension | Track 3 essay: 9/9 unanimous |
| Workshop provocations | **Oscillation** | Locates the insight "one layer deeper" | Track 3 prov: 2/3 unanimous, 1/3 split |
| Research ideation (what to study) | **Oscillation** | Reframes problems, surfaces non-obvious questions | Track 3 hyp: Opus unanimous, "starved for Y-type reframings" |
| Research protocol (how to test) | **Baseline** | More falsifiable, rigorous protocols | Track 3 hyp: GPT unanimous, falsifiability +3 |
| Strategic options (explore) | **Oscillation** | More surprising, sharper tradeoffs | Track 3 strat: Opus prefers |
| Strategic options (decide) | **Baseline** | Better portfolio coverage, more executable | Track 3 strat: GPT prefers, "hand to exec Monday" |
| Policy recommendations | **Either** | Generic grounding erases the difference | Track 1: 8.88 vs 8.88 |

### The Decision Rule

```
Need to think differently?     → Oscillation
Need to act on Monday?         → Baseline
Need both?                     → Oscillation upstream + adapted grounding
Don't know yet?                → Oscillation (you can always converge later)
```

---

## Known Biases

| ID | Bias | Severity | Mitigation |
|----|------|----------|------------|
| B1 | Unequal LLM calls (osc ~7, base 3) | Medium | Inherent to architecture |
| B2 | Embeddings disabled (OAuth mode) | Low | Handicaps oscillation, not baseline |
| B3 | Thread contamination (Track 1 only) | Low | Fixed for Tracks 2-3 |
| B4 | LLM-as-judge | Medium | Mitigated by cross-model (GPT + Opus) |
| B5 | Single generator model | Medium | Future: test on Claude, Gemini |
| B6 | Volume asymmetry in Track 2 | Low | Osc ~9+11, base 5+5 |
| B7 | Codex truncation (baseline pass 1) | Low | Pipeline continues via fallback |
| B8 | 2 invalid strategy seeds | Medium | Codex crash, not method failure |

---

## Conclusions

**Established:**
1. Oscillation produces genuinely different upstream thinking — more novel, more tension-preserving, more human-like
2. Generic grounding destroys this advantage by compressing to policy-memo format
3. Mode-adapted grounding preserves the advantage for creative outputs (essay, provocations)
4. For actionable outputs (strategy, hypotheses), the value depends on phase: explore → oscillation, execute → baseline
5. Cross-model judging reveals tensions in what "quality" means that single-model judging hides
6. The fundamental tradeoff is originality vs. specificity — and it is irreducible by design

**Open:**
1. Would a grounding prompt that preserves tensions AND adds specificity close the gap?
2. Does the pattern hold with embeddings enabled (full novelty filtering)?
3. Do human judges agree with GPT, Opus, or neither?
4. Does the pattern generalize across generator models?
5. Can strategy mode be split into "explore" and "decide" sub-modes?
6. What happens with more than 3 cycles?

---

## Data Files

| File | Contents |
|------|----------|
| `results_20260418_091937.json` | Track 1 full data (10 seeds, 30 judgments) |
| `results_20260418_091937_report.md` | Track 1 GPT judge report |
| `results_20260418_091937_stats.json` | Track 1 aggregate statistics |
| `raw_results_20260418_095054.json` | Track 2 raw generation data (10 seeds) |
| `raw_gpt_judgments.json` | Track 2 GPT judge results (20 judgments) |
| `mode_results_20260418_121602.json` | Track 3 mode data (12 trials) |
| `generated_essays.md` | Track 3 essay outputs (readable) |
| `META-strategy-divergence.md` | Meta-judge analysis of GPT/Opus split |
| `MODEL-DIVERGENCE.md` | Standalone model divergence analysis |
| `PROTOCOL.md` | Full evaluation methodology |
| `seeds.json` | Track 1-2 seeds (10) |
| `seeds_by_mode.json` | Track 3 seeds (12, by mode) |
