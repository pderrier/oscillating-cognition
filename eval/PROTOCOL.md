# Evaluation Protocol: Oscillating Cognition vs. Iterative Baseline

**What we test, why it matters, and what the results would mean.**

---

## 1. The Claim

Oscillating Cognition's thesis: LLMs converge too fast. By structuring generation into explicit divergent/convergent phases with persistent memory, adaptive temperature control, and mandatory tension preservation, the system produces richer, more human-like thinking than standard iterative prompting.

This evaluation tests that claim on external domains with controlled methodology.

---

## 2. What We Actually Compare

Both conditions explore the same seed topic. We run **two evaluation tracks**:

- **Track 1 (Grounded):** Both conditions produce a grounded output (actions, experiments, questions, synthesis) using an identical grounding prompt. Tests the full pipeline end-to-end.
- **Track 2 (Raw):** We compare the raw upstream outputs before grounding — crystallized insights + open knots (oscillation) vs. synthesized ideas + open questions (baseline). Tests whether the thinking process itself differs.

Track 2 was added after Track 1 revealed that grounding homogenizes both conditions (see [RESULTS.md](RESULTS.md)).

### Condition A — Oscillation (3 cycles)

Each cycle makes 2 LLM calls (~7 total, +1 optional grounding):

```
┌─ Cycle 1 ──────────────────────────────────────────┐
│  DG (temp 0.95) → 5 artifacts                      │
│    Specialized prompt: no conclusions allowed,      │
│    must produce metaphors/inversions/hypotheses     │
│  CC (temp 0.4) → select max 3, compress, add knots │
│    Must preserve ≥1 unresolved tension              │
│  TC → compute metrics, adjust temperature           │
│  Memory → crystallized.json, open_knots.json        │
└─────────────────────────────────────────────────────┘
        ↓ memory persists
┌─ Cycle 2 ──────────────────────────────────────────┐
│  DG sees accumulated context + knots + probes       │
│  CC sees richer material, builds on prior models    │
│  TC detects stagnation or excessive convergence     │
└─────────────────────────────────────────────────────┘
        ↓ memory persists
┌─ Cycle 3 ──────────────────────────────────────────┐
│  Same loop. TC may force divergence if too rigid.   │
└─────────────────────────────────────────────────────┘
        ↓
  Raw output: crystallized insights + open knots
        ↓ (Track 1 only)
┌─ Grounding ────────────────────────────────────────┐
│  Same prompt as baseline.                           │
│  Input: crystallized insights + open knots          │
│  Output: actions, experiments, questions, synthesis │
└─────────────────────────────────────────────────────┘
```

### Condition B — Standard iterative refinement (3 passes)

3-4 LLM calls total:

```
┌─ Pass 1: Generate (temp 0.7) ──────────────────────┐
│  Generic prompt: "generate 5 ideas, be creative"    │
└─────────────────────────────────────────────────────┘
        ↓ output forwarded
┌─ Pass 2: Critique (temp 0.5) ──────────────────────┐
│  Generic prompt: "critique, refine, find tensions"  │
└─────────────────────────────────────────────────────┘
        ↓ output forwarded
┌─ Pass 3: Synthesize (temp 0.5) ────────────────────┐
│  Generic prompt: "best ideas + open questions"      │
└─────────────────────────────────────────────────────┘
        ↓
  Raw output: final ideas + open questions + synthesis
        ↓ (Track 1 only)
┌─ Grounding ────────────────────────────────────────┐
│  Same prompt as oscillation.                        │
│  Input: synthesized ideas + open questions           │
│  Output: actions, experiments, questions, synthesis │
└─────────────────────────────────────────────────────┘
```

### The Real Differences

