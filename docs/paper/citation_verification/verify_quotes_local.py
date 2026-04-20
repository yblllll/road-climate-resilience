#!/usr/bin/env python3
"""
verify_quotes_local.py — Tokenless local verifier for citation quotes using PyMuPDF.

Given a citation_map.json (output of run.py), for each entry that has a
`source_quote` and `source_location.pdf_path`, verify via 3-layer fallback:

  Layer 1: exact-phrase search on the claimed page
  Layer 2: full-document scan across all pages
  Layer 3: substring search using the first ~40% of the phrase
           (handles PDF encoding artefacts: ligatures, hyphenation, line breaks)

Every verification is tokenless — no LLM call — which makes this a cheap
adversarial cross-check against the LLM close_reader + semantic_matcher agents.

Usage:
    uv run python verify_quotes_local.py \
        --citation-map <path> \
        --output verification_local.json

Output schema per entry:
    {
      "cite_key": "...",
      "claim_line": 70,
      "quote_char_count": 123,
      "claimed_page": 4,
      "verdict": "MATCH_EXACT" | "MATCH_WRONG_PAGE" | "MATCH_PARTIAL" | "NOT_FOUND" | "NO_QUOTE" | "NO_PDF",
      "matched_layer": 1 | 2 | 3 | null,
      "matched_page": <int or null>,
      "matched_snippet": "..." | null,
      "reason": "..."
    }
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: uv pip install pymupdf", file=sys.stderr)
    sys.exit(2)


def normalize(text: str) -> str:
    """Collapse whitespace, unify quotes/dashes, lowercase for matching."""
    text = text.replace("\u2013", "-").replace("\u2014", "-")  # en/em dash
    text = text.replace("\u2018", "'").replace("\u2019", "'")  # curly apostrophe
    text = text.replace("\u201c", '"').replace("\u201d", '"')  # curly quotes
    text = text.replace("\ufb01", "fi").replace("\ufb02", "fl")  # ligatures
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def layer1_exact_on_page(doc: "fitz.Document", quote: str, page_num: int) -> tuple[bool, str | None]:
    """Search the claimed page for the full phrase."""
    if page_num is None or page_num < 1 or page_num > len(doc):
        return False, None
    page = doc[page_num - 1]
    page_text = normalize(page.get_text())
    needle = normalize(quote)
    if needle in page_text:
        idx = page_text.find(needle)
        snippet = page_text[max(0, idx - 40): idx + len(needle) + 40]
        return True, snippet
    return False, None


def layer2_scan_all_pages(doc: "fitz.Document", quote: str) -> tuple[int | None, str | None]:
    """Scan every page for the full phrase."""
    needle = normalize(quote)
    for i in range(len(doc)):
        page_text = normalize(doc[i].get_text())
        if needle in page_text:
            idx = page_text.find(needle)
            snippet = page_text[max(0, idx - 40): idx + len(needle) + 40]
            return i + 1, snippet
    return None, None


def layer3_partial_match(doc: "fitz.Document", quote: str) -> tuple[int | None, str | None, float]:
    """Try matching the first ~40% of the phrase (handles PDF artefacts)."""
    norm = normalize(quote)
    if len(norm) < 20:
        return None, None, 0.0
    # Try progressively shorter prefixes, stopping when one matches
    for frac in (0.6, 0.5, 0.4, 0.3):
        n = max(20, int(len(norm) * frac))
        prefix = norm[:n]
        # stop at word boundary to avoid cut-off words
        if " " in prefix:
            prefix = prefix.rsplit(" ", 1)[0]
        for i in range(len(doc)):
            page_text = normalize(doc[i].get_text())
            if prefix in page_text:
                idx = page_text.find(prefix)
                snippet = page_text[max(0, idx - 40): idx + n + 40]
                return i + 1, snippet, frac
    return None, None, 0.0


def verify_one(entry: dict) -> dict:
    cite_key = entry.get("cite_key", "UNKNOWN")
    claim_line = entry.get("line_num_in_paper")
    quote = entry.get("source_quote")
    loc = entry.get("source_location") or {}
    pdf_path = loc.get("pdf_path")
    claimed_page = loc.get("page") or loc.get("page_num")

    result = {
        "cite_key": cite_key,
        "claim_line": claim_line,
        "quote_char_count": len(quote) if quote else 0,
        "claimed_page": claimed_page,
        "verdict": None,
        "matched_layer": None,
        "matched_page": None,
        "matched_snippet": None,
        "reason": "",
    }

    if not quote:
        result["verdict"] = "NO_QUOTE"
        result["reason"] = "No source_quote in citation_map entry (likely PENDING_LLM)"
        return result
    if not pdf_path or not Path(pdf_path).exists():
        result["verdict"] = "NO_PDF"
        result["reason"] = f"PDF not found: {pdf_path}"
        return result

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        result["verdict"] = "NO_PDF"
        result["reason"] = f"Failed to open PDF: {e}"
        return result

    try:
        # Layer 1: exact on claimed page
        if claimed_page:
            ok, snip = layer1_exact_on_page(doc, quote, claimed_page)
            if ok:
                result["verdict"] = "MATCH_EXACT"
                result["matched_layer"] = 1
                result["matched_page"] = claimed_page
                result["matched_snippet"] = snip
                result["reason"] = "Exact phrase found on claimed page"
                return result

        # Layer 2: full-document scan
        page_found, snip = layer2_scan_all_pages(doc, quote)
        if page_found:
            if claimed_page and page_found != claimed_page:
                result["verdict"] = "MATCH_WRONG_PAGE"
                result["reason"] = f"Phrase found on p.{page_found}, not claimed p.{claimed_page}"
            else:
                result["verdict"] = "MATCH_EXACT"
                result["reason"] = f"Exact phrase found on p.{page_found}"
            result["matched_layer"] = 2
            result["matched_page"] = page_found
            result["matched_snippet"] = snip
            return result

        # Layer 3: partial match
        page_found, snip, frac = layer3_partial_match(doc, quote)
        if page_found:
            result["verdict"] = "MATCH_PARTIAL"
            result["matched_layer"] = 3
            result["matched_page"] = page_found
            result["matched_snippet"] = snip
            result["reason"] = (
                f"Partial match ({int(frac*100)}% prefix) on p.{page_found} — "
                f"possibly a PDF-encoding artefact or paraphrase"
            )
            return result

        result["verdict"] = "NOT_FOUND"
        result["reason"] = "Quote not found in any form across all pages"
        return result
    finally:
        doc.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--citation-map", required=True, help="Path to citation_map.json")
    ap.add_argument("--output", required=True, help="Path to write verification_local.json")
    args = ap.parse_args()

    cm_path = Path(args.citation_map).resolve()
    entries = json.loads(cm_path.read_text())

    results = []
    verdicts = {}
    for e in entries:
        r = verify_one(e)
        results.append(r)
        verdicts[r["verdict"]] = verdicts.get(r["verdict"], 0) + 1

    out_path = Path(args.output).resolve()
    out_path.write_text(json.dumps({
        "generated_from": str(cm_path),
        "total_entries": len(results),
        "verdict_counts": verdicts,
        "results": results,
    }, indent=2, ensure_ascii=False))

    print(f"Verified {len(results)} entries → {out_path}")
    print("Verdict distribution:")
    for v, n in sorted(verdicts.items(), key=lambda x: -x[1]):
        print(f"  {v:20s}  {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
