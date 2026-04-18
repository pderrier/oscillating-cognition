# Evaluation Protocol: Oscillating Cognition vs. Iterative Baseline

**What we test, why it matters, and how the protocol evolved across three tracks.**

---

## 1. The Claim

Oscillating Cognition's thesis: LLMs converge too fast. By structuring generation into explicit divergent/convergent phases with persistent memory, adaptive temperature control, and mandatory tension preservation, the system produces richer, more human-like thinking than standard iterative prompting.

This evaluation tests that claim on external domains with controlled methodology across three tracks, each designed in response to findings from the previous one.

---

## 2. Evolution of the Protocol

### Track 1 (Grounded -- generic) --> finding: grounding homogenizes

Both conditions produced raw outputs, then passed through an identical grounding prompt that compressed everything into actions/experiments/questions/synthesis. Result: **tie** (8.88 vs 8.88 GPT mean, 60% ties GPT, 70% ties Opus). The grounding step flattened oscillation's divergent texture and baseline's straightforward analysis into near-identical policy memos.

This raised the question: is there no upstream difference, or does grounding erase one?

### Track 2 (Raw -- no grounding) --> finding: oscillation wins upstream

We stripped the grounding step entirely and compared raw outputs: crystallized insights + open knots (oscillation) vs. synthesized ideas + open questions (baseline). Result: **oscillation wins 19/20 GPT, 4/5 Opus**. Per-criterion (GPT, 20 judgments): novelty 9.0 vs 7.2, depth 8.6 vs 8.0, specificity 6.5 vs 8.2, internal tension 9.4 vs 7.7, emergent insight 9.0 vs 7.5, human-likeness 7.9 vs 7.2.

Oscillation wins 5/6 criteria but loses on specificity (-1.7). The upstream thinking is genuinely superior; the grounding step destroys the advantage.

This raised the question: is the problem with grounding *per se*, or with *generic* grounding?

### Track 3 (Grounded -- mode-specific) --> tests: adapted grounding

If we replace the one-size-fits-all grounding prompt with mode-specific grounding tailored to actual deliverables, does oscillation's upstream advantage survive? Track 3 tests four distinct output modes, each with its own grounding prompt and judging criteria.

---

## 3. What We Actually Compare

Both conditions explore the same seed topic. The generation pipelines are identical across all three tracks.

### Condition A -- Oscillation (3 cycles)

Each cycle makes 2 LLM calls (~7 total, +1 grounding in Tracks 1 and 3):

```
+-  Cycle 1 --------------------------------------------------+
|  DG (temp 0.95) -> 5 artifacts                              |
|    Specialized prompt: no conclusions allowed,               |
|    must produce metaphors/inversions/hypotheses              |
|  CC (temp 0.4) -> select max 3, compress, add knots         |
|    Must preserve >=1 unresolved tension                      |
|  TC -> compute metrics, adjust temperature                   |
|  Memory -> crystallized.json, open_knots.json                |
+-  -----------------------------------------------------------+
        | memory persists
+-  Cycle 2 --------------------------------------------------+
|  DG sees accumulated context + knots + probes                |
|  CC sees richer material, builds on prior models             |
|  TC detects stagnation or excessive convergence              |
+-  -----------------------------------------------------------+
        | memory persists
+-  Cycle 3 --------------------------------------------------+
|  Same loop. TC may force divergence if too rigid.            |
+-  -----------------------------------------------------------+
        |
  Raw output: crystallized insights + open knots
        | (Tracks 1 and 3 only)
+-  Grounding ------------------------------------------------+
|  Track 1: generic prompt (actions/experiments/questions)     |
|  Track 3: mode-specific prompt (see section 4)              |
+-  -----------------------------------------------------------+
```

### Condition B -- Standard iterative refinement (3 passes)

3-4 LLM calls total:

