"""
Statistical analysis and report generation from evaluation results.
"""
import json
import math
import sys
from collections import defaultdict
from pathlib import Path


CRITERIA = [
    "novelty", "depth", "specificity",
    "internal_tension", "emergent_insight", "human_likeness"
]


def load_results(results_file: str) -> dict:
    with open(results_file) as f:
        return json.load(f)


def compute_statistics(results: dict) -> dict:
    """Compute aggregate statistics from evaluation results."""
    all_judgments = []
    for seed_id, seed_data in results.get("trials", {}).items():
        for judgment in seed_data.get("judgments", []):
            if "scores_by_method" in judgment:
                all_judgments.append(judgment)

    if not all_judgments:
        return {"error": "No valid judgments found"}

    # Aggregate scores by method and criterion
    method_scores = defaultdict(lambda: defaultdict(list))
    preferences = defaultdict(int)

    for j in all_judgments:
        for method, scores in j.get("scores_by_method", {}).items():
            for criterion, score in scores.items():
                if criterion in CRITERIA:
                    method_scores[method][criterion].append(score)

        pref = j.get("preferred_method", "tie")
        preferences[pref] += 1

    # Compute means and std devs
    stats = {}
    for method in ["oscillation", "baseline"]:
        stats[method] = {}
        all_scores = []
        for criterion in CRITERIA:
            scores = method_scores[method].get(criterion, [])
            if scores:
                mean = sum(scores) / len(scores)
                variance = sum((s - mean) ** 2 for s in scores) / len(scores) if len(scores) > 1 else 0
                std = math.sqrt(variance)
                stats[method][criterion] = {
                    "mean": round(mean, 2),
                    "std": round(std, 2),
                    "n": len(scores)
                }
                all_scores.extend(scores)
        if all_scores:
            overall_mean = sum(all_scores) / len(all_scores)
            stats[method]["overall"] = {
                "mean": round(overall_mean, 2),
                "n": len(all_scores)
            }

    # Win rate
    total_judgments = sum(preferences.values())
    win_rate = {}
    for method in ["oscillation", "baseline", "tie"]:
        count = preferences.get(method, 0)
        win_rate[method] = {
            "count": count,
            "rate": round(count / total_judgments, 2) if total_judgments > 0 else 0
        }

    # Per-criterion comparison (delta = oscillation - baseline)
    deltas = {}
    for criterion in CRITERIA:
        osc_mean = stats.get("oscillation", {}).get(criterion, {}).get("mean", 0)
        base_mean = stats.get("baseline", {}).get(criterion, {}).get("mean", 0)
        deltas[criterion] = round(osc_mean - base_mean, 2)

    return {
        "total_judgments": total_judgments,
        "total_seeds": len(results.get("trials", {})),
        "method_stats": stats,
        "win_rate": win_rate,
        "deltas": deltas,
        "preferences_raw": dict(preferences)
    }


def format_report(results: dict, stats: dict) -> str:
    """Format a human-readable markdown report."""
    lines = []
    lines.append("# Oscillation vs Baseline — Evaluation Report")
    lines.append("")
    lines.append(f"**Model:** {results.get('config', {}).get('model', 'unknown')}")
    lines.append(f"**Cycles:** {results.get('config', {}).get('cycles', '?')}")
    lines.append(f"**Seeds tested:** {stats['total_seeds']}")
    lines.append(f"**Total judgments:** {stats['total_judgments']}")
    lines.append(f"**Judge model:** {results.get('config', {}).get('judge_model', 'same as generation')}")
    lines.append("")

    # Win rate
    lines.append("## Win Rate")
    lines.append("")
    wr = stats["win_rate"]
    lines.append(f"| Method | Wins | Rate |")
    lines.append(f"|--------|------|------|")
    for method in ["oscillation", "baseline", "tie"]:
        lines.append(f"| {method} | {wr[method]['count']} | {wr[method]['rate']:.0%} |")
    lines.append("")

    # Score comparison
    lines.append("## Scores by Criterion (mean)")
    lines.append("")
    lines.append("| Criterion | Oscillation | Baseline | Delta |")
    lines.append("|-----------|:-----------:|:--------:|:-----:|")
    ms = stats["method_stats"]
    for c in CRITERIA:
        osc = ms.get("oscillation", {}).get(c, {})
        base = ms.get("baseline", {}).get(c, {})
        delta = stats["deltas"].get(c, 0)
        sign = "+" if delta > 0 else ""
        lines.append(
            f"| {c.replace('_', ' ').title()} "
            f"| {osc.get('mean', '—')} (±{osc.get('std', '—')}) "
            f"| {base.get('mean', '—')} (±{base.get('std', '—')}) "
            f"| {sign}{delta} |"
        )

    # Overall
    osc_overall = ms.get("oscillation", {}).get("overall", {}).get("mean", "—")
    base_overall = ms.get("baseline", {}).get("overall", {}).get("mean", "—")
    if isinstance(osc_overall, (int, float)) and isinstance(base_overall, (int, float)):
        overall_delta = round(osc_overall - base_overall, 2)
        sign = "+" if overall_delta > 0 else ""
        lines.append(f"| **Overall** | **{osc_overall}** | **{base_overall}** | **{sign}{overall_delta}** |")
    lines.append("")

    # Per-seed details
    lines.append("## Per-Seed Results")
    lines.append("")
    for seed_id, seed_data in results.get("trials", {}).items():
        seed_topic = seed_data.get("seed", seed_id)
        lines.append(f"### {seed_id}")
        lines.append(f"*{seed_topic}*")
        lines.append("")
        for i, j in enumerate(seed_data.get("judgments", []), 1):
            pref = j.get("preferred_method", "?")
            qual = j.get("qualitative", "")
            lines.append(f"**Judge {i}:** preferred **{pref}**")
            if qual:
                lines.append(f"> {qual}")
            lines.append("")

    # Methodology notes
    lines.append("## Methodology")
    lines.append("")
    lines.append("- **Equal effort:** Both conditions use 3 iterative passes")
    lines.append("- **Blind judging:** Judge sees Output X / Output Y with randomized assignment")
    lines.append("- **Non-circular criteria:** No criterion references oscillation-specific vocabulary")
    lines.append("- **External domains:** All seeds are external to the oscillating-cognition project")
    lines.append("- **Position bias mitigation:** X/Y assignment is randomized per judgment")
    lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python report.py <results.json>")
        sys.exit(1)

    results_file = sys.argv[1]
    results = load_results(results_file)
    stats = compute_statistics(results)
    report = format_report(results, stats)

    # Write report
    report_file = results_file.replace(".json", "_report.md")
    with open(report_file, "w") as f:
        f.write(report)
    print(f"Report written to {report_file}")

    # Also write stats JSON
    stats_file = results_file.replace(".json", "_stats.json")
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"Stats written to {stats_file}")

    # Print summary
    print(f"\n{'='*50}")
    print(f"SUMMARY: {stats['total_seeds']} seeds, {stats['total_judgments']} judgments")
    wr = stats["win_rate"]
    print(f"Oscillation wins: {wr['oscillation']['rate']:.0%} | Baseline wins: {wr['baseline']['rate']:.0%} | Ties: {wr['tie']['rate']:.0%}")
    osc = stats["method_stats"].get("oscillation", {}).get("overall", {}).get("mean", "?")
    base = stats["method_stats"].get("baseline", {}).get("overall", {}).get("mean", "?")
    print(f"Mean scores: Oscillation={osc} | Baseline={base}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
