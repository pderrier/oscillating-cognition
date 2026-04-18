#!/usr/bin/env python3
"""
A/B Evaluation: Oscillating Cognition vs. Iterative Baseline

Rigorous protocol:
  - Equal effort (3 cycles/passes per condition)
  - Blind judging (randomized X/Y assignment)
  - External domains (no self-referential seeds)
  - Multiple judges per seed for reliability
  - Statistical reporting

Usage:
    python eval/run_eval.py                          # Run all 10 seeds, 2 judges each
    python eval/run_eval.py --seeds 3                # First 3 seeds only
    python eval/run_eval.py --seeds 3 --judges 1     # Quick test
    python eval/run_eval.py --cycles 5               # More oscillation cycles (baseline also gets 3 passes)
    python eval/run_eval.py --model gpt-4o           # Override model
    python eval/run_eval.py --resume results.json    # Resume from partial results
"""
import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eval.baseline import run_baseline
from eval.oscillation_runner import run_oscillation
from eval.judge import judge_blind
from eval.report import compute_statistics, format_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


def load_seeds(seeds_file: str = None) -> list[dict]:
    if seeds_file is None:
        seeds_file = os.path.join(os.path.dirname(__file__), "seeds.json")
    with open(seeds_file) as f:
        data = json.load(f)
    return data["seeds"]


def run_trial(seed: dict, cycles: int, model: str = None) -> dict:
    """Run both conditions on a single seed."""
    topic = seed["topic"]
    seed_id = seed["id"]

    logger.info(f"{'='*60}")
    logger.info(f"TRIAL: {seed_id} — {topic[:60]}")
    logger.info(f"{'='*60}")

    trial = {
        "seed": topic,
        "seed_id": seed_id,
        "domain": seed.get("domain", "unknown"),
    }

    # Condition A: Oscillation
    logger.info(f"[A] Running oscillation ({cycles} cycles)...")
    t0 = time.time()
    try:
        osc_result = run_oscillation(topic, cycles=cycles, model=model)
        trial["oscillation"] = osc_result
        trial["oscillation_time"] = round(time.time() - t0, 1)
        logger.info(f"[A] Done in {trial['oscillation_time']}s — "
                     f"{len(osc_result.get('final', {}).get('ideas', []))} insights, "
                     f"{len(osc_result.get('final', {}).get('open_questions', []))} knots")
    except Exception as e:
        logger.error(f"[A] Oscillation failed: {e}")
        trial["oscillation"] = {"error": str(e), "final": {"ideas": [], "open_questions": [], "synthesis": ""}}
        trial["oscillation_time"] = round(time.time() - t0, 1)

    # Condition B: Baseline (3-pass iterative)
    logger.info(f"[B] Running baseline (3 passes)...")
    t0 = time.time()
    try:
        base_result = run_baseline(topic, model=model)
        trial["baseline"] = base_result
        trial["baseline_time"] = round(time.time() - t0, 1)
        logger.info(f"[B] Done in {trial['baseline_time']}s — "
                     f"{len(base_result.get('final', {}).get('ideas', []))} ideas, "
                     f"{len(base_result.get('final', {}).get('open_questions', []))} questions")
    except Exception as e:
        logger.error(f"[B] Baseline failed: {e}")
        trial["baseline"] = {"error": str(e), "final": {"ideas": [], "open_questions": [], "synthesis": ""}}
        trial["baseline_time"] = round(time.time() - t0, 1)

    return trial


def judge_trial(trial: dict, num_judges: int, model: str = None) -> list[dict]:
    """Run N blind judges on a completed trial."""
    seed = trial["seed"]
    osc_final = trial.get("oscillation", {}).get("final", {})
    base_final = trial.get("baseline", {}).get("final", {})

    judgments = []
    for i in range(num_judges):
        logger.info(f"[JUDGE {i+1}/{num_judges}] Evaluating {trial['seed_id']}...")
        try:
            j = judge_blind(seed, osc_final, base_final, model=model)
            judgments.append(j)
            pref = j.get("preferred_method", "?")
            logger.info(f"[JUDGE {i+1}] Preferred: {pref}")
        except Exception as e:
            logger.error(f"[JUDGE {i+1}] Failed: {e}")
            judgments.append({"error": str(e)})

    return judgments