```
+-  Pass 1: Generate (temp 0.7) ------------------------------+
|  Generic prompt: "generate 5 ideas, be creative"            |
+-  -----------------------------------------------------------+
        | output forwarded
+-  Pass 2: Critique (temp 0.5) ------------------------------+
|  Generic prompt: "critique, refine, find tensions"          |
+-  -----------------------------------------------------------+
        | output forwarded
+-  Pass 3: Synthesize (temp 0.5) ----------------------------+
|  Generic prompt: "best ideas + open questions"              |
+-  -----------------------------------------------------------+
        |
  Raw output: final ideas + open questions + synthesis
        | (Tracks 1 and 3 only)
+-  Grounding ------------------------------------------------+
|  Track 1: same generic prompt as oscillation                |
|  Track 3: same mode-specific prompt as oscillation          |
+-  -----------------------------------------------------------+
```

### The Real Differences

| Dimension | Oscillation | Baseline |
|-----------|-------------|----------|
| **Generation prompts** | Specialized: forbids conclusions, forces fragments, metaphors, inversions | Generic: "be creative and specific" |
| **Critique prompts** | Specialized: must preserve tensions, max 3 selections, compress to models | Generic: "critique and refine" |
| **Temperature strategy** | Deliberate oscillation: 0.95 (chaos) -> 0.4 (structure), adaptive via TC | Flat: 0.7 -> 0.5, no adaptation |
| **Memory across passes** | Persistent: each cycle sees all prior insights + knots | Stateless: each pass sees only the previous pass output |
| **Feedback loop** | TC monitors compression ratio, novelty, knot count; triggers forced divergence | None |
| **LLM calls** | ~7 (+1 grounding in Tracks 1/3) | 3 (+1 grounding in Tracks 1/3) |

### Known Confound

Oscillation makes ~7 LLM calls vs. baseline's 3. We are not controlling for compute budget. This is inherent to the system design -- but a future compute-controlled test (equal call count) would separate the two effects.

---

## 4. Track 3: Mode-Specific Grounded Evaluation

### Design

- **4 modes** x **3 seeds** = **12 trials**
- Each trial generates both conditions, applies mode-specific grounding, then judges with mode-specific criteria
- Same blind randomized X/Y design as Tracks 1 and 2
- Cross-model judges: GPT (2 per trial) + Opus (1 per trial) = 36 judgments total

### Modes and Seeds

| Mode | Seed 1 | Seed 2 | Seed 3 |
|------|--------|--------|--------|
| **Essay** | CRISPR gene editing should be available for non-medical human enhancement | We will never be able to determine whether a machine is conscious | Life extension technology will create the most extreme inequality in human history |
| **Strategy** | Remote-first companies will outcompete office-first companies within 10 years | The open-source model is fundamentally broken and needs a new economic foundation | Cars should be banned from city centers worldwide |
| **Hypotheses** | Nuclear energy is the only realistic path to decarbonization at scale | Decentralized systems always re-centralize and this is inevitable | AI tutors will make traditional universities obsolete for most students |
| **Provocations** | AI-generated art is not art and should not be treated as such | CRISPR gene editing should be available for non-medical human enhancement | Decentralized systems always re-centralize and this is inevitable |

Seeds are drawn from the same 10 used in Tracks 1 and 2. Two seeds appear in two modes to test whether the same upstream thinking grounds differently across formats.

### Mode-Specific Grounding Prompts

Each mode's grounding prompt receives the same upstream material (crystallized insights + open knots for oscillation, synthesized ideas + open questions for baseline) and transforms it into a mode-appropriate deliverable.

**Essay mode.** Produce a 600-800 word argumentative essay. Must have a thesis, must complicate that thesis with at least one genuine counterargument, must end with an unresolved question rather than a tidy conclusion. The grounding prompt explicitly instructs: "Preserve metaphors and reframings from the source material. Do not flatten tensions into false resolution."

**Strategy mode.** Produce a strategic brief: 3 recommended actions with rationale, 2 experiments to run before committing, 1 explicit bet-against (a plausible strategy you reject and why). The grounding prompt instructs: "Flag which recommendations are conventional wisdom vs. which emerged from non-obvious analysis. Include one unresolved strategic tension."

**Hypotheses mode.** Produce 5 testable hypotheses ranked by surprise value. Each hypothesis must include: the claim, why it is non-obvious, a falsification method, and confidence level. The grounding prompt instructs: "Favor hypotheses that challenge dominant assumptions. Include one hypothesis pair where the two hypotheses are in productive tension with each other."

