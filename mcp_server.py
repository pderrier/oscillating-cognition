#!/usr/bin/env python3
"""
Oscillating Cognition MCP Server

Exposes the oscillating cognition system as tools for AI agents.
"""

import json
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from memory_manager import (
    build_context, initialize_memory, load_crystallized, load_open_knots,
    append_crystallized, add_open_knots, get_knot_count
)
from divergent_generator import generate as dg_generate
from convergent_critic import critique as cc_critique
from tension_controller import TensionController

# Global state
tc = TensionController()
history_texts = []
probe_directions = []

app = Server("oscillating-cognition")


def run_cycle(seed_topic: str = None, temperature: float = None) -> dict:
    """Run a single oscillation cycle."""
    global history_texts, probe_directions

    context = build_context()
    if seed_topic:
        context["seed_topic"] = seed_topic
    if probe_directions:
        context["probe_directions"] = probe_directions

    if temperature is None:
        temperature = tc.current_dg_temp

    # Divergent Generation
    artifacts = dg_generate(context, temperature=temperature)

    # Convergent Critique
    critique_result = cc_critique(artifacts, context)

    selected = critique_result.get("selected", [])
    compressed = critique_result.get("compressed_models", [])
    new_knots = critique_result.get("new_open_knots", [])
    probe_directions = critique_result.get("next_probe_directions", [])
    no_add = critique_result.get("no_add", False)

    # Update memory
    if not no_add:
        if compressed:
            append_crystallized(compressed)
        if new_knots:
            add_open_knots(new_knots)

    # Update metrics
    raw_text = " ".join(a.get("content", "") for a in artifacts)
    history_texts.append(raw_text)

    metrics = tc.compute_metrics({
        "raw_artifacts": artifacts,
        "compressed_models": compressed,
        "history": history_texts
    })

    tc.get_adjustments(metrics)

    return {
        "artifacts_generated": len(artifacts),
        "artifacts_selected": len(selected),
        "new_models": compressed,
        "new_knots": new_knots,
        "silence": no_add,
        "metrics": metrics
    }


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="oscillate",
            description="Run oscillating cognition cycles on a topic. Generates divergent ideas, then compresses into insights while preserving unresolved tensions. Use this for deep exploration of complex topics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "seed": {
                        "type": "string",
                        "description": "The topic or question to explore"
                    },
                    "cycles": {
                        "type": "integer",
                        "description": "Number of oscillation cycles (default: 3)",
                        "default": 3
                    }
                },
                "required": ["seed"]
            }
        ),
        Tool(
            name="get_insights",
            description="Retrieve crystallized insights from previous oscillation cycles. These are compressed, validated models that emerged from the exploration.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of insights to return (default: all)"
                    }
                }
            }
        ),
        Tool(
            name="get_open_questions",
            description="Retrieve open knots - unresolved tensions, paradoxes, and contradictions that were deliberately preserved. These reveal blind spots and unexplored angles.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of questions to return (default: all)"
                    }
                }
            }
        ),
        Tool(
            name="continue_thinking",
            description="Continue oscillation on existing context without a new seed. Builds on previous crystallized memory and open knots.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cycles": {
                        "type": "integer",
                        "description": "Number of additional cycles (default: 2)",
                        "default": 2
                    }
                }
            }
        ),
        Tool(
            name="reset_cognition",
            description="Clear all memory and start fresh. Use when switching to an unrelated topic.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    global history_texts, probe_directions, tc

    if name == "oscillate":
        seed = arguments.get("seed")
        cycles = arguments.get("cycles", 3)

        initialize_memory()

        results = []
        for i in range(cycles):
            cycle_seed = seed if i == 0 else None
            result = run_cycle(seed_topic=cycle_seed)
            results.append(result)

            # Check for diminishing returns
            if tc.detect_diminishing_returns():
                break

        # Summary
        all_models = []
        all_knots = []
        for r in results:
            all_models.extend(r.get("new_models", []))
            all_knots.extend(r.get("new_knots", []))

        summary = {
            "cycles_completed": len(results),
            "insights": all_models,
            "open_questions": all_knots,
            "final_knot_count": get_knot_count()
        }

        return [TextContent(
            type="text",
            text=json.dumps(summary, indent=2, ensure_ascii=False)
        )]

    elif name == "get_insights":
        limit = arguments.get("limit")
        crystallized = load_crystallized()

        if limit:
            crystallized = crystallized[-limit:]

        insights = [item.get("content", str(item)) for item in crystallized]

        return [TextContent(
            type="text",
            text=json.dumps({"insights": insights}, indent=2, ensure_ascii=False)
        )]

    elif name == "get_open_questions":
        limit = arguments.get("limit")
        knots = load_open_knots()

        if limit:
            knots = knots[-limit:]

        questions = [item.get("content", str(item)) for item in knots]

        return [TextContent(
            type="text",
            text=json.dumps({"open_questions": questions}, indent=2, ensure_ascii=False)
        )]

    elif name == "continue_thinking":
        cycles = arguments.get("cycles", 2)

        results = []
        for _ in range(cycles):
            result = run_cycle()
            results.append(result)

            if tc.detect_diminishing_returns():
                break

        all_models = []
        all_knots = []
        for r in results:
            all_models.extend(r.get("new_models", []))
            all_knots.extend(r.get("new_knots", []))

        summary = {
            "cycles_completed": len(results),
            "new_insights": all_models,
            "new_questions": all_knots,
            "total_insights": len(load_crystallized()),
            "total_knots": get_knot_count()
        }

        return [TextContent(
            type="text",
            text=json.dumps(summary, indent=2, ensure_ascii=False)
        )]

    elif name == "reset_cognition":
        import shutil
        import os
        from config import MEMORY_DIR, SCRATCH_DIR

        for directory in [MEMORY_DIR, SCRATCH_DIR]:
            if os.path.exists(directory):
                shutil.rmtree(directory)

        # Reset global state
        tc = TensionController()
        history_texts = []
        probe_directions = []

        initialize_memory()

        return [TextContent(
            type="text",
            text=json.dumps({"status": "Memory cleared. Ready for new exploration."})
        )]

    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"})
        )]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