def save_results(results: dict, output_file: str):
    """Save results incrementally."""
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="A/B Evaluation: Oscillation vs Baseline")
    parser.add_argument("--seeds", type=int, default=None, help="Number of seeds to test (default: all)")
    parser.add_argument("--judges", type=int, default=2, help="Number of blind judges per seed (default: 2)")
    parser.add_argument("--cycles", type=int, default=3, help="Oscillation cycles (default: 3)")
    parser.add_argument("--model", type=str, default=None, help="Model override (default: from config)")
    parser.add_argument("--judge-model", type=str, default=None, help="Judge model override (default: same as --model)")
    parser.add_argument("--seeds-file", type=str, default=None, help="Custom seeds file")
    parser.add_argument("--output", type=str, default=None, help="Output file (default: eval/results_<timestamp>.json)")
    parser.add_argument("--resume", type=str, default=None, help="Resume from partial results file")
    args = parser.parse_args()

    judge_model = args.judge_model or args.model

    # Load seeds
    seeds = load_seeds(args.seeds_file)
    if args.seeds:
        seeds = seeds[:args.seeds]

    # Output file
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(os.path.dirname(__file__), f"results_{timestamp}.json")

    # Initialize or resume results
    if args.resume and os.path.exists(args.resume):
        with open(args.resume) as f:
            results = json.load(f)
        output_file = args.resume
        logger.info(f"Resuming from {args.resume}")
    else:
        results = {
            "config": {
                "cycles": args.cycles,
                "judges_per_seed": args.judges,
                "model": args.model or "default (config.py)",
                "judge_model": judge_model or "same as generation",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_seeds": len(seeds),
            },
            "trials": {}
        }

    logger.info(f"Starting evaluation: {len(seeds)} seeds × {args.judges} judges = {len(seeds) * args.judges} judgments")
    logger.info(f"Output: {output_file}")

    total_start = time.time()

    for i, seed in enumerate(seeds):
        seed_id = seed["id"]

        # Skip if already completed
        existing = results["trials"].get(seed_id, {})
        if existing.get("judgments") and len(existing["judgments"]) >= args.judges:
            logger.info(f"[{i+1}/{len(seeds)}] Skipping {seed_id} (already completed)")
            continue

        logger.info(f"\n[{i+1}/{len(seeds)}] Processing {seed_id}...")

        # Run trial (both conditions)
        if not existing.get("oscillation") or not existing.get("baseline"):
            trial = run_trial(seed, cycles=args.cycles, model=args.model)
        else:
            trial = existing
            logger.info(f"Using cached trial data for {seed_id}")

        # Run judges
        judgments = judge_trial(trial, num_judges=args.judges, model=judge_model)
        trial["judgments"] = judgments

        # Store (without the full intermediate data to keep file manageable)
        results["trials"][seed_id] = {
            "seed": trial["seed"],
            "domain": trial.get("domain", ""),
            "oscillation_time": trial.get("oscillation_time"),
            "baseline_time": trial.get("baseline_time"),
            "oscillation_final": trial.get("oscillation", {}).get("final", {}),
            "baseline_final": trial.get("baseline", {}).get("final", {}),
            "judgments": judgments,
        }

        # Save incrementally
        save_results(results, output_file)
        logger.info(f"Saved progress to {output_file}")

    total_time = round(time.time() - total_start, 1)
    results["config"]["total_time_seconds"] = total_time

    # Final save
    save_results(results, output_file)

    # Generate report
    stats = compute_statistics(results)
    report = format_report(results, stats)
    report_file = output_file.replace(".json", "_report.md")
    with open(report_file, "w") as f:
        f.write(report)

    stats_file = output_file.replace(".json", "_stats.json")
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)

    # Print summary
    print(f"\n{'='*60}")
    print(f"EVALUATION COMPLETE")
    print(f"{'='*60}")
    print(f"Time: {total_time}s")
    print(f"Seeds: {len(seeds)} | Judgments: {stats['total_judgments']}")

    wr = stats.get("win_rate", {})
    osc_wins = wr.get("oscillation", {}).get("rate", 0)
    base_wins = wr.get("baseline", {}).get("rate", 0)
    ties = wr.get("tie", {}).get("rate", 0)
    print(f"Win rate: Oscillation={osc_wins:.0%} | Baseline={base_wins:.0%} | Tie={ties:.0%}")

    ms = stats.get("method_stats", {})
    osc_avg = ms.get("oscillation", {}).get("overall", {}).get("mean", "?")
    base_avg = ms.get("baseline", {}).get("overall", {}).get("mean", "?")
    print(f"Mean score: Oscillation={osc_avg} | Baseline={base_avg}")

    print(f"\nResults:  {output_file}")
    print(f"Report:   {report_file}")
    print(f"Stats:    {stats_file}")


if __name__ == "__main__":
    main()
