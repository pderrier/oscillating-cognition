# Does Forcing an AI to Think Like a Human Actually Work? We Tested It.

Follow-up to "Another Approach to Building Machine Intelligence: Between Chaos and Structure"
https://www.linkedin.com/pulse/another-approach-building-machine-intelligence-between-pierre-derrier-2ow1f/

---

A few months ago, I published an article about Oscillating Cognition — a system designed to make LLMs think more like humans.

The premise: LLMs converge too fast. Ask one a hard question and it summarizes, concludes, and moves on. Great for quick answers, but terrible for deep exploration — the kind where you need to sit with contradictions, follow unexpected tangents, and resist the urge to wrap things up neatly.

So we built a cognitive orchestration system that forces oscillation between divergence (wild, metaphorical, conclusion-free generation at high temperature) and convergence (ruthless compression, critique, but with at least one unresolved tension preserved per cycle). A Tension Controller monitors the balance and injects chaos if the system becomes too rigid. Memory persists across cycles so ideas compound.

The system runs as an MCP server (github.com/pderrier/oscillating-cognition) — any AI agent can call oscillate(seed="your topic", cycles=3) and get back crystallized insights, open questions, and optionally grounded action proposals. It also has a CLI and a web UI.

The obvious next question was: does it actually produce better thinking than standard prompting?

So we built a rigorous A/B evaluation and ran it. Here's what we found — including where the system genuinely outperforms, where it doesn't, and an unexpected meta-discovery about how different AI models judge quality itself.


THE TEST DESIGN

We compared oscillation against a fair baseline — not a single prompt, but a 3-pass iterative refinement (generate, critique, synthesize). The kind of structured chain-of-thought that a competent engineer would build. Same number of iteration passes, same final formatting.

We picked 10 topics across domains that have nothing to do with our project — to prevent circular evaluation:

- "CRISPR gene editing should be available for non-medical human enhancement" (bioethics)
- "Remote-first companies will outcompete office-first companies within 10 years" (business strategy)
- "Nuclear energy is the only realistic path to decarbonization at scale" (energy policy)
- "AI-generated art is not art and should not be treated as such" (aesthetics)
- ...and six more across education, urban planning, philosophy, economics, social futures, and systems theory.

Both systems explored each topic, and their outputs were evaluated blindly — judges see "Output X" and "Output Y" with randomized assignment. No labels, no method names. Two different judge models (GPT-5.4 and Claude Opus) to catch model-specific bias.

We ran three evaluation tracks, each designed in response to what the previous one revealed.


TRACK 1: THE HUMBLING TIE

Both systems explored each topic, then their raw thinking was passed through an identical "grounding" prompt that converts insights into a structured deliverable: actions to take, experiments to run, questions to investigate, and a synthesis.

Result: perfect tie. Mean scores of 8.88 vs 8.88. Sixty percent of judgments were ties.

One judge noted:

"The overlap is so extensive that it suggests a shared underlying template rather than independent reasoning."

This was our first surprise. Both systems — one with specialized prompts, persistent memory, temperature oscillation, and tension preservation, the other with three generic passes — produced near-identical policy memos after grounding.

The problem wasn't the thinking engine. It was the last mile: the grounding step was acting as a convergent compressor that flattened everything into the same format, erasing whatever upstream difference existed.


TRACK 2: WHAT DOES OSCILLATION ACTUALLY THINK?

So we removed the grounding step entirely and compared the raw upstream outputs side by side: oscillation's crystallized insights + deliberately unresolved tensions versus baseline's refined ideas + synthesis.

Result: oscillation wins 19 out of 20 blind judgments.

The per-criterion breakdown reveals what's different — and what isn't:

Oscillation produces more of:
- Novelty: +1.8
- Preserved contradictions: +1.8
- Emergent insight: +1.5
- Human-likeness: +0.8
- Depth: +0.6

Baseline produces more of:
- Specificity / actionability: +1.7

Oscillation wins on 5 out of 6 criteria. But baseline wins on the one that matters most for practical use: specificity.

To make this concrete, here's what the difference looks like. On the topic "Remote-first companies will outcompete office-first companies within 10 years":

The baseline produced insights like: "Remote-first advantage is operational legibility — written decisions create compounding institutional memory" and "Geographic diversification reduces cost shocks." Competent, correct, and you've read it before.

Oscillation produced: "Remote-first may sort for liminal operators: people fluent in translation, ambiguity, and self-explanation rather than people whose authority depends on thick local context" and "Physical co-presence may function less as a coordination engine than as a trust-conversion device, turning uncertainty into felt legitimacy through embodied ritual."

A judge summarized it:

"The baseline delivers a competent, well-organized take that reads like a strong blog post — correct but largely predictable. Oscillation operates at a genuinely different level of abstraction: rival memory architectures, interpretive hierarchies, presence as trust-conversion ritual."

On "AI tutors will make traditional universities obsolete":

"Oscillation treats the university as a psychosocial institution — moratorium on adulthood, witness to becoming, accent formation, marriage market — rather than defaulting to the standard unbundling/credentialing frame that the baseline reproduces competently but predictably."

