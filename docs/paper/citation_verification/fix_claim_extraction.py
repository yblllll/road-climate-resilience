#!/usr/bin/env python3
"""
fix_claim_extraction.py — Re-extract the correct claim per citation position.

The original audit pipeline bled the paragraph's first/topic sentence into
every \\citep in that paragraph. 63% of the 63 verdicts ended up testing the
wrong claim. This script:

1. Reads docs/paper_v2/main.tex
2. For each (cite_key, line_num) in citation_map.llm.json, finds the actual
   *sentence* that contains \\citep{...cite_key...} at that line
3. Writes `claim_in_paper_corrected` back into each entry (does not overwrite
   the original claim_in_paper, so we can diff)
4. Emits a short report on entries where the corrected claim differs

Usage:
    uv run python docs/paper/citation_verification/fix_claim_extraction.py
    # --dry-run for preview
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER_TEX = ROOT / "paper_v2" / "main.tex"
LLM_PATH = ROOT / "paper" / "citation_verification" / "citation_map.llm.json"


def strip_latex(s: str) -> str:
    """Light LaTeX → plain text for claim comparison / display."""
    # Drop LaTeX comment-only lines (% at start, after optional whitespace).
    s = re.sub(r"(?m)^\s*%.*$", "", s)
    s = re.sub(r"\\cite[pt]?\{[^}]*\}", "", s)     # drop \citep{...}
    s = re.sub(r"\\citeauthor\{[^}]*\}", "", s)
    s = re.sub(r"\\citet\{[^}]*\}", "", s)
    s = re.sub(r"\\label\{[^}]*\}", "", s)
    s = re.sub(r"\\ref\{[^}]*\}", "", s)
    # Strip sectioning commands entirely so they don't become "sentences"
    s = re.sub(r"\\(section|subsection|subsubsection|paragraph)\*?\{[^}]*\}", "", s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\textit\{([^}]*)\}", r"\1", s)
    s = s.replace("\\,", " ").replace("\\%", "%").replace("\\&", "&")
    s = s.replace("~", " ").replace("--", "–")
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Sentence splitter (LaTeX-aware, light): split on `. ` / `! ` / `? ` but not
# inside \citep{..}. We already strip those above, so simple regex is fine.
_SENT_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z\\])")


def split_sentences(text: str) -> list[str]:
    text = strip_latex(text)
    return [s.strip() for s in _SENT_END.split(text) if s.strip()]


def extract_sentence_with_cite(tex_lines: list[str], line_num: int, cite_key: str,
                               max_span: int = 6) -> str:
    """Walk backward/forward from line_num to find the sentence containing
    \\citep{...cite_key...}. Join up to ±max_span lines around line_num, split
    into sentences (after stripping \\citep), and return the sentence that
    contains cite_key — approximated by finding the sentence whose offset in
    the joined raw text contains the \\citep{cite_key} marker."""
    lo = max(0, line_num - 1 - max_span)
    hi = min(len(tex_lines), line_num + max_span)
    # Drop comment-only lines before joining (else strip_latex's multi-line
    # regex can't fire after we flatten with " ".join).
    block_lines = [ln for ln in tex_lines[lo:hi]
                   if not re.match(r"\s*%", ln)]
    # For each physical line, note which sentences it maps to in the joined raw.
    # But we need to know WHICH sentence has the cite. Do this on the raw text:
    raw = " ".join(block_lines)

    # Find position of \citep{..cite_key..} in raw
    pat = re.compile(r"\\cite[pt]?\{[^}]*" + re.escape(cite_key) + r"[^}]*\}")
    m = pat.search(raw)
    if not m:
        # cite_key not in window → fall back to the physical line content only
        return strip_latex(tex_lines[line_num - 1]) if 0 < line_num <= len(tex_lines) else ""

    # Replace \citep with a sentinel so stripping doesn't destroy position info.
    # Use a lambda replacement to avoid re.sub treating \c etc. as escapes.
    SENTINEL = "__CITEHIT__"
    hit = m.group(0)
    raw_marked = pat.sub(lambda _m: SENTINEL + hit, raw, count=1)

    # Now strip LaTeX and split
    plain = strip_latex(raw_marked)
    sentences = split_sentences(plain) if SENTINEL not in plain else []
    # The sentinel survives strip_latex (it's plain text). Find the sentence
    # that contains the sentinel.
    # Re-split manually preserving sentinel
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\\]|__CITEHIT__)", plain)
    for p in parts:
        p = p.strip()
        if SENTINEL in p:
            return p.replace(SENTINEL, "").strip()

    # fallback: return whole line
    return strip_latex(tex_lines[line_num - 1])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tex_lines = PAPER_TEX.read_text().splitlines()
    llm = json.loads(LLM_PATH.read_text())

    changed = 0
    same = 0
    for e in llm:
        ln = e.get("line_num_in_paper")
        ck = e["cite_key"]
        if not ln:
            continue
        corrected = extract_sentence_with_cite(tex_lines, ln, ck)
        if not corrected:
            continue
        orig = (e.get("claim_in_paper") or "").strip()
        # Treat them as "different" if the first 60 chars of corrected isn't in orig
        head = corrected[:60]
        if head not in orig:
            e["claim_in_paper_corrected"] = corrected
            changed += 1
        else:
            same += 1

    print(f"Total entries: {len(llm)}")
    print(f"  same claim         : {same}")
    print(f"  corrected (was wrong): {changed}")

    if args.dry_run:
        print("\n--dry-run: not writing.")
        # print a few sample corrections
        print("\nSample corrections:")
        n = 0
        for e in llm:
            if "claim_in_paper_corrected" in e and n < 6:
                print(f"\n  {e['cite_key']} L{e['line_num_in_paper']}:")
                print(f"    OLD: {(e.get('claim_in_paper') or '')[:110]}...")
                print(f"    NEW: {e['claim_in_paper_corrected'][:110]}...")
                n += 1
        return 0

    bak = LLM_PATH.with_suffix(".json.preextract.bak")
    shutil.copy2(LLM_PATH, bak)
    print(f"Backup: {bak}")
    LLM_PATH.write_text(json.dumps(llm, indent=2, ensure_ascii=False))
    print(f"Wrote:  {LLM_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
