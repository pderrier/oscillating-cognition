#!/usr/bin/env python3
"""
Oscillating Cognition - Entry Point

A cognitive orchestration system that simulates oscillation between
divergent generation (chaos) and convergent structuring (compression).

Usage:
    python run.py [options]

Options:
    --seed TOPIC       Initial seed topic to explore
    --cycles N         Maximum number of cycles (default: 10)
    --reset            Clear all memory before starting
"""

import argparse
import os
import sys
import shutil

from config import OPENAI_API_KEY, MEMORY_DIR, SCRATCH_DIR


def check_environment():
    """Verify environment is configured correctly."""
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)


def reset_memory():
    """Clear all memory directories."""
    for directory in [MEMORY_DIR, SCRATCH_DIR]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Cleared {directory}/")


def main():
    parser = argparse.ArgumentParser(
        description="Oscillating Cognition - Chaos-Structure Cognitive System"
    )
    parser.add_argument(
        "--seed", "-s",
        type=str,
        default=None,
        help="Initial seed topic to explore"
    )
    parser.add_argument(
        "--cycles", "-c",
        type=int,
        default=None,
        help="Maximum number of cycles"
    )
    parser.add_argument(
        "--reset", "-r",
        action="store_true",
        help="Clear all memory before starting"
    )

    args = parser.parse_args()

    # Check environment
    check_environment()

    # Reset if requested
    if args.reset:
        reset_memory()

    # Import here to avoid import errors if config is wrong
    from orchestrator import Orchestrator

    # Create and run orchestrator
    orchestrator = Orchestrator(
        seed_topic=args.seed,
        max_cycles=args.cycles
    )

    try:
        summary = orchestrator.run()
        print("\n[DONE] Oscillation complete")
        return 0
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Run terminated by user")
        return 1
    except Exception as e:
        print(f"\n[FATAL] {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
