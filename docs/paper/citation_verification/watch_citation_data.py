#!/usr/bin/env python3
"""
watch_citation_data.py — Poll citation-verification files and auto-run
refresh_all.py whenever any of them is touched.

Watched inputs (any mtime change triggers refresh):

  - docs/paper_v2/main.tex                              (paper source — drives claim extraction)
  - docs/paper/citation_verification/citation_map.llm.json
  - docs/paper/verification_local/verification_local.llm.json

Effect chain (handled by refresh_all.py):
  main.tex changed
    → fix_claim_extraction.py re-derives claim_in_paper_corrected for each \\citep
    → sync_citation_flags.py propagates verdicts → hallucination_flag
    → diff_verifications.py rebuilds the Needs Review agreement buckets
    → viewer picks up everything on next ⌘+Shift+R (or any reload — cache-bust is on)

Usage
-----
    uv run python docs/paper/citation_verification/watch_citation_data.py
    #  Ctrl-C to stop

Pair with watch_paper_edits.py (rebuilds PDF) for a full hands-free pipeline:
    (tab 1) python docs/paper/watch_paper_edits.py       # paper → PDF
    (tab 2) python docs/paper/citation_verification/watch_citation_data.py  # citations → platform

Flags
-----
  --interval FLOAT   polling interval (default 2.0s)
  --debounce FLOAT   don't re-run within this many seconds of the last run (default 5.0s)
  --once             run refresh_all.py once, then exit
  --no-initial       skip refresh on startup
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    repo = Path(__file__).resolve().parents[3]
    refresh_path = Path(__file__).resolve().parent / "refresh_all.py"

    watched = [
        repo / "docs/paper_v2/main.tex",
        repo / "docs/paper/citation_verification/citation_map.llm.json",
        repo / "docs/paper/verification_local/verification_local.llm.json",
    ]

    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--interval", type=float, default=2.0)
    ap.add_argument("--debounce", type=float, default=5.0,
                    help="Minimum seconds between consecutive refresh runs")
    ap.add_argument("--once",       action="store_true")
    ap.add_argument("--no-initial", action="store_true")
    args = ap.parse_args()

    if not refresh_path.exists():
        print(f"[watch-cite] ERROR: refresh script not found → {refresh_path}",
              file=sys.stderr)
        return 2

    def refresh(tag: str) -> int:
        print(f"\n[watch-cite] {tag} — running refresh_all.py")
        t0 = time.time()
        r = subprocess.run([sys.executable, str(refresh_path)])
        print(f"[watch-cite] refresh exited {r.returncode} in {time.time()-t0:.1f}s")
        return r.returncode

    if args.once:
        return refresh("one-shot")

    # Snapshot initial mtimes
    mtimes: dict[Path, float | None] = {}
    for p in watched:
        mtimes[p] = p.stat().st_mtime if p.exists() else None

    if not args.no_initial:
        refresh("startup refresh")
    last_run = time.time()

    print(f"[watch-cite] polling {len(watched)} paths @ {args.interval}s  (debounce {args.debounce}s)")
    for p in watched:
        exists = "✓" if p.exists() else "✗"
        print(f"   {exists} {p.relative_to(repo)}")
    print("[watch-cite] Ctrl-C to stop")

    while True:
        try:
            time.sleep(args.interval)
            triggered: list[str] = []
            for p in watched:
                if not p.exists():
                    continue
                m = p.stat().st_mtime
                if mtimes.get(p) is None:
                    mtimes[p] = m
                    triggered.append(f"{p.name} appeared")
                elif m != mtimes[p]:
                    mtimes[p] = m
                    triggered.append(p.name)
            if triggered and (time.time() - last_run) >= args.debounce:
                tag = time.strftime("%H:%M:%S") + " — changed: " + ", ".join(triggered)
                refresh(tag)
                last_run = time.time()
        except KeyboardInterrupt:
            print("\n[watch-cite] stopped by user")
            return 0
        except Exception as e:
            print(f"[watch-cite] warning: {e}")


if __name__ == "__main__":
    sys.exit(main())