The thinking is genuinely different in kind, not just degree. But it's less actionable. That tradeoff is real and, as we'd discover, irreducible by design.


TRACK 3: THE RIGHT OUTPUT FOR THE RIGHT JOB

Track 1 showed that generic grounding erases the difference. Track 2 showed that the raw thinking is superior but too abstract. The natural question: what if we design the output format to match the actual use case?

We built four "grounding modes" — each with its own prompt and its own judging criteria.


Essay mode

Instead of actions and experiments, the grounding prompt asks: "Write a structured essay with a narrative arc. Use tensions as rhetorical structure. Preserve the strongest metaphors as section anchors."

We tested this on three philosophical and societal topics — machine consciousness, life-extension inequality, and AI-generated art. Each system's raw thinking was grounded into an essay, then judged on: narrative voice, tension as structure, originality of framing, "would you keep reading?", and intellectual honesty.

Result: oscillation wins all 9 judgments. Both judge models agree.

The essays were strikingly different. On "We will never be able to determine whether a machine is conscious", oscillation produced an essay titled "The Trial We Can Never Finish" — built around consciousness as an asylum claim, where private reality is true but public legitimacy is granted only through hostile procedures. Baseline produced "The Witness We Cannot Call" — a well-organized epistemological survey.

A judge compared them:

"Oscillation's tensions genuinely destabilize the reader's footing. Baseline's tensions organize the reader's learning. That is the difference between an essay and a textbook chapter."

On AI-generated art:

"Baseline would be publishable in a generalist outlet. Oscillation would make someone stop scrolling."

On life-extension inequality:

"Oscillation earns its unresolved ending — the impossibility feels discovered through the argument. Baseline's unresolved ending feels more like a responsible caveat."

(Full essays are available in the eval data on GitHub if you want to judge for yourself.)


Provocation mode

The prompt asks: "Generate 5 provocative questions designed to destabilize consensus in a team discussion. Each must be uncomfortable, precise, and impossible to answer with a platitude."

We tested on urban car bans, university obsolescence, and CRISPR ethics. Judged on: discomfort level, precision, resistance to platitudes, ability to unstick a group.

Result: oscillation wins 2 out of 3 seeds unanimously.

On "CRISPR gene editing should be available for non-medical human enhancement", the baseline asked questions like: "If enhancement is legal only through accredited clinics, what stops it from becoming a premium advantage for the wealthy?" — a real question, but one a bioethics seminar handles routinely.

Oscillation asked: "If the rich can signal superiority both by editing their children and by publicly refusing to edit them, what makes you think legalization levels the field?"

The judge:

"Oscillation's questions assume legalization has already happened and ask what follows, which strips away the comfortable abstraction layer. Baseline leans on familiar policy-debate framing that experienced participants can handle with practiced responses."

On university obsolescence:

"Oscillation asks whether universities are a diagnosable pathology and whether their survival instincts will make them actively harmful. That move is harder to deflect."


Strategy and hypothesis modes — where it gets complicated

We also tested strategic option generation ("We should pivot to an AI-tutor-first platform") and research hypothesis generation ("Nuclear is the only realistic path to decarbonization").

Here's where something unexpected happened: the two judge models disagreed systematically.

GPT-5.4 preferred baseline on every strategy and hypothesis seed. Claude Opus preferred oscillation on every one. Same rubric, same outputs, opposite verdicts.


THE META-FINDING: AI MODELS HAVE IMPLICIT VALUES

This turned out to be the most thought-provoking result of the entire evaluation.

On the strategy seed, Opus gave these scores (1-10 scale):

Oscillation scored: Non-obviousness 8, Clarity of tradeoffs 9, Actionability 5, Decision-readiness 6
Baseline scored: Non-obviousness 5, Clarity of tradeoffs 8, Actionability 8, Decision-readiness 8

The total scores are nearly tied. But which criteria you weight determines who wins. GPT implicitly weighted actionability and decision-readiness. Opus implicitly weighted originality and tradeoff clarity.

Opus articulated this precisely:

"Oscillation optimizes for intellectual originality at the cost of executability. Baseline optimizes for decision utility at the cost of originality. If the ask were 'which set do I hand to an exec team on Monday,' the answer flips."

We ran a meta-analysis on the disagreement itself. The conclusion:

"The two judges are answering different implicit questions. One asks: which output is more useful to a decision-maker? The other: which output demonstrates stronger strategic thinking? These are not the same question."

"The disagreement itself is the most informative signal in this evaluation. A single-judge system would have presented one answer as authoritative."

This has implications far beyond our project. Anyone using LLM-as-judge should know that a single model gives you one implicit value system, not ground truth. Cross-model judging doesn't just reduce bias — it surfaces tensions in what "quality" means. (We wrote a standalone analysis on this finding, available on the GitHub repo.)


SO WHEN SHOULD YOU USE OSCILLATION?

After three tracks and 60+ blind judgments across two judge models, the answer isn't "always" or "never." It depends on what you need the output to do.