**Provocations mode.** Produce 3 provocative reframings of the topic designed to shift how a reader thinks about it. Each must be a single paragraph that destabilizes a default assumption. No recommendations, no solutions. The grounding prompt instructs: "Maximize surprise and discomfort. Preserve ambiguity. Do not resolve the provocation into an actionable takeaway."

### Mode-Specific Judging Criteria (scored 1-10)

Each mode has 5 criteria. No criterion references oscillation-specific vocabulary.

**Essay**

| Criterion | What it measures |
|-----------|-----------------|
| Thesis strength | Is the central argument clear, specific, and worth arguing? |
| Intellectual honesty | Does it genuinely engage counterarguments, or strawman them? |
| Texture | Metaphors, examples, and framings that make it memorable vs. generic |
| Unresolved tension | Does the essay end with productive ambiguity, or collapse into false resolution? |
| Voice | Reads like a specific thinker wrote it, or like boilerplate? |

**Strategy**

| Criterion | What it measures |
|-----------|-----------------|
| Non-obviousness | Are the recommendations surprising given the domain, or standard playbook? |
| Falsifiability | Are the experiments concrete enough to actually run and learn from? |
| Risk awareness | Does the bet-against show genuine strategic thinking, or a token contrarian move? |
| Internal coherence | Do the pieces fit together as a strategy, or is it a disconnected list? |
| Preserved tension | Does it acknowledge what remains genuinely uncertain? |

**Hypotheses**

| Criterion | What it measures |
|-----------|-----------------|
| Surprise value | Would a domain expert find these hypotheses non-obvious? |
| Testability | Could you actually design an experiment to falsify each one? |
| Range | Do the hypotheses span different levels of analysis, or cluster in one frame? |
| Productive conflict | Is there genuine tension between at least two hypotheses? |
| Depth | Do hypotheses engage root mechanisms, or stay at surface-level correlations? |

**Provocations**

| Criterion | What it measures |
|-----------|-----------------|
| Destabilization | Does it genuinely shift how you think about the topic? |
| Originality | Is this a reframing you haven't encountered before? |
| Precision | Is the provocation sharp and specific, or vaguely contrarian? |
| Discomfort | Does it challenge something the reader likely believes? |
| Resistance to resolution | Does it stay productively unresolved, or collapse into a hidden argument? |

---

## 5. What Track 3 Results Would Mean

### If oscillation wins on some modes but not others

The value of oscillation is **use-case dependent**. The most likely pattern: oscillation wins on provocations and essays (where tension and metaphor are the deliverable) but ties on strategy and hypotheses (where specificity matters more). This would define the system's niche precisely: use oscillation when the goal is reframing, not when the goal is planning.

### If oscillation wins across all modes

The upstream thinking advantage **survives grounding when grounding is well-designed**. The Track 1 tie was an artifact of generic grounding, not a fundamental limit. This would validate the system end-to-end and indicate that the fix is in prompt design, not architecture.

### If tie again across all modes

The grounding step **inherently compresses regardless of format**. Any structured output requirement -- even one designed to preserve tension -- forces enough convergence to erase upstream differences. This would suggest oscillation's value is limited to raw exploratory output and cannot be transmitted through a final formatting step.

### What to watch per-mode

- **Provocations** is oscillation's best case -- the DG's inversion constraints and knot preservation map directly to what provocations demand. If oscillation doesn't win here, the architecture has a deeper problem.
- **Strategy** is oscillation's hardest case -- it lost on specificity in Track 2, and strategy requires specificity. A win here would be the strongest evidence.
- **Essay** tests whether oscillation's metaphorical register survives compression into prose. Track 2 showed oscillation produces richer metaphors; the question is whether a grounding prompt can carry them into finished writing.
- **Hypotheses** tests range and surprise. Oscillation should produce more surprising hypotheses (novelty +1.8 in Track 2), but the question is whether they remain testable.

### Cross-mode criterion analysis

The five mode-specific criteria are different per mode, but "preserved tension" or its equivalent (unresolved tension, productive conflict, resistance to resolution) appears in all four. If oscillation wins on this criterion across all modes, the tension preservation architecture is the system's core differentiator regardless of output format.

