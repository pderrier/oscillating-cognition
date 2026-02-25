# Oscillating Cognition

**A cognitive orchestration system that thinks before it concludes.**

Human creativity doesn't follow a straight line. It oscillates between chaos and structure—generating wildly, then compressing ruthlessly, while deliberately preserving unresolved tensions.

This prototype simulates that dynamic. It's not a chatbot. It's a thinking tool.

```
Generate → Tension → Compress → Preserve ambiguity → Regenerate
```

## Why?

LLMs converge too fast. They summarize, conclude, and move on. Great for quick answers. Not great for deep exploration.

Oscillating Cognition holds contradictions instead of resolving them. It produces:
- **Compressed insights** — validated, structured models
- **Open knots** — paradoxes and tensions kept deliberately unresolved
- **Probe directions** — angles for further exploration

## Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/oscillating-cognition.git
cd oscillating-cognition

# Set your API key
export OPENAI_API_KEY='your-key'

# Run (creates virtualenv automatically)
./oscillate --seed "consciousness and recursion"

# Run with custom cycles
./oscillate --seed "emergence" --cycles 5

# Reset memory and start fresh
./oscillate --reset --seed "new topic"
```

Override the API endpoint if needed:
```bash
export OPENAI_BASE_URL='https://your-proxy.com/v1'
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR LOOP                       │
│                                                             │
│    ┌──────────────┐              ┌──────────────┐          │
│    │   DIVERGENT  │──artifacts──▶│  CONVERGENT  │          │
│    │  GENERATOR   │              │    CRITIC    │          │
│    │  (temp 0.95) │              │  (temp 0.4)  │          │
│    └──────────────┘              └──────┬───────┘          │
│           ▲                             │                   │
│           │                             ▼                   │
│           │                    ┌────────────────┐          │
│           │                    │  MEMORY FABRIC │          │
│           │                    │  • crystallized│          │
│           │                    │  • open_knots  │          │
│           │                    └────────┬───────┘          │
│           │     ┌──────────────┐        │                   │
│           └─────│   TENSION    │◀───────┘                   │
│                 │  CONTROLLER  │                            │
│                 └──────────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

### Components

| Component | Role |
|-----------|------|
| **Divergent Generator** | High-temperature generation. Produces fragments, metaphors, hypotheses. Forbidden from concluding. |
| **Convergent Critic** | Low-temperature analysis. Compresses insights, rejects noise. Must preserve at least one tension. |
| **Memory Fabric** | Three layers: `crystallized` (persistent insights), `open_knots` (unresolved tensions), `scratch` (volatile) |
| **Tension Controller** | Monitors compression ratio, novelty, knot count. Triggers forced divergence if system becomes too rigid. |

## Output

After running, check your results:

```bash
# Validated insights
cat memory/crystallized.json | jq '.[].content'

# Unresolved tensions
cat memory/open_knots.json | jq '.[].content'
```

Memory persists across runs. Use `--reset` to start fresh.

## Example Session

```
[CYCLE 2]
============================================================

[DG] Generating artifacts (temp=0.95)...
  1. [metaphor] Recursion as a mirror facing a mirror
  2. [inversion] What if understanding prevents thinking?
  3. [hypothesis] Consciousness requires forgetting to avoid collapse

[CC] Critiquing...
  Selected: 2, Rejected: 3
  Compressed: "Self-reference may require structural amnesia"
  New knot: "Does awareness of a process alter the process?"

[TC] Metrics:
  Compression: 0.38
  Novelty: 0.71
  Knot count: 2
```

## Configuration

Environment variables:
- `OPENAI_API_KEY` — Required
- `OPENAI_BASE_URL` — API endpoint (default: OpenAI)
- `OPENAI_MODEL` — Model to use (default: gpt-4o)

Edit `config.py` for fine-tuning:
- Temperature settings
- Artifact counts
- Tension thresholds
- Cycle limits

## File Structure

```
oscillate                  # CLI wrapper (uses .venv)
run.py                     # Entry point
orchestrator.py            # Main loop
divergent_generator.py     # Chaos module
convergent_critic.py       # Structure module
tension_controller.py      # Balance metrics
memory_manager.py          # Persistence layer
config.py                  # Settings
prompts/
  dg_prompt.txt            # Divergent system prompt
  cc_prompt.txt            # Convergent system prompt
```

## MCP Server

Run as an MCP server for AI agent integration:

```bash
./mcp-serve
```

### Claude Desktop Configuration

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "oscillating-cognition": {
      "command": "/path/to/oscillating-cognition/mcp-serve",
      "env": {
        "OPENAI_API_KEY": "your-key"
      }
    }
  }
}
```

### Available Tools

| Tool | Description |
|------|-------------|
| `oscillate` | Run N cycles on a seed topic. Returns insights and open questions. |
| `get_insights` | Retrieve crystallized models from memory. |
| `get_open_questions` | Retrieve unresolved tensions and paradoxes. |
| `continue_thinking` | Add more cycles without a new seed. |
| `reset_cognition` | Clear memory and start fresh. |

### Agent Usage Example

```
Agent receives complex question
    ↓
Calls oscillate(seed="the question", cycles=3)
    ↓
Reviews insights + open_questions
    ↓
Formulates response with both answers AND unresolved tensions
```

## Roadmap

- [x] MCP server for agent integration
- [ ] Web UI for exploring memory
- [ ] Embedding-based novelty scoring
- [ ] Multi-model support (different models for DG vs CC)

## Philosophy

> Intelligence may not be structure. Intelligence may not be chaos.
> It may be sustained oscillation between incompatible regimes.

This is an experiment. It might be a dead end. But there's something worth exploring in systems that help you *think* rather than just *answer*.

## License

MIT

## Contributing

This is an early prototype. Issues, ideas, and PRs welcome.