| Dimension | Oscillation | Baseline |
|-----------|-------------|----------|
| **Generation prompts** | Specialized: forbids conclusions, forces fragments, metaphors, inversions | Generic: "be creative and specific" |
| **Critique prompts** | Specialized: must preserve tensions, max 3 selections, compress to models | Generic: "critique and refine" |
| **Temperature strategy** | Deliberate oscillation: 0.95 (chaos) → 0.4 (structure), adaptive via TC | Flat: 0.7 → 0.5, no adaptation |
| **Memory across passes** | Persistent: each cycle sees all prior insights + knots | Stateless: each pass sees only the previous pass output |
| **Feedback loop** | TC monitors compression ratio, novelty, knot count; triggers forced divergence | None |
| **LLM calls** | ~7 (+1 grounding in Track 1) | 3 (+1 grounding in Track 1) |

### Known Confound

Oscillation makes ~7 LLM calls vs. baseline's 3. We are not controlling for compute budget. This is inherent to the system design — but a future compute-controlled test (equal call count) would separate the two effects.

---

## 3. Evaluation Method

### Seeds

10 external-domain topics. None reference oscillating cognition or AI tools, eliminating circular evaluation.

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

### Blind Judging — Two Judge Models

Each trial is evaluated by **two different model families** to detect same-family scoring bias:

| Judge | Model | Relation to generator | Judges per seed |
|-------|-------|----------------------|-----------------|
| **Judge GPT** | GPT-4o (via Codex OAuth) | Same family as generator | 2 |
| **Judge Opus** | Claude Opus 4.6 | Different family | 1 |

Both judges receive outputs as "Output X" and "Output Y" with randomized assignment. Neither judge knows which method produced which output.

Position bias mitigation: X/Y assignment is randomized independently per judgment.

### Criteria (scored 1-10)

| Criterion | What it measures |
|-----------|-----------------|
| **Novelty** | How surprising and non-obvious are the proposals? |
| **Depth** | Genuine engagement with complexity, or surface-level? |
| **Specificity** | Concrete enough to act on, with clear rationale? |
| **Internal tension** | Productive contradictions preserved, or everything flattened? |
| **Emergent insight** | Ideas that are more than the sum of inputs? |
| **Human-likeness** | Reads like thoughtful human exploration, or predictable LLM list? |

No criterion references oscillation-specific vocabulary (knots, divergence, etc.).

### Statistical Design

- 10 seeds × 3 judges (2 GPT + 1 Opus) = 30 judgments per track
- Cross-model judging detects same-family inflation
- Resumable: partial runs can be continued
- Per-seed and aggregate reporting

---

## 4. What the Results Would Mean

### If oscillation wins clearly (>65% win rate, +1.0 mean delta)

The specialized architecture — constrained prompts, persistent memory, temperature oscillation, mandatory tension preservation — produces measurably better thinking than generic multi-pass prompting. The system's design choices are validated.

### If it's close (40-60% win rate, <0.5 mean delta)

The oscillation architecture doesn't clearly outperform competent iterative prompting. The value may be in the process (making the multi-pass automatic and reproducible) rather than in the output quality. The specialized prompts and memory architecture need refinement.

### If baseline wins (>60% baseline win rate)

The oscillation constraints may be hurting more than helping. Forcing metaphors, inversions, and tension preservation may produce interesting-sounding output that doesn't ground well into actionable proposals. The system would need fundamental rethinking.

### If Track 1 (grounded) shows no difference but Track 2 (raw) does

The grounding phase is homogenizing the outputs — compressing different upstream thinking into the same policy-memo format. This would indicate that the oscillation architecture works but the grounding prompt needs redesign to preserve divergent texture.

### What to watch per-criterion

- **Internal tension** is where oscillation should dominate — it's architecturally forced to preserve contradictions.
- **Specificity** is where baseline might win — generic prompts may produce more conventional but more actionable proposals.
- **Human-likeness** is the most important criterion for the project's thesis. If oscillation consistently scores higher here, it validates the core claim that structured chaos-structure cycling produces more human-like thinking.
- **Novelty × Specificity** tradeoff: if oscillation is more novel but less specific, the grounding step isn't doing its job of bridging abstraction to action.
- **GPT vs. Opus divergence**: if GPT judges see differences that Opus doesn't (or vice versa), this reveals model-specific evaluation bias.

---

## 5. Running the Evaluation

