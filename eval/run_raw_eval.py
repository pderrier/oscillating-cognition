#!/usr/bin/env python3
"""
Re-run generations only (no grounding), save raw upstream outputs for judging.

Oscillation raw = crystallized insights + open knots
Baseline raw = pass 3 final_ideas + open_questions + synthesis
"""
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eval.baseline import run_baseline
from eval.oscillation_runner import run_oscillation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)


def load_seeds():
    with open(os.path.join(os.path.dirname(__file__), "seeds.json")) as f:
        return json.load(f)["seeds"]


def extract_raw_oscillation(result: dict) -> dict:
    """Extract pre-grounding output from oscillation."""
    return {
        "insights": [c["content"] for c in result.get("crystallized", [])],
        "open_knots": [k["content"] for k in result.get("open_knots", [])],
        "synthesis": "",  # no synthesis pre-grounding
    }


def extract_raw_baseline(result: dict) -> dict:
    """Extract pre-grounding output from baseline (pass 3)."""
    pass3 = None
    for p in result.get("passes", []):
        if p.get("pass") == 3:
            pass3 = p.get("output", {})
            break
    if not pass3:
        return {"insights": [], "open_knots": [], "synthesis": ""}

    return {
        "insights": [
            i.get("content", str(i)) if isinstance(i, dict) else str(i)
            for i in pass3.get("final_ideas", [])
        ],
        "open_knots": pass3.get("open_questions", []),
        "synthesis": pass3.get("synthesis", ""),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=None)
    parser.add_argument("--cycles", type=int, default=3)
    parser.add_argument("--resume", type=str, default=None)
    args = parser.parse_args()

    seeds = load_seeds()
    if args.seeds:
        seeds = seeds[:args.seeds]

    output_file = args.resume or os.path.join(
        os.path.dirname(__file__),
        f"raw_results_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    )

    if args.resume and os.path.exists(args.resume):
        with open(args.resume) as f:
            results = json.load(f)
    else:
        results = {"config": {"cycles": args.cycles}, "trials": {}}

    for i, seed in enumerate(seeds):
        sid = seed["id"]
        if sid in results["trials"]:
            logger.info(f"[{i+1}/{len(seeds)}] Skipping {sid} (cached)")
            continue

        topic = seed["topic"]
        logger.info(f"[{i+1}/{len(seeds)}] {sid}: {topic[:60]}")

        # Oscillation
        logger.info(f"  [A] Oscillation ({args.cycles} cycles)...")
        t0 = time.time()
        try:
            osc = run_oscillation(topic, cycles=args.cycles, skip_grounding=True)
            osc_raw = extract_raw_oscillation(osc)
            osc_time = round(time.time() - t0, 1)
        except Exception as e:
            logger.error(f"  [A] Failed: {e}")
            osc_raw = {"insights": [], "open_knots": [], "synthesis": ""}
            osc_time = round(time.time() - t0, 1)

        # Baseline
        logger.info(f"  [B] Baseline (3 passes)...")
        t0 = time.time()
        try:
            base = run_baseline(topic, skip_grounding=True)
            base_raw = extract_raw_baseline(base)
            base_time = round(time.time() - t0, 1)
        except Exception as e:
            logger.error(f"  [B] Failed: {e}")
            base_raw = {"insights": [], "open_knots": [], "synthesis": ""}
            base_time = round(time.time() - t0, 1)

        results["trials"][sid] = {
            "seed": topic,
            "domain": seed.get("domain", ""),
            "oscillation_raw": osc_raw,
            "baseline_raw": base_raw,
            "oscillation_time": osc_time,
            "baseline_time": base_time,
        }

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"  Saved to {output_file}")

    print(f"\nDone. Raw results: {output_file}")


if __name__ == "__main__":
    main()
