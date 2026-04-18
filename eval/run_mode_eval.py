#!/usr/bin/env python3
"""
Mode-aware A/B Evaluation: Oscillating Cognition vs. Iterative Baseline
across use-case-specific grounding modes (essay, strategy, hypotheses, provocations).

Each mode has its own seeds, grounding prompt, and judge criteria.

Usage:
    python eval/run_mode_eval.py                              # All modes, all seeds
    python eval/run_mode_eval.py --modes essay,strategy       # Specific modes only
    python eval/run_mode_eval.py --judges 3                   # 3 judges per seed
    python eval/run_mode_eval.py --model gpt-4o               # Override model
    python eval/run_mode_eval.py --resume mode_results_*.json # Resume from partial
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
from eval.judge_by_mode import judge_mode_blind, MODE_CRITERIA

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
SEEDS_FILE = os.path.join(EVAL_DIR, "seeds_by_mode.json")


def load_seeds_by_mode(seeds_file: str = None) -> dict:
    """Load mode-grouped seeds from JSON file."""
    if seeds_file is None:
        seeds_file = SEEDS_FILE
    with open(seeds_file) as f:
        return json.load(f)


def run_trial(mode: str, seed: dict, cycles: int, model: str = None) -> dict:
    """Run both conditions (oscillation + baseline) on a single seed with mode-specific grounding."""
    topic = seed["topic"]
    seed_id = seed["id"]

    logger.info(f"{'='*60}")
    logger.info(f"TRIAL [{mode}]: {seed_id} -- {topic[:60]}")
    logger.info(f"{'='*60}")

    trial = {
        "seed": topic,
        "seed_id": seed_id,
        "mode": mode,
    }

    # Condition A: Oscillation (N cycles) + mode-specific grounding
    logger.info(f"[A] Running oscillation ({cycles} cycles) + {mode} grounding...")
    t0 = time.time()
    try:
        osc_result = run_oscillation(
            topic, cycles=cycles, model=model, grounding_mode=mode
        )
        trial["oscillation"] = osc_result
        trial["oscillation_time"] = round(time.time() - t0, 1)
        logger.info(f"[A] Done in {trial['oscillation_time']}s")
    except Exception as e:
        logger.error(f"[A] Oscillation failed: {e}")
        trial["oscillation"] = {"error": str(e), "final": {}}
        trial["oscillation_time"] = round(time.time() - t0, 1)

    # Condition B: Baseline (3 passes) + same mode-specific grounding
    logger.info(f"[B] Running baseline (3 passes) + {mode} grounding...")
    t0 = time.time()
    try:
        base_result = run_baseline(
            topic, model=model, grounding_mode=mode
        )
        trial["baseline"] = base_result
        trial["baseline_time"] = round(time.time() - t0, 1)
        logger.info(f"[B] Done in {trial['baseline_time']}s")
    except Exception as e:
        logger.error(f"[B] Baseline failed: {e}")
        trial["baseline"] = {"error": str(e), "final": {}}
        trial["baseline_time"] = round(time.time() - t0, 1)

    return trial


def judge_trial(mode: str, trial: dict, num_judges: int, model: str = None) -> list[dict]:
    """Run N mode-specific blind judges on a completed trial."""
    seed = trial["seed"]
    osc_final = trial.get("oscillation", {}).get("final", {})
    base_final = trial.get("baseline", {}).get("final", {})

    judgments = []
    for i in range(num_judges):
        logger.info(f"[JUDGE {i+1}/{num_judges}] Evaluating {trial['seed_id']} ({mode} criteria)...")
        try:
            j = judge_mode_blind(mode, seed, osc_final, base_final, model=model)
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


def compute_mode_statistics(results: dict) -> dict:
    """Compute per-mode and aggregate statistics from mode eval results."""
    from collections import defaultdict
    import math

    all_stats = {}

    for mode, mode_data in results.get("modes", {}).items():
        criteria = MODE_CRITERIA.get(mode, [])
        method_scores = defaultdict(lambda: defaultdict(list))
        preferences = defaultdict(int)

        for seed_id, seed_data in mode_data.get("trials", {}).items():
            for judgment in seed_data.get("judgments", []):
                if "scores_by_method" in judgment:
                    for method, scores in judgment["scores_by_method"].items():
                        for criterion, score in scores.items():
                            if criterion in criteria:
                                method_scores[method][criterion].append(score)
                    pref = judgment.get("preferred_method", "tie")
                    preferences[pref] += 1

        total_judgments = sum(preferences.values())
        mode_stats = {"total_judgments": total_judgments, "criteria": criteria}

        # Scores per method per criterion
        for method in ["oscillation", "baseline"]:
            mode_stats[method] = {}
            all_scores = []
            for criterion in criteria:
                scores = method_scores[method].get(criterion, [])
                if scores:
                    mean = sum(scores) / len(scores)
                    variance = sum((s - mean) ** 2 for s in scores) / len(scores) if len(scores) > 1 else 0
                    mode_stats[method][criterion] = {
                        "mean": round(mean, 2),
                        "std": round(math.sqrt(variance), 2),
                        "n": len(scores)
                    }
                    all_scores.extend(scores)
            if all_scores:
                mode_stats[method]["overall"] = {
                    "mean": round(sum(all_scores) / len(all_scores), 2),
                    "n": len(all_scores)
                }

        # Win rate
        mode_stats["win_rate"] = {}
        for method in ["oscillation", "baseline", "tie"]:
            count = preferences.get(method, 0)
            mode_stats["win_rate"][method] = {
                "count": count,
                "rate": round(count / total_judgments, 2) if total_judgments > 0 else 0
            }

        # Deltas
        mode_stats["deltas"] = {}
        for criterion in criteria:
            osc_mean = mode_stats.get("oscillation", {}).get(criterion, {}).get("mean", 0)
            base_mean = mode_stats.get("baseline", {}).get(criterion, {}).get("mean", 0)
            mode_stats["deltas"][criterion] = round(osc_mean - base_mean, 2)

        all_stats[mode] = mode_stats

    # Aggregate across modes
    total_judgments = sum(s["total_judgments"] for s in all_stats.values())
    agg_prefs = defaultdict(int)
    agg_osc_scores = []
    agg_base_scores = []
    for mode_stats in all_stats.values():
        for method in ["oscillation", "baseline", "tie"]:
            agg_prefs[method] += mode_stats["win_rate"].get(method, {}).get("count", 0)
        osc_overall = mode_stats.get("oscillation", {}).get("overall", {})
        base_overall = mode_stats.get("baseline", {}).get("overall", {})
        if osc_overall.get("mean") is not None:
            agg_osc_scores.append(osc_overall["mean"])
        if base_overall.get("mean") is not None:
            agg_base_scores.append(base_overall["mean"])

    all_stats["_aggregate"] = {
        "total_judgments": total_judgments,
        "win_rate": {
            method: {
                "count": agg_prefs[method],
                "rate": round(agg_prefs[method] / total_judgments, 2) if total_judgments > 0 else 0
            }
            for method in ["oscillation", "baseline", "tie"]
        },
        "oscillation_mean": round(sum(agg_osc_scores) / len(agg_osc_scores), 2) if agg_osc_scores else None,
        "baseline_mean": round(sum(agg_base_scores) / len(agg_base_scores), 2) if agg_base_scores else None,
    }

    return all_stats


def print_summary(stats: dict):
    """Print a compact summary of mode eval results."""
    print(f"\n{'='*60}")
    print("MODE EVALUATION COMPLETE")
    print(f"{'='*60}")

    agg = stats.get("_aggregate", {})
    print(f"Total judgments: {agg.get('total_judgments', 0)}")
    wr = agg.get("win_rate", {})
    osc_rate = wr.get("oscillation", {}).get("rate", 0)
    base_rate = wr.get("baseline", {}).get("rate", 0)
    tie_rate = wr.get("tie", {}).get("rate", 0)
    print(f"Overall: Oscillation={osc_rate:.0%} | Baseline={base_rate:.0%} | Tie={tie_rate:.0%}")
    print(f"Mean scores: Oscillation={agg.get('oscillation_mean', '?')} | Baseline={agg.get('baseline_mean', '?')}")
    print()

    for mode in sorted(k for k in stats if not k.startswith("_")):
        ms = stats[mode]
        wr = ms.get("win_rate", {})
        osc_rate = wr.get("oscillation", {}).get("rate", 0)
        base_rate = wr.get("baseline", {}).get("rate", 0)
        osc_mean = ms.get("oscillation", {}).get("overall", {}).get("mean", "?")
        base_mean = ms.get("baseline", {}).get("overall", {}).get("mean", "?")
        print(f"  {mode:15s} | Osc={osc_rate:.0%} Base={base_rate:.0%} | "
              f"Scores: Osc={osc_mean} Base={base_mean}")

        # Per-criterion deltas
        for criterion, delta in ms.get("deltas", {}).items():
            sign = "+" if delta > 0 else ""
            print(f"    {criterion:30s} {sign}{delta}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Mode-aware A/B Evaluation: Oscillation vs Baseline")
    parser.add_argument("--modes", type=str, default=None,
                        help="Comma-separated list of modes to run (default: all)")
    parser.add_argument("--judges", type=int, default=2,
                        help="Number of blind judges per seed (default: 2)")
    parser.add_argument("--cycles", type=int, default=3,
                        help="Oscillation cycles (default: 3)")
    parser.add_argument("--model", type=str, default=None,
                        help="Model override (default: from config)")
    parser.add_argument("--judge-model", type=str, default=None,
                        help="Judge model override (default: same as --model)")
    parser.add_argument("--seeds-file", type=str, default=None,
                        help="Custom seeds-by-mode file")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file (default: eval/mode_results_<timestamp>.json)")
    parser.add_argument("--resume", type=str, default=None,
                        help="Resume from partial results file")
    args = parser.parse_args()

    judge_model = args.judge_model or args.model

    # Load seeds grouped by mode
    all_seeds = load_seeds_by_mode(args.seeds_file)

    # Filter modes if specified
    if args.modes:
        requested_modes = [m.strip() for m in args.modes.split(",")]
        for m in requested_modes:
            if m not in all_seeds:
                logger.error(f"Unknown mode '{m}'. Available: {list(all_seeds.keys())}")
                sys.exit(1)
        modes = requested_modes
    else:
        modes = list(all_seeds.keys())

    # Output file
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(EVAL_DIR, f"mode_results_{timestamp}.json")

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
                "modes": modes,
            },
            "modes": {}
        }

    # Count total work
    total_seeds = sum(len(all_seeds[m]) for m in modes)
    total_judgments = total_seeds * args.judges
    logger.info(f"Starting mode evaluation: {len(modes)} modes, {total_seeds} seeds, "
                f"{args.judges} judges = {total_judgments} judgments")
    logger.info(f"Modes: {', '.join(modes)}")
    logger.info(f"Output: {output_file}")

    total_start = time.time()

    for mode in modes:
        seeds = all_seeds[mode]
        logger.info(f"\n{'#'*60}")
        logger.info(f"MODE: {mode.upper()} ({len(seeds)} seeds)")
        logger.info(f"{'#'*60}")

        # Ensure mode entry exists in results
        if mode not in results["modes"]:
            results["modes"][mode] = {"trials": {}}

        mode_results = results["modes"][mode]

        for i, seed in enumerate(seeds):
            seed_id = seed["id"]

            # Skip if already completed
            existing = mode_results["trials"].get(seed_id, {})
            if existing.get("judgments") and len(existing["judgments"]) >= args.judges:
                logger.info(f"[{mode}/{i+1}/{len(seeds)}] Skipping {seed_id} (already completed)")
                continue

            logger.info(f"\n[{mode}/{i+1}/{len(seeds)}] Processing {seed_id}...")

            # Run trial (both conditions)
            if not existing.get("oscillation") or not existing.get("baseline"):
                trial = run_trial(mode, seed, cycles=args.cycles, model=args.model)
            else:
                trial = existing
                logger.info(f"Using cached trial data for {seed_id}")

            # Run mode-specific judges
            judgments = judge_trial(mode, trial, num_judges=args.judges, model=judge_model)
            trial["judgments"] = judgments

            # Store (trimmed for manageability)
            mode_results["trials"][seed_id] = {
                "seed": trial["seed"],
                "mode": mode,
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

    # Compute statistics
    stats = compute_mode_statistics(results)
    stats_file = output_file.replace(".json", "_stats.json")
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)

    # Print summary
    print_summary(stats)
    print(f"\nResults:  {output_file}")
    print(f"Stats:    {stats_file}")


if __name__ == "__main__":
    main()
