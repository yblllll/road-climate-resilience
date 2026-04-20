#!/usr/bin/env python3
"""
close_read_pymupdf.py — Deterministic (LLM-free) close reader + naive semantic
matcher. Pairs with verify_quotes_local.py to give an end-to-end cross-check
against the LLM close_reader + semantic_matcher agents.

Workflow:
  1. Load claims_extracted.json and pdf_locations.json.
  2. For each (cite_key, claim) pair:
       - Tokenize claim_text into content words (stopwords removed).
       - Extract every sentence from the PDF (per page, split on .!?).
       - Score each 15-50-word sentence by keyword-overlap fraction.
       - Pick top candidate; verify exact substring with PyMuPDF search_for.
       - Assign verdict: MATCH / PARTIAL / NOT_FOUND.
  3. Write a new citation_map.json with populated source_quote + verdicts.
  4. Refresh close_reads/<cite_key>.json with the per-paper candidate set.

This is NOT a replacement for an LLM close reader — the scoring is
keyword-bag overlap, no semantics, no polarity. Think of it as a lossy
reference that the LLM output must explain when it disagrees.

Usage:
    uv run python close_read_pymupdf.py \
        --claims docs/paper/citation_verification/claims_extracted.json \
        --pdf-locations docs/paper/citation_verification/pdf_locations.json \
        --citation-map-in docs/paper/citation_verification/citation_map.json \
        --close-reads-dir docs/paper/citation_verification/close_reads \
        --citation-map-out docs/paper/citation_verification/citation_map.local.json \
        --reading-memory-dir docs/paper/reading_memory
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: uv pip install pymupdf", file=sys.stderr)
    sys.exit(2)


STOPWORDS = set("""
a an the and or but of to in on at for with by from as is are was were be been being
this that these those it its their his her our your my we you i he she they them us
have has had do does did not no nor can could should would may might must will shall
than then so such if because while although though whereas however also
which who whom whose what when where why how
""".split())


def tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split on whitespace, drop stopwords/short tokens."""
    text = re.sub(r"[^\w\s-]", " ", text.lower())
    return [t for t in text.split() if len(t) > 2 and t not in STOPWORDS]


def normalize(text: str) -> str:
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\ufb01", "fi").replace("\ufb02", "fl")
    text = re.sub(r"\s+", " ", text).strip()
    return text


SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")


def split_sentences(page_text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_SPLIT.split(page_text) if s.strip()]


def score_sentence(claim_tokens: set[str], sentence: str) -> tuple[float, int]:
    s_tokens = set(tokenize(sentence))
    if not s_tokens:
        return 0.0, 0
    overlap = claim_tokens & s_tokens
    recall = len(overlap) / max(1, len(claim_tokens))
    return recall, len(overlap)


def extract_candidates(doc: "fitz.Document", claim: str, top_k: int = 5) -> list[dict]:
    claim_tokens = set(tokenize(claim))
    if not claim_tokens:
        return []
    all_candidates: list[dict] = []
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = normalize(page.get_text())
        for sent in split_sentences(text):
            words = sent.split()
            if not (10 <= len(words) <= 55):
                continue
            recall, n_overlap = score_sentence(claim_tokens, sent)
            if n_overlap < 2:
                continue
            all_candidates.append({
                "page": page_idx + 1,
                "quote": sent,
                "word_count": len(words),
                "overlap_n": n_overlap,
                "recall": round(recall, 3),
            })
    all_candidates.sort(key=lambda c: (-c["recall"], -c["overlap_n"]))
    # Verify with search_for; drop unverified
    verified: list[dict] = []
    for c in all_candidates[: top_k * 3]:
        page = doc[c["page"] - 1]
        needle = c["quote"][:80]  # PyMuPDF search_for tolerates short needles better
        rects = page.search_for(needle)
        if rects:
            c["search_verified"] = True
            c["bbox"] = list(rects[0])
        else:
            c["search_verified"] = False
        verified.append(c)
        if sum(1 for v in verified if v["search_verified"]) >= top_k:
            break
    return [v for v in verified if v["search_verified"]][:top_k]


