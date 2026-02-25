#!/usr/bin/env python3
"""
Web UI for exploring oscillating cognition memory.

Run with: ./web-serve or python web_server.py
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from config import BASE_DIR, MEMORY_DIR, CRYSTALLIZED_FILE, OPEN_KNOTS_FILE
from memory_manager import (
    load_crystallized, load_open_knots, get_knot_count, initialize_memory,
    append_crystallized, add_open_knots, build_context
)

app = FastAPI(
    title="Oscillating Cognition",
    description="Memory explorer for the oscillating cognition system",
    version="0.1.0"
)

# Static files
STATIC_DIR = BASE_DIR / "web" / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class MemoryStats(BaseModel):
    crystallized_count: int
    open_knots_count: int
    memory_dir: str
    last_modified: Optional[str] = None


class InsightItem(BaseModel):
    content: str
    cycle_added: int
    index: int


class KnotItem(BaseModel):
    content: str
    cycle_added: int
    index: int


class OscillateRequest(BaseModel):
    seed: str
    cycles: int = 3
    ground: bool = False


class CycleResult(BaseModel):
    cycle: int
    artifacts_generated: int
    artifacts_selected: int
    new_models: list[str]
    new_knots: list[str]
    silence: bool


class OscillateResponse(BaseModel):
    cycles_completed: int
    insights: list[str]
    open_questions: list[str]
    final_knot_count: int
    grounding: Optional[dict] = None


# Global state for oscillation
oscillation_state = {
    "running": False,
    "current_cycle": 0,
    "total_cycles": 0,
    "seed": None
}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main UI."""
    index_path = BASE_DIR / "web" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse(content="""
    <html>
        <head><title>Oscillating Cognition</title></head>
        <body>
            <h1>Oscillating Cognition</h1>
            <p>Web UI not found. Run from project directory.</p>
            <p>API endpoints available at /api/</p>
        </body>
    </html>
    """)


@app.get("/api/status", response_model=MemoryStats)
async def get_status():
    """Get current memory status."""
    last_mod = None
    if os.path.exists(CRYSTALLIZED_FILE):
        mtime = os.path.getmtime(CRYSTALLIZED_FILE)
        last_mod = datetime.fromtimestamp(mtime).isoformat()

    return MemoryStats(
        crystallized_count=len(load_crystallized()),
        open_knots_count=get_knot_count(),
        memory_dir=MEMORY_DIR,
        last_modified=last_mod
    )


@app.get("/api/insights", response_model=list[InsightItem])
async def get_insights(limit: Optional[int] = None, offset: int = 0):
    """Get crystallized insights."""
    crystallized = load_crystallized()

    # Apply offset
    if offset > 0:
        crystallized = crystallized[offset:]

    # Apply limit
    if limit:
        crystallized = crystallized[:limit]

    return [
        InsightItem(
            content=item.get("content", str(item)),
            cycle_added=item.get("cycle_added", 0),
            index=offset + i
        )
        for i, item in enumerate(crystallized)
    ]


@app.get("/api/knots", response_model=list[KnotItem])
async def get_knots(limit: Optional[int] = None, offset: int = 0):
    """Get open knots (unresolved tensions)."""
    knots = load_open_knots()

    if offset > 0:
        knots = knots[offset:]

    if limit:
        knots = knots[:limit]

    return [
        KnotItem(
            content=item.get("content", str(item)),
            cycle_added=item.get("cycle_added", 0),
            index=offset + i
        )
        for i, item in enumerate(knots)
    ]


@app.get("/api/memory/raw")
async def get_raw_memory():
    """Get raw memory files for debugging."""
    return {
        "crystallized": load_crystallized(),
        "open_knots": load_open_knots()
    }


@app.delete("/api/memory")
async def clear_memory():
    """Clear all memory (use with caution)."""
    import shutil
    from config import SCRATCH_DIR

    for directory in [MEMORY_DIR, SCRATCH_DIR]:
        if os.path.exists(directory):
            shutil.rmtree(directory)

    # Reinitialize
    initialize_memory()

    return {"status": "Memory cleared"}


@app.get("/api/oscillation/status")
async def get_oscillation_status():
    """Get current oscillation status."""
    return oscillation_state


def _run_oscillation_sync(seed: str, cycles: int, do_grounding: bool) -> dict:
    """Run oscillation synchronously (called from thread pool)."""
    global oscillation_state

    # Import here to avoid circular imports
    from divergent_generator import generate as dg_generate
    from convergent_critic import critique as cc_critique
    from tension_controller import TensionController
    from grounding import ground as do_ground

    initialize_memory()

    tc = TensionController()
    history_texts = []
    probe_directions = []

    results = []
    all_models = []
    all_knots = []

    for i in range(cycles):
        oscillation_state["current_cycle"] = i + 1

        # Build context
        context = build_context()
        if i == 0 and seed:
            context["seed_topic"] = seed
        if probe_directions:
            context["probe_directions"] = probe_directions

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
                all_models.extend(compressed)
            if new_knots:
                add_open_knots(new_knots)
                all_knots.extend(new_knots)

        # Update metrics
        raw_text = " ".join(a.get("content", "") for a in artifacts)
        history_texts.append(raw_text)

        metrics = tc.compute_metrics({
            "raw_artifacts": artifacts,
            "compressed_models": compressed,
            "history": history_texts
        })
        tc.get_adjustments(metrics)

        results.append({
            "cycle": i + 1,
            "artifacts_generated": len(artifacts),
            "artifacts_selected": len(selected),
            "new_models": compressed,
            "new_knots": new_knots,
            "silence": no_add
        })

        # Check for diminishing returns
        if tc.detect_diminishing_returns():
            break

    response = {
        "cycles_completed": len(results),
        "insights": all_models,
        "open_questions": all_knots,
        "final_knot_count": get_knot_count(),
        "grounding": None
    }

    # Optional grounding phase
    if do_grounding and (all_models or all_knots):
        import time
        time.sleep(1)  # Small delay to avoid API rate limits
        try:
            crystallized = load_crystallized()
            knots = load_open_knots()
            grounding_result = do_ground(seed, crystallized, knots)
            response["grounding"] = grounding_result
        except Exception as e:
            response["grounding"] = {"error": str(e)}

    return response


@app.post("/api/oscillate", response_model=OscillateResponse)
async def run_oscillation(request: OscillateRequest):
    """Run oscillation cycles on a seed topic."""
    global oscillation_state
    import asyncio
    import concurrent.futures

    if oscillation_state["running"]:
        raise HTTPException(status_code=409, detail="Oscillation already in progress")

    oscillation_state = {
        "running": True,
        "current_cycle": 0,
        "total_cycles": request.cycles,
        "seed": request.seed
    }

    try:
        # Run in thread pool to allow status polling
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool,
                _run_oscillation_sync,
                request.seed,
                request.cycles,
                request.ground
            )

        return OscillateResponse(**result)

    finally:
        oscillation_state = {
            "running": False,
            "current_cycle": 0,
            "total_cycles": 0,
            "seed": None
        }


def main():
    """Run the web server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
