#!/usr/bin/env python3
"""
sync_citation_flags.py — merge LLM close-read verdicts into citation_map.json.

Reads:
  citation_map.json           (the platform's color-source; 63 rows with hallucination_flag)
  citation_map.llm.json       (LLM close-reader output; 63 rows with match_verdict)

Writes back citation_map.json with hallucination_flag updated per mapping:
  LLM MATCH       → NONE                  (green - "verified")
  LLM PARTIAL     → PARTIAL               (yellow - "partial / overclaim")
  LLM MISMATCH    → MISMATCH              (red   - "misattribution")
  LLM OPPOSITE    → OPPOSITE              (red   - "contradicts source")
  LLM NOT_FOUND   → MISMATCH              (red   - LLM could not find support in paper)
  LLM PENDING_LLM → NEEDS_MANUAL_REVIEW   (blue  - not yet audited)

Existing AUTHORITY_VIOLATION flags are preserved unless LLM escalates severity
(MATCH+authority → AUTHORITY_VIOLATION stays; MISMATCH+authority → MISMATCH wins).

Usage:
    uv run python docs/paper/citation_verification/sync_citation_flags.py
    # --dry-run to preview without writing
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
# citation_map.json copies: the viewer fetches the one at docs/paper/ (root),
# the pipeline writes to docs/paper/citation_verification/. Keep them in sync.
CM_PATHS = [
    ROOT / "paper" / "citation_map.json",                        # viewer fallback (cmLegacy)
    ROOT / "paper" / "citation_verification" / "citation_map.json",
]
CM_PATH = CM_PATHS[0]   # primary for read
# The viewer prefers citation_map.llm.json when it exists (see literature_viewer.html
# L770-771: cmMerged = cmLlm && cmLlm.length ? cmLlm : cmLegacy). It also has its own
# hallucination_flag field that we must keep in sync with the cmLegacy copies.
LLM_PATH = ROOT / "paper" / "citation_verification" / "citation_map.llm.json"


LLM_TO_FLAG = {
    "MATCH":       "NONE",
    "PARTIAL":     "PARTIAL",
    "MISMATCH":    "MISMATCH",
    "OPPOSITE":    "OPPOSITE",
    "NOT_FOUND":   "OVERCLAIM",    # LLM read full paper + found no passage supporting claim
    "PENDING_LLM": "NEEDS_MANUAL_REVIEW",
}

# Only these tier codes are a real authority problem. `X` = metadata lookup
# failed (no journal info resolved), which is NOT the same as "low tier" and
# must NOT default to AUTHORITY_VIOLATION. This fixes the 2026-04-21 bug where
# bi2022weather (Urban Climate, Q1) etc. were mis-flagged purple.
AUTH_VIOLATION_TIERS = {"B", "C"}

# Severity rank: higher = more severe, wins tie between LLM and existing flag
SEVERITY = {
    "NONE":                  0,
    "NEEDS_MANUAL_REVIEW":   1,
    "SOURCE_NOT_AVAILABLE":  2,
    "PARTIAL":               3,
    "OVERCLAIM":             4,
    "AUTHORITY_VIOLATION":   5,
    "MISMATCH":              6,
    "OPPOSITE":              6,
    "MISATTRIBUTION":        6,
    "FAKE_QUOTE":            7,
    "FAKE_REFERENCE":        8,
}


def key(e: dict) -> tuple[str, int | None]:
    return (e["cite_key"], e.get("line_num_in_paper"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cm = json.loads(CM_PATH.read_text())
    llm = json.loads(LLM_PATH.read_text())

    llm_by_key = {key(e): e for e in llm}

    before = Counter(e.get("hallucination_flag") for e in cm)
    updates = 0
    new_flags = []

    for e in cm:
        k = key(e)
        lv = llm_by_key.get(k)
        cur = e.get("hallucination_flag") or "NEEDS_MANUAL_REVIEW"
        if not lv:
            new_flags.append(cur)
            continue
        mv = (lv.get("match_verdict") or "").upper()
        if not mv or mv not in LLM_TO_FLAG:
            new_flags.append(cur)
            continue
        proposed = LLM_TO_FLAG[mv]

        # If current flag is AUTHORITY_VIOLATION but tier is unresolved (X / empty),
        # downgrade it — metadata lookup failed, not a real authority problem.
        tier = (lv.get("authority_tier") or "").upper()
        if cur == "AUTHORITY_VIOLATION" and tier not in AUTH_VIOLATION_TIERS:
            cur = "NEEDS_MANUAL_REVIEW"

        # Decide winner. Two overrides that bypass severity-based preservation:
        # (a) Re-audited entries (reaudit_reason present) — the old claim was wrong,
        #     so the old flag is stale and cannot be trusted. Always trust new verdict.
        # (b) Current flag is NEEDS_MANUAL_REVIEW — placeholder, always superseded.
        reaudited = bool(lv.get("reaudit_reason"))
        if reaudited or cur == "NEEDS_MANUAL_REVIEW":
            chosen = proposed
        else:
            # Normal path: AUTHORITY_VIOLATION beats NONE/PARTIAL,
            # but LLM MISMATCH/OPPOSITE/FAKE* is more severe and wins.
            chosen = cur
            if SEVERITY.get(proposed, 0) >= SEVERITY.get(cur, 0):
                chosen = proposed
        # Also import LLM reasoning into the entry for better tooltip
        if lv.get("reasoning") and not e.get("reasoning"):
            e["reasoning"] = lv["reasoning"][:500]
        # Propagate match_verdict so tooltips can show both
        e["match_verdict"] = mv

        if chosen != cur:
            updates += 1
        e["hallucination_flag"] = chosen
        new_flags.append(chosen)

    after = Counter(new_flags)

    print("── Before ──")
    for k_, n in sorted(before.items(), key=lambda x: -x[1]):
        print(f"  {k_:30s} {n}")
    print(f"\n── After ({updates} changed) ──")
    for k_, n in sorted(after.items(), key=lambda x: -x[1]):
        print(f"  {k_:30s} {n}")

    if args.dry_run:
        print("\n--dry-run: not writing.")
        return 0

    # Back up, then write both citation_map.json copies
    payload = json.dumps(cm, indent=2, ensure_ascii=False)
    for p in CM_PATHS:
        if p.exists():
            bak = p.with_suffix(".json.bak")
            shutil.copy2(p, bak)
            print(f"Backup: {bak}")
        p.write_text(payload)
        print(f"Wrote  : {p}")

    # Also propagate the chosen flags into citation_map.llm.json — that file
    # is what the viewer actually prefers (L770-771). Each llm entry gets the
    # flag derived for its (cite_key, line_num) from cm above.
    flag_by_key = {key(e): e.get("hallucination_flag") for e in cm}
    llm_updated = 0
    for e in llm:
        new_flag = flag_by_key.get(key(e))
        if new_flag and new_flag != e.get("hallucination_flag"):
            e["hallucination_flag"] = new_flag
            llm_updated += 1
    if LLM_PATH.exists():
        bak = LLM_PATH.with_suffix(".json.bak")
        shutil.copy2(LLM_PATH, bak)
        print(f"Backup: {bak}")
    LLM_PATH.write_text(json.dumps(llm, indent=2, ensure_ascii=False))
    print(f"Wrote  : {LLM_PATH}  ({llm_updated} flags updated in .llm.json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