---

## 6. Seeds

### Tracks 1 and 2 (10 seeds)

| Domain | Seed |
|--------|------|
| Bioethics | CRISPR gene editing should be available for non-medical human enhancement |
| Business strategy | Remote-first companies will outcompete office-first companies within 10 years |
| Education | AI tutors will make traditional universities obsolete for most students |
| Energy policy | Nuclear energy is the only realistic path to decarbonization at scale |
| Software economics | The open-source model is fundamentally broken and needs a new economic foundation |
| Philosophy of mind | We will never be able to determine whether a machine is conscious |
| Urban planning | Cars should be banned from city centers worldwide |
| Social futures | Life extension technology will create the most extreme inequality in human history |
| Aesthetics | AI-generated art is not art and should not be treated as such |
| Systems theory | Decentralized systems always re-centralize and this is inevitable |

### Track 3 (12 trials)

See mode/seed matrix in section 4. Seeds drawn from the same pool. Two seeds appear in two modes to enable cross-mode comparison on identical upstream material.

---

## 7. Judging Design

### Blind Randomized X/Y

Each trial is presented as "Output X" and "Output Y" with randomized assignment. Neither judge knows which method produced which output. Position assignment is randomized independently per judgment.

### Cross-Model Judges

| Judge | Model | Relation to generator | Per trial |
|-------|-------|----------------------|-----------|
| **Judge GPT** | GPT-4o (via Codex OAuth) | Same family as generator | 2 |
| **Judge Opus** | Claude Opus 4.6 | Different family | 1 |

### Criteria by Track

| Track | Criteria | Count |
|-------|----------|-------|
| Track 1 (grounded, generic) | Novelty, depth, specificity, internal tension, emergent insight, human-likeness | 6 |
| Track 2 (raw) | Same as Track 1 | 6 |
| Track 3 (grounded, mode-specific) | Mode-specific (see section 4) | 5 per mode |

### Statistical Design

| Track | Trials | Judges per trial | Total judgments |
|-------|--------|-------------------|-----------------|
| Track 1 | 10 seeds | 2 GPT + 1 Opus | 30 |
| Track 2 | 10 seeds | 2 GPT + 1 Opus | 30 |
| Track 3 | 12 trials (4 modes x 3 seeds) | 2 GPT + 1 Opus | 36 |

All tracks are resumable: partial runs can be continued from saved JSON.

---

## 8. Known Biases

### B1: Unequal LLM call count
Oscillation makes ~7 calls; baseline makes 3. We are not isolating architecture from raw iteration count. This is inherent to the system design -- but a future compute-controlled test (equal call count) would separate the two effects.

### B2: Embedding novelty disabled (OAuth mode)
When running via Codex OAuth (no `OPENAI_API_KEY`), the embedding API is unavailable. Oscillation falls back to lexical diversity for novelty scoring instead of semantic similarity. This is a handicap for oscillation -- it runs with a weaker novelty filter than its intended design. Baseline is unaffected.

### B3: Thread contamination (Track 1 Run 1 only -- fixed)
The first evaluation run reused a single Codex app-server thread across all seeds. Fixed in subsequent runs: the codex client singleton is now reset between each trial.

### B4: LLM-as-judge -- mitigated by cross-model design
LLM judges have systematic biases (preferring verbose output, favoring certain rhetorical styles). Same-family judges (GPT judging GPT output) inflate scores. Mitigated by using two judge families. In Track 1, GPT scored both conditions at 8.88 mean while Opus scored ~6.0. Both reached the same structural conclusion (tie), but Opus was more discriminating.

### B5: Single generator model
Both conditions use the same model (via Codex OAuth, GPT-4o or equivalent). Results may not generalize to other model families.

### B6: Volume asymmetry in Track 2
Oscillation produces ~9 insights + ~11 knots vs. baseline's 5 ideas + 5 questions + synthesis. Judges may favor richer outputs regardless of per-item quality. Track 3 mitigates this: grounding normalizes output volume to format-specific requirements.

