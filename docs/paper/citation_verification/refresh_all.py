#!/usr/bin/env python3
"""
refresh_all.py — One-shot orchestrator for the citation-verification pipeline.

Runs the full refresh chain whenever any citation data changes:

    1. fix_claim_extraction.py
         Re-extract claim_in_paper_corrected per \\citep in main.tex.
         Catches cases where the paper text changed (sentence moved, cite
         added / removed).

    2. sync_citation_flags.py
         Propagate match_verdict → hallucination_flag into citation_map.json
         AND citation_map.llm.json.

    3. diff_verifications.py
         Regenerate diff_llm_vs_local.json so the Needs Review tab's
         agreement buckets match the updated LLM verdicts.

The viewer already does `?v=${Date.now()}` cache-bust on every load, so a
normal page refresh will pick up everything. Pair this with
`watch_paper_edits.py` (+ new watch on citation_map.llm.json) for
hands-free updates.

Usage
-----
    uv run python docs/paper/citation_verification/refresh_all.py
    uv run python docs/paper/citation_verification/refresh_all.py --skip-fix
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CV = REPO / "docs" / "paper" / "citation_verification"
VL = REPO / "docs" / "paper" / "verification_local"
SKILLS_DIFF = Path.home() / ".claude/skills/citation-verification/scripts/diff_verifications.py"


def run(cmd: list[str], label: str) -> int:
    print(f"\n── {label} ──")
    print("  $ " + " ".join(str(c) for c in cmd))
    r = subprocess.run(cmd, cwd=str(REPO))
    print(f"  exit={r.returncode}")
    return r.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-fix",  action="store_true",
                    help="Skip fix_claim_extraction (leave claims as-is)")
    ap.add_argument("--skip-diff", action="store_true",
                    help="Skip diff_verifications (don't rebuild Needs Review bucketing)")
    args = ap.parse_args()

    steps = []

    if not args.skip_fix:
        steps.append((
            [sys.executable, str(CV / "fix_claim_extraction.py")],
            "1/3 fix_claim_extraction — re-derive claim_in_paper_corrected from main.tex",
        ))

    steps.append((
        [sys.executable, str(CV / "sync_citation_flags.py")],
        "2/3 sync_citation_flags — propagate match_verdict → hallucination_flag",
    ))

    if not args.skip_diff:
        steps.append((
            [
                sys.executable, str(SKILLS_DIFF),
                "--citation-map", str(CV / "citation_map.llm.json"),
                "--local-verification", str(VL / "verification_local.llm.json"),
                "--output", str(VL / "diff_llm_vs_local.json"),
                "--md", str(VL / "diff_llm_vs_local.md"),
            ],
            "3/3 diff_verifications — rebuild Needs Review agreement buckets",
        ))

    failures = 0
    for cmd, label in steps:
        if run(cmd, label) != 0:
            failures += 1
            print(f"  !! {label} failed, continuing …")

    print()
    print("=" * 60)
    print(f"refresh_all done — {len(steps) - failures}/{len(steps)} steps succeeded")
    if failures:
        print("   Some steps failed — check output above.")
        return 1
    print("   Hard-refresh the browser (⌘+Shift+R) to see updated platform.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
