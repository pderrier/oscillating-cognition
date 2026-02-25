import signal
import sys
from config import MAX_CYCLES
from memory_manager import (
    build_context, initialize_memory, write_scratch, clear_scratch,
    append_crystallized, add_open_knots, load_open_knots
)
from divergent_generator import generate as dg_generate
from convergent_critic import critique as cc_critique
from tension_controller import TensionController


class Orchestrator:
    """Main orchestration loop for the oscillating cognition system."""

    def __init__(self, seed_topic: str = None, max_cycles: int = None):
        self.seed_topic = seed_topic
        self.max_cycles = max_cycles or MAX_CYCLES
        self.tc = TensionController()
        self.cycle = 0
        self.running = True
        self.history_texts = []
        self.probe_directions = []

        # Handle graceful shutdown
        signal.signal(signal.SIGINT, self._handle_interrupt)

    def _handle_interrupt(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print("\n[INTERRUPT] Graceful shutdown initiated...")
        self.running = False

    def run(self) -> dict:
        """
        Execute the main oscillation loop.

        Returns:
            Summary dict with final state
        """
        print(f"[ORCHESTRATOR] Starting oscillation (max {self.max_cycles} cycles)")
        initialize_memory()

        while self.running and self.cycle < self.max_cycles:
            self.cycle += 1
            print(f"\n{'='*60}")
            print(f"[CYCLE {self.cycle}]")
            print('='*60)

            try:
                cycle_result = self._run_cycle()

                if cycle_result.get("no_add"):
                    print("[SILENCE] System chose intentional silence")

                # Check for diminishing returns
                if self.tc.detect_diminishing_returns():
                    print("[TERMINATION] Diminishing returns detected")
                    break

            except Exception as e:
                print(f"[ERROR] Cycle failed: {e}")
                if self.cycle >= 3:  # Allow some retries early
                    raise

        return self._generate_summary()

    def _run_cycle(self) -> dict:
        """Execute a single oscillation cycle."""
        # Build context
        context = build_context()
        if self.cycle == 1 and self.seed_topic:
            context["seed_topic"] = self.seed_topic
        if self.probe_directions:
            context["probe_directions"] = self.probe_directions

        # Get current adjustments
        tc_state = self.tc.get_state()
        temperature = tc_state["current_temperature"]

        # Phase 1: Divergent Generation
        print(f"\n[DG] Generating artifacts (temp={temperature:.2f})...")
        artifacts = dg_generate(context, temperature=temperature)
        print(f"[DG] Generated {len(artifacts)} artifacts")

        for i, artifact in enumerate(artifacts):
            print(f"  {i+1}. [{artifact.get('type', '?')}] {artifact.get('content', '')[:60]}...")

        # Write to scratch
        write_scratch({
            "cycle": self.cycle,
            "artifacts": artifacts,
            "temperature": temperature
        })

        # Phase 2: Convergent Critique
        print(f"\n[CC] Critiquing artifacts...")
        critique_result = cc_critique(artifacts, context)

        selected = critique_result.get("selected", [])
        rejected = critique_result.get("rejected", [])
        compressed = critique_result.get("compressed_models", [])
        new_knots = critique_result.get("new_open_knots", [])
        self.probe_directions = critique_result.get("next_probe_directions", [])
        no_add = critique_result.get("no_add", False)

        print(f"[CC] Selected: {len(selected)}, Rejected: {len(rejected)}")
        print(f"[CC] Compressed models: {len(compressed)}")
        print(f"[CC] New open knots: {len(new_knots)}")

        if compressed:
            print("[CC] Models:")
            for model in compressed:
                print(f"  - {model[:80]}...")

        if new_knots:
            print("[CC] Knots:")
            for knot in new_knots:
                print(f"  - {knot[:80]}...")

        # Phase 3: Update Memory
        if not no_add:
            if compressed:
                append_crystallized(compressed)
            if new_knots:
                add_open_knots(new_knots)

        # Phase 4: Compute Metrics & Adjustments
        raw_text = " ".join(a.get("content", "") for a in artifacts)
        self.history_texts.append(raw_text)

        metrics = self.tc.compute_metrics({
            "raw_artifacts": artifacts,
            "compressed_models": compressed,
            "history": self.history_texts
        })

        adjustments = self.tc.get_adjustments(metrics)

        print(f"\n[TC] Metrics:")
        print(f"  - Compression: {metrics['compression_delta']:.2f}")
        print(f"  - Novelty: {metrics['novelty_score']:.2f}")
        print(f"  - Knot count: {metrics['knot_count']}")

        for rec in adjustments.get("recommendations", []):
            print(f"[TC] {rec}")

        if adjustments.get("forced_divergence"):
            print("[TC] FORCED DIVERGENCE triggered for next cycle")

        # Clear scratch for next cycle
        clear_scratch()

        return {
            "artifacts": artifacts,
            "critique": critique_result,
            "metrics": metrics,
            "adjustments": adjustments,
            "no_add": no_add
        }

    def _generate_summary(self) -> dict:
        """Generate final summary of the run."""
        context = build_context()

        summary = {
            "total_cycles": self.cycle,
            "crystallized_count": len(context["crystallized"]),
            "open_knots_count": len(context["open_knots"]),
            "final_temperature": self.tc.current_dg_temp,
            "novelty_history": self.tc.history
        }

        print(f"\n{'='*60}")
        print("[SUMMARY]")
        print('='*60)
        print(f"Total cycles: {summary['total_cycles']}")
        print(f"Crystallized models: {summary['crystallized_count']}")
        print(f"Open knots: {summary['open_knots_count']}")
        print(f"Final temperature: {summary['final_temperature']:.2f}")

        if context["crystallized"]:
            print("\nCrystallized Memory:")
            for item in context["crystallized"]:
                print(f"  - {item.get('content', str(item))[:80]}...")

        if context["open_knots"]:
            print("\nOpen Knots:")
            for knot in context["open_knots"]:
                print(f"  - {knot.get('content', str(knot))[:80]}...")

        return summary
