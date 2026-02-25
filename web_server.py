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
from memory_manager import load_crystallized, load_open_knots, get_knot_count

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
    from memory_manager import initialize_memory
    initialize_memory()

    return {"status": "Memory cleared"}


def main():
    """Run the web server."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