Oscillation's strength is producing ideas you wouldn't have reached otherwise. Across every seed and every mode, judges consistently described its output as operating at a "genuinely different level of abstraction" — reframing problems instead of mapping them, questioning the terms of the debate instead of arguing within them. On research ideation, a judge noted that "the field is saturated with baseline-type studies and starved for this type of reframing." On provocations, oscillation's questions "locate the uncomfortable insight one layer deeper." On essays, the difference was described as "between an essay and a textbook chapter" — and more bluntly: "baseline would be publishable in a generalist outlet; oscillation would make someone stop scrolling."

Baseline's strength is producing output you can act on immediately. Its strategy options "genuinely span a spectrum from narrow-and-safe to broad-and-disruptive, so a leadership team could use this set to locate their risk appetite and pick a direction." Its research hypotheses have "numeric thresholds, named methods, and clear success criteria" — a modeler could start work tomorrow. Oscillation's hypotheses are more original but harder to operationalize: they "interrogate the construct validity of the dependent variable" rather than adding variables to a regression.

Here's the practical guide:

Use oscillation for:
- Essay and thought piece writing (+3.0 on originality of framing) — "tensions destabilize the reader's footing" vs "tensions organize the reader's learning"
- Workshop provocations — "harder to deflect with stock answers," locates the insight "one layer deeper"
- Research ideation (what to study) — "would change how we interpret the debate itself" vs baseline that "confirms existing intuitions"
- Strategy exploration — more surprising options, sharper tradeoffs, "every option built around a real insight"

Use baseline for:
- Research protocols (how to test) — falsifiability +3.0, "could be handed to a modeler tomorrow"
- Monday-morning strategy decisions — better portfolio coverage, more executable, "spans a risk spectrum for an exec team"
- Policy memos — generic grounding makes both identical anyway

The core tradeoff is irreducible by design. The divergent generator forbids conclusions and forces metaphors and inversions. That's what produces genuinely novel thinking — and also what makes it less concrete. You can't maximize both simultaneously.

But you can sequence them. The most promising path: oscillation upstream for exploration, then adapted grounding for the specific deliverable. Our essay and provocation modes already prove this works — the upstream richness survives when the output format is designed to carry it. Strategy and hypothesis modes need further work — probably splitting into "explore" and "decide" sub-modes, so you get the reframing and the Monday morning action plan.


WHERE WE STAND (A TEMPORARY CONCLUSION)

Oscillating Cognition started as a bet: that forcing an LLM to oscillate between chaos and structure — generating wildly, compressing ruthlessly, and deliberately preserving what remains unresolved — would produce thinking that a standard prompt chain cannot.

That bet is partially validated. The system genuinely produces different thinking. Not marginally better on the same axis, but operating on a different axis entirely — one that values reframing over mapping, tension over resolution, and surprise over completeness. When the output format is designed to carry that texture (essays, provocations), the result is measurably and unanimously superior.

But the system also has a real weakness: it doesn't naturally produce actionable output. Its strength in novelty comes at the cost of specificity, and if you compress the output into a standard deliverable format, you lose exactly what made it valuable. The grounding problem — how to translate rich, tension-preserving thinking into something a team can execute on — is the central open challenge.

My current take on when oscillating cognition earns its place:

Use it when you suspect you're thinking inside a frame you haven't noticed. When every brainstorm produces variations on the same three ideas. When a strategy deck feels thorough but somehow unsurprising. When a research proposal is rigorous but asks questions everyone is already asking. That's where the system reliably breaks through — not by being smarter, but by being structurally unable to settle.

Don't use it when you need to ship. If the question is "what do we build this sprint?" or "what's the test protocol?", standard iterative prompting is faster, more concrete, and equally good. Oscillation is a thinking tool, not an execution tool.

The most interesting space is in between — and it's where the work goes next. Can a system that thinks divergently also land concretely, without one destroying the other? The essay mode suggests yes. The strategy mode suggests not yet. That's an honest answer, and an interesting problem.


WHAT'S NEXT

1. Redesign the grounding prompts to preserve tensions alongside actions — the current "last mile" is too convergent for some modes

2. Human expert judges — LLM judges revealed fascinating model-level biases, but we need domain experts to establish ground truth

3. Cross-model generation — what happens when Claude runs the divergent generator and GPT runs the convergent critic?

4. Longitudinal testing — does oscillation with persistent memory across sessions compound insight over days, not just cycles?

The code, full evaluation data, judge quotes, and methodology are all open source:
github.com/pderrier/oscillating-cognition

---

The evaluation was run using GPT-5.4 (via Codex OAuth) for generation and judging, with Claude Opus 4.6 as cross-model judge.

Full methodology: github.com/pderrier/oscillating-cognition/blob/main/eval/PROTOCOL.md
Complete results with all judge quotes: github.com/pderrier/oscillating-cognition/blob/main/eval/RESULTS.md
Model divergence analysis: github.com/pderrier/oscillating-cognition/blob/main/eval/MODEL-DIVERGENCE.md