```bash
# Track 1: Grounded evaluation (full pipeline)
./eval-run                                    # 10 seeds × 2 GPT judges
./eval-run --seeds 2 --judges 1               # Smoke test

# Track 2: Raw evaluation (pre-grounding)
python eval/run_raw_eval.py                   # Generate raw outputs
# Opus judges are run via Claude Code subagents

# Resume interrupted run
./eval-run --resume eval/results_TIMESTAMP.json
python eval/run_raw_eval.py --resume eval/raw_results_TIMESTAMP.json
```

Outputs:
- `eval/results_<timestamp>.json` — grounded evaluation data (Track 1)
- `eval/results_<timestamp>_report.md` — GPT judge report
- `eval/raw_results_<timestamp>.json` — raw evaluation data (Track 2)
- `eval/RESULTS.md` — combined final report

Works with or without `OPENAI_API_KEY`. Without a key, routes through Codex CLI OAuth automatically.

---

## 6. Known Biases

### B1: Unequal LLM call count
Oscillation makes ~7 calls; baseline makes 3. We are not isolating architecture from raw iteration count. This is inherent to the system design — but a future compute-controlled test (equal call count) would separate the two effects.

### B2: Embedding novelty disabled (OAuth mode)
When running via Codex OAuth (no `OPENAI_API_KEY`), the embedding API is unavailable. The Codex app-server protocol does not expose an embeddings endpoint. Oscillation falls back to **lexical diversity** for novelty scoring instead of semantic similarity. This means:
- The DG novelty filter is degraded: it catches literal repetition but misses semantic paraphrases
- The TC novelty metric is less accurate: it may not detect "spinning in circles" with varied vocabulary

This is a **handicap for oscillation** — it runs with a weaker filter than its intended design. Baseline is unaffected (it never uses embeddings). Results with `OPENAI_API_KEY` set (full embeddings) should be strictly better for oscillation.

### B3: Thread contamination (Run 1 only — fixed)
The first evaluation run reused a single Codex app-server thread across all seeds. The model may have carried conversational context from one seed into the next. This was **fixed** in subsequent runs: the codex client singleton is now reset between each trial (oscillation, baseline, and judge), giving each a fresh thread with no prior context.

### B4: LLM-as-judge — mitigated by cross-model design
LLM judges may have systematic biases (preferring verbose output, favoring certain rhetorical styles). Same-family judges (GPT judging GPT output) tend to inflate scores. We mitigate this by using **two judge families**:
- GPT (same family as generator) — 2 judges per seed
- Claude Opus (different family) — 1 judge per seed

Cross-model comparison reveals scoring inflation: in Track 1, GPT scored both conditions at 8.88 mean while Opus scored ~6.0. Both reached the same structural conclusion (tie), but Opus was more discriminating.

### B5: Single generator model
Both conditions use the same model (via Codex OAuth, GPT-4o or equivalent). Results may not generalize to other model families.

---

## 7. Limitations and Future Work

**This evaluation does not prove:**
- That oscillation is better than *any* alternative prompting strategy
- That the specific DG/CC/TC prompts are optimal
- That more LLM calls aren't the sole driver of improvement
- That results generalize beyond the model used

**Next steps:**
1. **Raw output evaluation** (Track 2): compare pre-grounding outputs to test whether the thinking process itself differs, even if grounding erases the difference
2. **Redesign grounding prompt**: if Track 2 shows oscillation wins upstream, the grounding prompt needs to preserve divergent texture instead of compressing to policy-memo format
3. **Compute-controlled test**: 7-call baseline vs. 7-call oscillation to isolate architecture from iteration count
4. **Embeddings-enabled run**: with `OPENAI_API_KEY` set, re-run to measure the impact of semantic novelty filtering
5. **Human judges**: recruit 3-5 domain experts to replace LLM-as-judge
6. **Longitudinal test**: multi-session oscillation with persistent memory vs. fresh-start baseline (testing the compounding memory hypothesis)
7. **Ablation study**: remove one component at a time (TC only, no memory, no specialized prompts) to identify which pieces matter most
8. **Cross-model test**: run on Claude, Gemini, and open-source models to test generalizability
