#!/usr/bin/env python3
"""
merge_llm_closereads.py — Merge per-paper LLM close_reader outputs into a
unified citation_map.llm.json for cross-checking against the local verifier.

Input:
  close_reads/<cite_key>.llm.json  — written by LLM close_reader agents
    { per_claim: [ {line_num, claim_text, source_quote, quote_page,
                    search_verified, verdict, reasoning} ] }
  citation_map.json  — the pipeline stub citation_map (one row per cite × line)

Output:
  citation_map.llm.json — citation_map rows populated with LLM source_quote +
                          match_verdict. Rows without an LLM close_read for
                          that cite_key keep match_verdict=PENDING_LLM.

Also updates reading_memory/<cite_key>.json with the LLM verdicts alongside
the earlier scripted verdicts (preserves both under `per_run/`).

Usage:
  uv run python merge_llm_closereads.py \
      --close-reads-dir docs/paper/citation_verification/close_reads \
      --citation-map-in docs/paper/citation_verification/citation_map.json \
      --citation-map-out docs/paper/citation_verification/citation_map.llm.json \
      --reading-memory-dir docs/paper/reading_memory
"""
from __future__ import annotations

import argparse
import glob
import json
from datetime import datetime, timezone
from pathlib import Path
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--close-reads-dir", required=True)
    ap.add_argument("--citation-map-in", required=True)
    ap.add_argument("--citation-map-out", required=True)
    ap.add_argument("--reading-memory-dir", default=None)
    args = ap.parse_args()

    close_dir = Path(args.close_reads_dir)
    mem_dir = Path(args.reading_memory_dir) if args.reading_memory_dir else None

    # Load all *.llm.json
    llm_by_key: dict[str, dict] = {}
    for p in sorted(close_dir.glob("*.llm.json")):
        data = json.loads(p.read_text())
        key = data.get("cite_key") or p.stem.replace(".llm", "")
        llm_by_key[key] = data

    # Build lookup: (cite_key, line_num) -> verdict dict
    verdict_by_claim: dict[tuple[str, int], dict] = {}
    for key, data in llm_by_key.items():
        for pc in data.get("per_claim", []):
            verdict_by_claim[(key, pc["line_num"])] = pc

    cm_in = json.loads(Path(args.citation_map_in).read_text())
    out = []
    summary = {"MATCH": 0, "PARTIAL": 0, "MISMATCH": 0, "OPPOSITE": 0,
               "NOT_FOUND": 0, "PENDING_LLM": 0}
    for row in cm_in:
        key = row["cite_key"]
        line = row.get("line_num_in_paper")
        v = verdict_by_claim.get((key, line))
        new = dict(row)
        if v:
            new["source_quote"] = v.get("source_quote")
            new["match_verdict"] = v.get("verdict")
            new["reasoning"] = v.get("reasoning")
            loc = new.get("source_location") or {}
            if v.get("quote_page"):
                loc["page"] = v["quote_page"]
                new["source_location"] = loc
        else:
            new["match_verdict"] = "PENDING_LLM"
            new["reasoning"] = "No LLM close_read produced for this cite_key."
        summary[new["match_verdict"]] = summary.get(new["match_verdict"], 0) + 1
        out.append(new)

    Path(args.citation_map_out).write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"Merged {len(llm_by_key)} LLM close_reads -> {args.citation_map_out}")
    print("LLM verdict distribution:")
    for v, n in sorted(summary.items(), key=lambda x: -x[1]):
        print(f"  {v:12s}  {n}")

    # Update reading_memory with LLM verdicts (add to per_run)
    if mem_dir and mem_dir.exists():
        for key, data in llm_by_key.items():
            mem_path = mem_dir / f"{key}.json"
            if not mem_path.exists():
                continue
            mem = json.loads(mem_path.read_text())
            per_run = mem.get("per_run", {})
            per_run["llm_close_reader_v1"] = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generated_by": data.get("generated_by"),
                "per_claim": data.get("per_claim", []),
            }
            mem["per_run"] = per_run
            mem["last_updated"] = datetime.now(timezone.utc).isoformat()
            mem_path.write_text(json.dumps(mem, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
