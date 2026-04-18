# Model Divergence as Signal: Systematic Disagreement Between GPT-4o and Claude Opus as Evaluation Judges

## Abstract

When two frontier LLMs judge the same blind output pairs using the same rubric, they sometimes reach opposite conclusions. This document reports a systematic pattern observed during an A/B evaluation of a cognitive tool across three output modes: GPT-4o and Claude Opus agree when one output is clearly stronger across all quality dimensions, but diverge sharply when **originality and executability trade off against each other**. The disagreement is not noise -- it reveals an under-specification in the rubric that a single-judge system would silently resolve according to that model's implicit preferences.

These findings are relevant to anyone building LLM-as-judge evaluation pipelines.

## Evaluation Setup

Two models (GPT-4o, Claude Opus) judged blind A/B pairs of outputs produced by a baseline system and an experimental "oscillation" system. Outputs were evaluated across three modes -- essay, strategy, and hypotheses -- using identical rubrics per mode. Judges scored on mode-specific criteria and selected a winner.

## Results

### Agreement by Mode

| Mode | Seeds | GPT-4o Judgments | GPT-4o Winner | Opus Judgments | Opus Winner | Agreement |
|------|-------|------------------|---------------|----------------|-------------|-----------|
| Essay | 3 | 6 | Oscillation (6/6) | 3 | Oscillation (3/3) | AGREE |
| Strategy | 1 | 2 | Baseline (2/2) | 1 | Oscillation (1/1) | **DISAGREE** |
| Hypotheses | 2 | 4 | Baseline (4/4) | 2 | Oscillation (2/2) | **DISAGREE** |

The pattern is immediate: **agreement in essay mode, disagreement in strategy and hypotheses**. Essay evaluation depends primarily on a single quality axis (depth and coherence of written argument). Strategy and hypotheses evaluation involves two axes in tension -- intellectual originality vs. practical executability.

### Score Calibration

| Metric | GPT-4o | Claude Opus |
|--------|--------|-------------|
| Mean score range | 8.5 - 9.0 | 5.0 - 8.0 |
| Score variance | Low (compressed) | High (discriminating) |
| Score spread | ~0.5 pts between outputs | ~2-3 pts between outputs |

GPT-4o is a generous grader with a compressed scale. Opus is a harsher grader that uses more of the scale. Both behaviors are stable across all three evaluation modes. Crucially, this calibration difference does not explain the winner disagreement -- a judge can be generous and still rank correctly. The disagreement comes from *which criteria dominate the ranking*.

### Where They Disagree: Criteria-Level Analysis

In strategy and hypotheses modes, Opus scores reveal a clean split in which criteria favor which output:

| Criteria favoring oscillation (Opus deltas +2 to +3) | Criteria favoring baseline (Opus deltas +2 to +3) |
|-------------------------------------------------------|----------------------------------------------------|
| Non-obviousness | Actionability |
| Originality | Falsifiability |
| Connection to tensions | Test protocol quality |
| Research value | Decision-readiness |

The total per-output means are nearly tied: **7.0 vs 7.0** in strategy, **7.4 vs 7.2** in hypotheses. The ranking depends entirely on which criteria a judge implicitly weights more heavily. GPT-4o weights the right column. Opus weights the left.

## The Mechanism

A meta-judge analysis of the disagreement identified the core dynamic:

> "The two judges are answering different implicit questions. Judge 1 [GPT]: *which output is more useful to a decision-maker?* Judge 2 [Opus]: *which output demonstrates stronger strategic thinking?*"

This is not a rubric failure in the usual sense. The rubric included all relevant criteria. But a rubric with multiple criteria **underdetermines the verdict** when criteria point in opposite directions:

> "AI judges are sensitive to implicit weighting in ways that are hard to audit. Same rubric, opposite conclusions -- the rubric underdetermines the verdict."

Opus itself articulated the trade-off clearly:

> "X [oscillation] optimizes for intellectual originality at the cost of executability. Y [baseline] optimizes for decision utility at the cost of originality."

> "If the ask were 'which set do I hand to an exec team on Monday,' the answer flips to Y."

## Implications for LLM-as-Judge Systems

### 1. Single-model judging hides disagreements that matter

A single-judge system would have presented one answer as authoritative. In this evaluation, that answer would have been different depending on which model you happened to pick. The disagreement itself was the most informative signal -- it revealed a genuine quality trade-off that no single ranking can resolve.

### 2. Cross-model judging is a diagnostic tool, not just a robustness check

The standard argument for multi-judge evaluation is noise reduction (average out individual judge variance). This data suggests a stronger claim: **cross-model disagreement localizes the specific quality dimension where a trade-off exists**. The pattern of agreement on essays and disagreement on strategy/hypotheses immediately pointed to the originality-vs-executability axis.

### 3. Score calibration differences are cosmetic; criteria weighting differences are structural

GPT-4o's generous scoring and Opus's harsh scoring are easy to normalize away. The criteria weighting divergence cannot be normalized because it reflects genuinely different evaluation philosophies. Any system that averages cross-model scores without detecting this divergence will produce meaningless middle-ground verdicts.

### 4. Rubrics need explicit weighting or they delegate weighting to the model

An unweighted rubric is not a neutral rubric. It is a rubric whose weighting is determined by whatever implicit preferences the judge model brings. If your evaluation depends on a specific trade-off resolution (e.g., "we care more about actionability than originality"), that preference must be in the rubric, not left to the model.

## Practical Recommendations

1. **Always use at least two structurally different judge models.** "Structurally different" means different training pipelines, not different sizes from the same family.

2. **Treat disagreement as signal, not noise.** When judges disagree, do not break the tie -- investigate which criteria diverge. The disagreement pattern tells you something about your outputs that no single verdict can.

3. **Report per-criteria scores, not just winners.** Aggregate rankings collapse multi-dimensional quality into a single bit. The criteria-level scores are where the information lives.

4. **Make criteria weights explicit in the rubric.** If you do not specify weights, the model will supply its own. Those implicit weights are stable within a model but differ across models, and are difficult to audit.

5. **Calibrate for spread, not just mean.** A judge that gives everything 8.5-9.0 is providing less information than one that uses 5.0-8.0, even if their rankings agree. Consider prompting for wider score distributions.

## The Deeper Question

The observed pattern -- GPT-4o as pragmatist, Opus as intellectual -- is consistent across all evaluation modes in this study. Is this a stable model "personality" that will persist across versions, or an artifact of current training data and RLHF?

This question matters for evaluation infrastructure. If these biases are stable, teams can calibrate for them. If they shift between model versions, any evaluation pipeline that depends on a specific model's implicit weighting is fragile in a way that will not be detected until results silently change.

The honest answer: we do not know yet. The prudent engineering response is to design systems that **detect and surface disagreement** rather than systems that assume any single model's preferences are ground truth.

---

*Data collected April 2026 during A/B evaluation of an oscillation-based cognitive tool. Three evaluation modes, 18 total judgments across two judge models. Full evaluation protocol and raw scores available in the same repository.*
