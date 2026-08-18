#!/usr/bin/env python3
"""
run_demo.py
-----------
One-command entry point for the CoastalVision AI demo.

What it does:
  1. Generates the DEMO / SYNTHETIC sample dataset (if missing).
  2. Runs the full data-processing pipeline (NDWI -> masks -> change
     detection -> areas -> risk -> stats.json + PNG outputs).
  3. Copies a safety-net copy of stats.json into demo/fallback/, so the
     dashboard has something to show even if a live re-run fails during
     the actual presentation.
  4. Prints the exact command to start the frontend.

Usage:
    python run_demo.py
"""

from __future__ import annotations

import os
import shutil
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO_ROOT, "data-processing"))


def main() -> None:
    from pipeline import run_pipeline
    from utils import OUTPUTS_DIR

    print("=" * 60)
    print("CoastalVision AI — Demo Setup")
    print("=" * 60)

    print("\n[1/3] Running data-processing pipeline (synthetic sample data)...")
    stats = run_pipeline()
    print("      stats.json written:")
    for k, v in stats.items():
        print(f"        {k}: {v}")

    print("\n[2/3] Refreshing offline fallback copy...")
    fallback_dir = os.path.join(REPO_ROOT, "demo", "fallback")
    os.makedirs(fallback_dir, exist_ok=True)
    for fname in os.listdir(OUTPUTS_DIR):
        shutil.copy2(os.path.join(OUTPUTS_DIR, fname), os.path.join(fallback_dir, fname))
    print(f"      Copied {len(os.listdir(OUTPUTS_DIR))} files to demo/fallback/")

    print("\n[3/3] Refreshing integration/sample_stats.json copy...")
    integration_dir = os.path.join(REPO_ROOT, "integration")
    os.makedirs(integration_dir, exist_ok=True)
    shutil.copy2(
        os.path.join(OUTPUTS_DIR, "stats.json"),
        os.path.join(integration_dir, "sample_stats.json"),
    )

    print("\n" + "=" * 60)
    print("Demo data is ready.")
    print("Start the frontend with:")
    print("    python3 -m http.server 8080")
    print("Then open:")
    print("    http://localhost:8080/frontend/public/index.html")
    print("    http://localhost:8080/frontend/public/report.html")
    print("    http://localhost:8080/integration/report.html  (standalone fallback report)")
    print("=" * 60)


if __name__ == "__main__":
    main()