### B7: Mode-specific criteria may favor oscillation (Track 3)
The Track 3 criteria were designed to measure what good output looks like for each mode, not to favor either condition. However, criteria like "unresolved tension" (essay), "preserved tension" (strategy), "productive conflict" (hypotheses), and "resistance to resolution" (provocations) align with oscillation's architectural strengths. This is partially by design -- these criteria exist because tension preservation is genuinely valuable in these formats -- but it creates a structural advantage. The mitigation is that each mode also includes criteria where baseline should compete well (thesis strength, falsifiability, testability, precision).

### B8: Grounding prompt design is not adversarial to oscillation
The mode-specific grounding prompts were written with knowledge of oscillation's strengths (metaphorical register, tension preservation). A grounding prompt designed by someone unfamiliar with the system might not preserve these qualities. This means Track 3 tests the best case for oscillation's grounding, not the typical case.

---

## 9. Running the Evaluation

```bash
# Set API key (optional -- routes through Codex OAuth without it)
export OPENAI_API_KEY='your-key-here'

# Track 1: Grounded evaluation (generic grounding)
./eval-run                                    # 10 seeds x 2 GPT judges
./eval-run --seeds 2 --judges 1               # Smoke test

# Track 2: Raw evaluation (no grounding)
python eval/run_raw_eval.py                   # Generate raw outputs + GPT judges
# Opus judges run via Claude Code subagents

# Track 3: Mode-specific grounded evaluation
python eval/run_mode_eval.py                  # 12 trials x 2 GPT judges
python eval/run_mode_eval.py --mode essay     # Single mode only
python eval/run_mode_eval.py --resume eval/mode_results_TIMESTAMP.json

# Resume any interrupted run
./eval-run --resume eval/results_TIMESTAMP.json
python eval/run_raw_eval.py --resume eval/raw_results_TIMESTAMP.json
```

---

## 10. File Listing

### Protocol and results
- `eval/PROTOCOL.md` -- this document
- `eval/RESULTS.md` -- combined results for Tracks 1 and 2
- `EVAL-oscillation-vs-baseline.md` -- initial informal evaluation (pre-protocol)

### Track 1 (grounded, generic)
- `eval/run_eval.py` -- main evaluation runner
- `eval/oscillation_runner.py` -- runs oscillation condition
- `eval/baseline.py` -- runs baseline condition
- `eval/judge.py` -- grounded judge (generic criteria)
- `eval/report.py` -- generates Track 1 report from results
- `eval/seeds.json` -- seed definitions
- `eval/results_20260418_091937.json` -- Track 1 raw data
- `eval/results_20260418_091937_report.md` -- Track 1 GPT judge report
- `eval/results_20260418_091937_stats.json` -- Track 1 statistics

### Track 2 (raw, no grounding)
- `eval/run_raw_eval.py` -- raw evaluation runner
- `eval/judge_raw.py` -- raw judge (same 6 criteria, no grounding)
- `eval/raw_results_20260418_095054.json` -- Track 2 generation data
- `eval/raw_gpt_judgments.json` -- Track 2 GPT judge results

### Track 3 (grounded, mode-specific)
- `eval/run_mode_eval.py` -- mode-specific evaluation runner (to be created)
- `eval/grounding_prompts/` -- mode-specific grounding prompts (to be created)
- `eval/judge_mode.py` -- mode-specific judge with per-mode criteria (to be created)

---

## 11. Limitations and Future Work

**This evaluation does not prove:**
- That oscillation is better than *any* alternative prompting strategy
- That the specific DG/CC/TC prompts are optimal
- That more LLM calls aren't the sole driver of improvement
- That results generalize beyond the model used

**Future work beyond Track 3:**
1. **Compute-controlled test**: 7-call baseline vs. 7-call oscillation to isolate architecture from iteration count
2. **Embeddings-enabled run**: with `OPENAI_API_KEY` set, re-run to measure the impact of semantic novelty filtering
3. **Human judges**: recruit 3-5 domain experts to replace LLM-as-judge
4. **Longitudinal test**: multi-session oscillation with persistent memory vs. fresh-start baseline
5. **Ablation study**: remove one component at a time (TC only, no memory, no specialized prompts) to identify which pieces matter most
6. **Cross-model test**: run on Claude, Gemini, and open-source models to test generalizability
