# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Oscillating Cognition is a cognitive orchestration system that simulates oscillation between:
- **Divergent generation** (chaos / low-density exploration)
- **Convergent structuring** (compression / coherence / critique)

The system models human-like thought: Generate → Tension → Compress → Preserve ambiguity → Regenerate

## Architecture

Five core components:

1. **Memory Fabric** - Three layers:
   - `scratch/` - Volatile, cleared each cycle (raw fragments, discarded ideas)
   - `crystallized.json` - Persistent compressed structures (models, constraints, principles)
   - `open_knots.json` - Persistent unresolved tensions (paradoxes, contradictions, ambiguous concepts)

2. **Divergent Generator (DG)** - Produces low-density cognitive artifacts (metaphors, hypotheses, inversions, images, frames). Must avoid conclusions, summaries, and optimization language.

3. **Convergent Critic (CC)** - Evaluates coherence, compresses models, rejects noise. Must preserve at least one unresolved tension per cycle.

4. **Tension Controller (TC)** - Monitors compression delta, novelty proxy, and knot preservation score to maintain chaos-structure balance.

5. **Orchestrator Loop** - Main execution loop cycling through DG → CC → memory update → TC adjustment.

## Build & Run

```bash
# Set API key
export OPENAI_API_KEY='your-key-here'

# Run with a seed topic (uses .venv automatically)
./oscillate --seed "consciousness and recursion"

# Run with custom cycle count
./oscillate --seed "emergence" --cycles 5

# Reset memory and start fresh
./oscillate --reset --seed "paradox of self-reference"
```

## File Structure

```
config.py                  # Configuration (API settings, parameters)
memory_manager.py          # Memory layer operations
divergent_generator.py     # DG module (high-temp artifact generation)
convergent_critic.py       # CC module (compression and critique)
tension_controller.py      # TC metrics and adaptive adjustments
orchestrator.py            # Main loop
run.py                     # CLI entry point
prompts/
    dg_prompt.txt          # DG system prompt
    cc_prompt.txt          # CC system prompt
memory/
    crystallized.json      # Persistent compressed structures
    open_knots.json        # Persistent unresolved tensions
scratch/
    last_cycle.json        # Volatile per-cycle data
```

## Key Constraints

- System must maintain at least one active "open knot" (unresolved tension) at all times
- CC can select maximum 3 artifacts per cycle
- Silence (`NO_ADD`) is a valid intentional output when adding content would reduce tension quality
- If all knots are resolved, the system has "collapsed into dense mode" - trigger forced divergence

## Anti-Patterns to Avoid

- Auto-summarizing everything
- Collapsing ambiguity immediately
- Over-optimizing for coherence
- Producing generic assistant-style output
