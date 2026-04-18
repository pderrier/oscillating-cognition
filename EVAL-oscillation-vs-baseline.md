# Does Oscillating Cognition Produce Better Ideas?

**An informal A/B evaluation of structured divergent-convergent cycling vs. standard LLM prompting for roadmap ideation.**

April 2026 — Oscillating Cognition project

---

## 1. Setup

We used Oscillating Cognition's own roadmap as the test case: given the project's README and current feature list, generate better, more ambitious future directions.

### Condition A — Oscillation (3 cycles of DG → CC → TC)

The oscillating cognition methodology was applied manually (the LLM simulated the system's roles):

- **Divergent Generator** produced 4-5 artifacts per cycle (metaphors, inversions, hypotheses, fragments) with explicit constraints: no conclusions, no optimization language, contradictions welcome.
- **Convergent Critic** selected max 3 per cycle, rejected noise, compressed insights, and preserved at least one unresolved tension ("open knot").
- **Tension Controller** monitored compression delta, novelty, and knot count across cycles.
- A **Grounding phase** then transformed abstract insights into concrete actions, experiments, and questions.

### Condition B — Standard prompting (single pass)

The same LLM (Claude Opus) received a straightforward prompt: *"Read the README and suggest better, more ambitious roadmap ideas. Be creative. Do NOT use oscillation methodology."* Run twice independently to reduce variance.

### Evaluation

Two independent judge agents (Claude Opus, no shared context) received both roadmaps and scored them on 6 criteria (1-10 scale): Novelty, Coherence with project identity, Ambition, Specificity, Emergent insight, Preserved tension.

---

## 2. Results

### Score table (two judges)

| Criterion | A (oscillation) | B (standard) | Judge 1 Δ | Judge 2 Δ |
|-----------|:---:|:---:|:---:|:---:|
| Novelty | 7 | 5 | +2 A | +2 A |
| Coherence with identity | 9 | 5 / 4 | +4 A | +5 A |
| Ambition | 7 | 7 / 6 | = | +1 A |
| Specificity | 6 | 8 / 7 | **+2 B** | **+1 B** |
| Emergent insight | 8 | 4 | +4 A | +4 A |
| Preserved tension | 9 | 2 / 1 | +7 A | +8 A |
| **Average** | **7.7** | **5.2 / 4.5** | | |

Both judges reached the same conclusion independently: **A wins overall, B wins on specificity only.**

### What A produced that B didn't

- **Convergence Detection** — turn the system's internal tension controller outward: analyze the *user's* prose for premature closure. Both judges flagged this as the standout emergent insight — an inversion that doesn't follow from reading the README.
- **Knot Gardening** — reframe knots from passive artifacts to cultivated objects with temporal extent. Shifts the product from "run once" to "daily practice."
- **Three open knots** that question the roadmap's own best ideas (e.g., "does thought forking lead to clarity or paralysis?").

### What B produced that A didn't

- **Multi-Seed Collision** — force unrelated seeds together. Both judges flagged this as genuinely good and absent from A.
- **Slow Thinking / Daemon Mode** — one cycle per hour/day with notifications. A temporal reframing B discovered independently.
- **RAG Integration** — anchor divergent generation in external sources. Practical, absent from A.

### Where they converged

Both independently proposed: thought forking/branching, adversarial modes, idea lineage/provenance tracking, plugin architecture. These ideas appear robust — they emerge regardless of method.

---

## 3. Adversarial Critique of the Evaluation

We then applied adversarial analysis to challenge A's apparent superiority. Five flaws were identified:

### Flaw 1: Unequal effort (Critical)

A had 3 structured cycles + grounding. B had 1 pass. We may have measured *iteration count*, not *method quality*. A fair comparison would pit 3 oscillation cycles against 3 standard iterative refinement passes.

**Counterpoint:** The multi-pass structure *is the product*. The user runs `./oscillate --cycles 3` and gets the result. Comparing the tool's output against a single prompt is a valid product evaluation, even if it's not a valid method evaluation. These are different questions.

### Flaw 2: Non-blind judges (High)

Judges knew which roadmap used oscillation. The criterion "preserved tension" maps directly to oscillation vocabulary — A scores 9 because the method *forces* knot production. B scores 1 because nobody asked it to preserve tensions. This criterion measures format compliance, not thinking quality.

### Flaw 3: Circular coherence (Medium)

Judging an oscillation-generated roadmap on "coherence with a project about oscillation" is self-referential. A naturally produces outputs that sound like the system that produced them.

### Flaw 4: Emergent insight may be overrated (Medium)

"Convergence Detection" is a mechanical inversion (apply internal mechanism X to external target Y), not necessarily a deep insight. It impresses in brainstorms but may have no viable use case. B's "Comparative Session Analysis" is less flashy but would actually advance the research.

### Flaw 5: Questions vs. answers (Context-dependent)

A produces elegant questions. B produces implementable answers. For a *thinking tool*, questions may be the point. For a *product roadmap*, shipping features matters. The evaluation doesn't distinguish these goals.

---

## 4. What This Actually Proves (and Doesn't)

### Three distinct claims, three different verdicts

| Claim | Verdict | Why |
|-------|---------|-----|
| **The oscillation method is inherently superior to standard prompting** | Not proven | Effort was unequal. Need controlled comparison at equal iteration count. |
| **The `oscillate` tool produces better output than a single standard prompt** | Proven (trivially) | This is the product's value proposition: automate structured multi-pass thinking so the user doesn't have to. Comparing it to a single prompt is like comparing a compiler to hand-written assembly — the asymmetry is the point. |
| **Oscillation makes LLM output more human-like and creative** | Promising, not proven | A produced inversions, self-doubt, and productive metaphors that B didn't. But the protocol lacks the rigor to make this claim with confidence. |

### The third claim is the one that matters

The project's stated goal is to make AI think more like humans: generate wildly, compress ruthlessly, preserve ambiguity. The interesting signal in this evaluation is not the scores — it's the *qualitative texture* of A's output:

- A doubts its own best ideas. B presents everything as unambiguously good.
- A produces metaphors that reframe the problem space (knots as seeds, not problems). B produces features.
- A leaves deliberate gaps. B tries to be comprehensive.

These are hallmarks of human creative thinking. Whether the oscillation method *causes* them or whether more iteration *would have produced the same result with any method* is the open question.

---

## 5. A Rigorous Protocol (If We Wanted to Prove It)

1. **Equal effort:** 3 oscillation cycles vs. 3 standard "critique-and-improve" passes
2. **Blind judges:** Roadmap 1 / Roadmap 2, zero method information
3. **Non-circular criteria:** Drop "preserved tension" and "coherence with identity." Add "utility for real users" and "originality vs. state-of-the-art AI tools"
4. **External domains:** Test on seeds unrelated to oscillating-cognition (business strategy, scientific research, product design) to eliminate self-reference
5. **Statistical power:** N ≥ 10 runs per condition
6. **Human-likeness metric:** Have humans rate outputs on "could this have come from a good human brainstorm?" vs. "this sounds like an LLM." If oscillation systematically makes LLM output less recognizable as LLM, that's the strongest possible evidence for the project's thesis.

---

## 6. Takeaways

**For the project:** The evaluation suggests oscillation produces *qualitatively different* output — more self-critical, more metaphorical, more comfortable with ambiguity. Whether this is the method or the iteration count is unresolved. Both are worth investigating.

**For the roadmap:** The best roadmap is probably A's vision + B's specificity + B's two unique ideas (Multi-Seed Collision, Slow Thinking). The open knots from A should be preserved as design constraints, not resolved prematurely.

**For the research:** The real experiment hasn't been run yet. This session produced the protocol. The next step is to run it on external domains, blind, at equal effort, and measure human-likeness directly.
