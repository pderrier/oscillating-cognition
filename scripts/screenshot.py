#!/usr/bin/env python3
"""Take a screenshot of the Web UI with demo data."""
import json
import os
import sys
import time
import subprocess
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import BASE_DIR, MEMORY_DIR, CRYSTALLIZED_FILE, OPEN_KNOTS_FILE

# Demo data
DEMO_CRYSTALLIZED = [
    {"content": "Meta-criterion: treat comfort, logging, and branching as manipulable surfaces. Any discriminator can be co-opted into theater.", "cycle_added": 1},
    {"content": "Rail-yard epistemics: crystallized memory = sealed freight (portable commitments); open knots = leaking cars (uncertainty as cross-contaminant).", "cycle_added": 2},
    {"content": "Closure-as-performance model: the UI can function like a theatrical announcer that produces the felt sense of arrival independent of actual progress.", "cycle_added": 3},
]

DEMO_KNOTS = [
    {"content": "When is UI-induced closure a necessary usability affordance versus a harmful illusion that collapses inquiry?", "cycle_added": 1},
    {"content": "If the infection is framed as 'the only honest thing', does that invert the moral valence of stability itself?", "cycle_added": 2},
    {"content": "How can a system expose unresolved reality without turning every interaction into anxiety-inducing ambiguity?", "cycle_added": 3},
    {"content": "The courtroom inversion makes the criterion the defendant, but the judge is still an internal tremor: is this genuinely adversarial?", "cycle_added": 4},
]


def setup_demo_data():
    """Write demo data to memory files."""
    os.makedirs(MEMORY_DIR, exist_ok=True)

    with open(CRYSTALLIZED_FILE, 'w') as f:
        json.dump(DEMO_CRYSTALLIZED, f, indent=2)

    with open(OPEN_KNOTS_FILE, 'w') as f:
        json.dump(DEMO_KNOTS, f, indent=2)

    print("Demo data written")


def take_screenshot():
    """Take screenshot using playwright."""
    from playwright.sync_api import sync_playwright

    output_path = BASE_DIR / "assets" / "screenshot.png"
    output_path.parent.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        # Navigate to local server
        page.goto("http://localhost:8080")

        # Wait for data to load
        page.wait_for_selector("#crystallized-count:not(:has-text('-'))", timeout=5000)
        time.sleep(0.5)  # Extra time for rendering

        # Take screenshot
        page.screenshot(path=str(output_path), full_page=False)
        browser.close()

    print(f"Screenshot saved to {output_path}")
    return output_path


def main():
    setup_demo_data()

    # Start server
    print("Starting server...")
    server = subprocess.Popen(
        [str(BASE_DIR / ".venv/bin/uvicorn"), "web_server:app", "--host", "127.0.0.1", "--port", "8080"],
        cwd=str(BASE_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        # Wait for server to start
        time.sleep(2)

        # Take screenshot
        screenshot_path = take_screenshot()
        print(f"Success! Screenshot at: {screenshot_path}")

    finally:
        server.terminate()
        server.wait()
        print("Server stopped")


if __name__ == "__main__":
    main()