def classify_verdict(recall: float, n_overlap: int) -> str:
    if recall >= 0.55 and n_overlap >= 4:
        return "MATCH"
    if recall >= 0.30 and n_overlap >= 2:
        return "PARTIAL"
    return "NOT_FOUND"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--claims", required=True)
    ap.add_argument("--pdf-locations", required=True)
    ap.add_argument("--citation-map-in", required=True)
    ap.add_argument("--close-reads-dir", required=True)
    ap.add_argument("--citation-map-out", required=True)
    ap.add_argument("--reading-memory-dir", default=None)
    args = ap.parse_args()

    claims = json.loads(Path(args.claims).read_text())
    pdf_loc = json.loads(Path(args.pdf_locations).read_text())
    cm_in = json.loads(Path(args.citation_map_in).read_text())
    close_dir = Path(args.close_reads_dir)
    close_dir.mkdir(parents=True, exist_ok=True)
    mem_dir = Path(args.reading_memory_dir) if args.reading_memory_dir else None
    if mem_dir:
        mem_dir.mkdir(parents=True, exist_ok=True)

    # Group claims by cite_key
    by_key: dict[str, list[dict]] = {}
    for c in claims:
        by_key.setdefault(c["cite_key"], []).append(c)

    # Cache PDFs so we only open each once
    doc_cache: dict[str, "fitz.Document"] = {}
    per_claim_verdict: dict[tuple[str, int], dict] = {}
    per_key_candidates: dict[str, list[dict]] = {}
    summary = {"MATCH": 0, "PARTIAL": 0, "NOT_FOUND": 0, "NO_PDF": 0}

    for key, key_claims in sorted(by_key.items()):
        loc = pdf_loc.get(key, {})
        pdf_path = loc.get("pdf_path")
        if not pdf_path or not Path(pdf_path).exists():
            for c in key_claims:
                per_claim_verdict[(key, c["line_num"])] = {
                    "source_quote": None,
                    "verdict": "NOT_FOUND",
                    "reason": "PDF not available",
                    "matched_page": None,
                }
                summary["NO_PDF"] += 1
            continue
        if pdf_path not in doc_cache:
            doc_cache[pdf_path] = fitz.open(pdf_path)
        doc = doc_cache[pdf_path]
        per_key_candidates.setdefault(key, [])
        for c in key_claims:
            cands = extract_candidates(doc, c["claim_text"])
            if cands:
                top = cands[0]
                verdict = classify_verdict(top["recall"], top["overlap_n"])
                per_claim_verdict[(key, c["line_num"])] = {
                    "source_quote": top["quote"],
                    "verdict": verdict,
                    "reason": f"Keyword-overlap recall={top['recall']} (n={top['overlap_n']}) on p.{top['page']}",
                    "matched_page": top["page"],
                    "candidate_count": len(cands),
                }
                summary[verdict] = summary.get(verdict, 0) + 1
                # track unique quotes for close_reads file
                per_key_candidates[key].extend(cands)
            else:
                per_claim_verdict[(key, c["line_num"])] = {
                    "source_quote": None,
                    "verdict": "NOT_FOUND",
                    "reason": "No candidate sentence passed the keyword-overlap threshold",
                    "matched_page": None,
                    "candidate_count": 0,
                }
                summary["NOT_FOUND"] += 1

    # Dedupe candidates per key
    for key, cands in per_key_candidates.items():
        seen = set()
        uniq = []
        for c in cands:
            sig = (c["page"], c["quote"][:60])
            if sig in seen:
                continue
            seen.add(sig)
            uniq.append(c)
        # write close_reads/<cite_key>.json
        (close_dir / f"{key}.json").write_text(json.dumps({
            "cite_key": key,
            "pdf_path": pdf_loc.get(key, {}).get("pdf_path"),
            "generated_by": "close_read_pymupdf.py (LLM-free)",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "candidate_quotes": uniq,
            "read_complete": True,
        }, indent=2, ensure_ascii=False))
        if mem_dir:
            mem_path = mem_dir / f"{key}.json"
            if mem_path.exists():
                mem = json.loads(mem_path.read_text())
            else:
                mem = {"cite_key": key, "per_claim_verdicts": []}
            mem["close_read_complete"] = True
            mem["candidate_quotes"] = uniq
            mem["last_updated"] = datetime.now(timezone.utc).isoformat()
            mem["per_claim_verdicts"] = []
            for c in by_key.get(key, []):
                v = per_claim_verdict.get((key, c["line_num"]), {})
                mem["per_claim_verdicts"].append({
                    "line_num": c["line_num"],
                    "claim_text": c["claim_text"][:300],
                    "source_quote": v.get("source_quote"),
                    "verdict": v.get("verdict"),
                    "matched_page": v.get("matched_page"),
                    "reason": v.get("reason"),
                })
            mem["notes"] = "Auto-populated by close_read_pymupdf.py (deterministic, no LLM)."
            mem_path.write_text(json.dumps(mem, indent=2, ensure_ascii=False))

    # Produce new citation_map.json with populated quotes + verdicts
    cm_out = []
    for entry in cm_in:
        key = entry["cite_key"]
        line = entry.get("line_num_in_paper")
        v = per_claim_verdict.get((key, line), {})
        new = dict(entry)
        if v:
            new["source_quote"] = v.get("source_quote")
            new["match_verdict"] = v.get("verdict")
            new["reasoning"] = v.get("reason")
            if v.get("matched_page"):
                loc = new.get("source_location") or {}
                loc["page"] = v["matched_page"]
                new["source_location"] = loc
        cm_out.append(new)

    Path(args.citation_map_out).write_text(json.dumps(cm_out, indent=2, ensure_ascii=False))
    print(f"Wrote {args.citation_map_out}")
    print("Verdict distribution (local close_read):")
    for v, n in sorted(summary.items(), key=lambda x: -x[1]):
        print(f"  {v:12s}  {n}")
    for d in doc_cache.values():
        d.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
