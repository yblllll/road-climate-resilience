# Citation-Verification Pipeline

Two independent verification paths, cross-checked.

## Layer A — LLM agents (semantic judgment)

| Stage | Agent | Input | Output |
|---|---|---|---|
| 1 | `claim_extractor` | `main.tex` + `paper_content.json` | `claims_extracted.json` |
| 2 | `pdf_locator` | `references.bib` + `Literature_Review/` | `pdf_locations.json` |
| 3 | `close_reader` | PDF + one cite_key's claims | `close_reads/<cite_key>.llm.json` |
| 4 | `semantic_matcher` | close_reads + claims | per-claim verdict (MATCH/PARTIAL/MISMATCH/OPPOSITE/NOT_FOUND) |
| 5 | `authority_gate` | cite_key + bib + domain rules | `authority_verdicts.json` |
| 6 | `hallucination_detector` | all of the above | `citation_map.json` |

Per-paper LLM close-reads are dispatched as parallel background agents.
Reasonable cap: 1 agent per cite_key, each seeing only that paper's PDF.

## Layer B — Deterministic PyMuPDF (tokenless)

| Script | Role | Output |
|---|---|---|
| `close_read_pymupdf.py` | Keyword-overlap baseline — extracts top-scoring sentence per claim, verifies with `search_for`, assigns MATCH / PARTIAL / NOT_FOUND by recall threshold | `citation_map.local.json` + `close_reads/<cite_key>.json` |
| `verify_quotes_local.py` | 3-layer fallback verifier (exact on claimed page → full-doc scan → 40% prefix partial) | `verification_local/verification_local.json` |
| `diff_verifications.py` | Compares any LLM-produced `citation_map.json` against the local verifier's output | `verification_local/diff_*.json` + `.md` |

No LLM calls. Runs in < 30 seconds on the full Literature_Review (~300 MB, 29 PDFs).

## Reading memory

`docs/paper/reading_memory/<cite_key>.json` — per-paper record of every
candidate quote ever extracted, the claims it was linked to, and the verdict
under each pipeline run. Committed to git so past reads are recoverable after
a pipeline re-run.

## Agreement buckets (diff)

`AGREE_MATCH`, `AGREE_PAGE_OFF`, `AGREE_PARTIAL`, `AGREE_NOT_FOUND` → no action.
`LLM_MATCH_LOCAL_NOT_FOUND` → **potential LLM hallucination**: LLM claims
support, local can't find the quote in the PDF. Read and judge.
`LLM_NOT_FOUND_LOCAL_MATCH` → LLM missed a real quote. Worth re-running the
close_reader for that cite_key.
`LOCAL_STRONGER_THAN_LLM` → local picked a MATCH where LLM was only PARTIAL.
Usually a keyword coincidence; still worth scanning.

## Usage

```bash
# Local baseline (tokenless, fast)
uv run python docs/paper/citation_verification/close_read_pymupdf.py \
    --claims docs/paper/citation_verification/claims_extracted.json \
    --pdf-locations docs/paper/citation_verification/pdf_locations.json \
    --citation-map-in docs/paper/citation_verification/citation_map.json \
    --close-reads-dir docs/paper/citation_verification/close_reads \
    --citation-map-out docs/paper/citation_verification/citation_map.local.json \
    --reading-memory-dir docs/paper/reading_memory

# Verify LLM output with local verifier
uv run python docs/paper/citation_verification/verify_quotes_local.py \
    --citation-map docs/paper/citation_verification/citation_map.llm.json \
    --output docs/paper/verification_local/verification_local.llm.json

# Diff
uv run python docs/paper/citation_verification/diff_verifications.py \
    --citation-map docs/paper/citation_verification/citation_map.llm.json \
    --local-verification docs/paper/verification_local/verification_local.llm.json \
    --output docs/paper/verification_local/diff_llm_vs_local.json \
    --md docs/paper/verification_local/diff_llm_vs_local.md
```

## Version history

All verification outputs (`citation_map*.json`, `close_reads/`, `verification_local/`,
`reading_memory/`) are committed to the `feat/citation-verification-local-pipeline`
branch on GitHub (remote: `yblllll/road-climate-resilience`) so every pipeline
run is recoverable.
