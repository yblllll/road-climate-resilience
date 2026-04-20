#!/usr/bin/env python3
"""
diff_verifications.py — Compare LLM verdicts vs local PyMuPDF verifier.

Input:
  citation_map.json         (LLM close_reader + semantic_matcher output)
  verification_local.json   (verify_quotes_local.py output)

Output:
  diff_verifications.json / .md
    For each cite_key, alignment between:
      - LLM match_verdict  ∈ {MATCH, PARTIAL, MISMATCH, OPPOSITE, NOT_FOUND, PENDING_LLM}
      - local verdict      ∈ {MATCH_EXACT, MATCH_WRONG_PAGE, MATCH_PARTIAL, NOT_FOUND, NO_QUOTE, NO_PDF}

    Disagreements are flagged and bucketed:
      LLM_MATCH_LOCAL_NOT_FOUND → potential hallucination
      LLM_NOT_FOUND_LOCAL_MATCH → LLM missed a real quote
      WRONG_PAGE                → page number off

Usage:
    uv run python diff_verifications.py \
        --citation-map citation_map.json \
        --local-verification verification_local.json \
        --output diff_verifications.json \
        --md diff_verifications.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


AGREEMENT_TABLE = {
    # (llm, local) → bucket
    ("MATCH", "MATCH_EXACT"): "AGREE_MATCH",
    ("MATCH", "MATCH_WRONG_PAGE"): "AGREE_PAGE_OFF",
    ("MATCH", "MATCH_PARTIAL"): "AGREE_MATCH_FUZZY",
    ("MATCH", "NOT_FOUND"): "LLM_MATCH_LOCAL_NOT_FOUND",
    ("MATCH", "NO_QUOTE"): "MATCH_WITHOUT_QUOTE",  # agent said MATCH but didn't supply a quote
    ("PARTIAL", "MATCH_EXACT"): "AGREE_PARTIAL_QUOTE_VERIFIED",
    ("PARTIAL", "MATCH_PARTIAL"): "AGREE_PARTIAL",
    ("PARTIAL", "MATCH_WRONG_PAGE"): "AGREE_PARTIAL_PAGE_OFF",
    ("PARTIAL", "NOT_FOUND"): "LLM_PARTIAL_LOCAL_NOT_FOUND",
    ("PARTIAL", "NO_QUOTE"): "LLM_PARTIAL_WITHOUT_QUOTE",
    ("MISMATCH", "MATCH_EXACT"): "LLM_FLAG_QUOTE_REAL",
    ("MISMATCH", "MATCH_PARTIAL"): "LLM_FLAG_QUOTE_FUZZY",
    ("MISMATCH", "NOT_FOUND"): "AGREE_NOT_SUPPORTED",
    ("MISMATCH", "NO_QUOTE"): "LLM_MISMATCH_WITHOUT_QUOTE",
    ("OPPOSITE", "MATCH_EXACT"): "LLM_OPPOSITE_QUOTE_REAL",
    ("OPPOSITE", "NO_QUOTE"): "LLM_OPPOSITE_WITHOUT_QUOTE",
    ("NOT_FOUND", "MATCH_EXACT"): "LLM_NOT_FOUND_LOCAL_MATCH",
    ("NOT_FOUND", "MATCH_PARTIAL"): "LLM_NOT_FOUND_LOCAL_PARTIAL",
    ("NOT_FOUND", "NOT_FOUND"): "AGREE_NOT_FOUND",
    ("NOT_FOUND", "NO_QUOTE"): "AGREE_NOT_FOUND",
    ("PENDING_LLM", "*"): "LLM_NOT_RUN",
}


def bucket(llm: str, local: str) -> str:
    if llm == "PENDING_LLM":
        return "LLM_NOT_RUN"
    if (llm, local) in AGREEMENT_TABLE:
        return AGREEMENT_TABLE[(llm, local)]
    # fallback pattern-match
    if llm in {"MISMATCH", "OPPOSITE"}:
        return f"LLM_{llm}_LOCAL_{local}"
    return f"UNCLASSIFIED_{llm}_{local}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--citation-map", required=True)
    ap.add_argument("--local-verification", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--md", default=None)
    args = ap.parse_args()

    cm = json.loads(Path(args.citation_map).read_text())
    lv = json.loads(Path(args.local_verification).read_text())
    # Keyed by (cite_key, claim_line) because one paper is cited at multiple
    # claim lines with different quotes per claim.
    local_by_claim: dict[tuple[str, int], dict] = {}
    for r in lv["results"]:
        local_by_claim[(r["cite_key"], r.get("claim_line"))] = r

    diffs = []
    buckets: dict[str, int] = {}
    for entry in cm:
        k = entry["cite_key"]
        line = entry.get("line_num_in_paper")
        llm = entry.get("match_verdict") or "PENDING_LLM"
        local_entry = local_by_claim.get((k, line), {"verdict": "NOT_RUN"})
        local = local_entry["verdict"]
        b = bucket(llm, local)
        buckets[b] = buckets.get(b, 0) + 1
        diffs.append({
            "cite_key": k,
            "line_num": entry.get("line_num_in_paper"),
            "llm_verdict": llm,
            "llm_reasoning": (entry.get("reasoning") or "")[:200],
            "local_verdict": local,
            "local_layer": local_entry.get("matched_layer"),
            "local_page": local_entry.get("matched_page"),
            "local_snippet": (local_entry.get("matched_snippet") or "")[:200],
            "agreement": b,
        })

    out = {
        "total": len(diffs),
        "agreement_buckets": buckets,
        "diffs": diffs,
    }
    Path(args.output).write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"Wrote {args.output}")
    print("Agreement distribution:")
    for b, n in sorted(buckets.items(), key=lambda x: -x[1]):
        print(f"  {b:40s}  {n}")

    if args.md:
        lines = [
            f"# Verification Diff — LLM vs Local PyMuPDF",
            "",
            f"Total entries: {len(diffs)}",
            "",
            "## Agreement distribution",
            "",
            "| Bucket | Count |",
            "|---|---|",
        ]
        for b, n in sorted(buckets.items(), key=lambda x: -x[1]):
            lines.append(f"| {b} | {n} |")
        lines.extend(["", "## Disagreements (LLM said MATCH, local says NOT_FOUND)", ""])
        for d in diffs:
            if d["agreement"] == "LLM_MATCH_LOCAL_NOT_FOUND":
                lines.append(f"- **{d['cite_key']}** (line {d['line_num']}) — LLM reasoning: _{d['llm_reasoning'][:150]}_")
        lines.extend(["", "## Disagreements (LLM said NOT_FOUND, local found it)", ""])
        for d in diffs:
            if d["agreement"].startswith("LLM_NOT_FOUND_LOCAL_"):
                lines.append(f"- **{d['cite_key']}** (line {d['line_num']}) — local found on p.{d['local_page']}: _{d['local_snippet'][:150]}_")
        Path(args.md).write_text("\n".join(lines))
        print(f"Wrote {args.md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
