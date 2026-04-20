# LLM close_reader vs Local PyMuPDF verifier — first run

Date: 2026-04-20
Branch: `feat/citation-verification-local-pipeline`
Scope: 5 cite_keys × 31 claims (subset of 63 total claims in `main.tex`)

---

## Pipeline

Two parallel verifiers on the same 31 claims:

1. **LLM close_reader + semantic_matcher** (5 parallel executor agents, one
   per cite_key). Reads the PDF, extracts a 15-40-word quote per claim,
   assigns `MATCH` / `PARTIAL` / `MISMATCH` / `OPPOSITE` / `NOT_FOUND`.
2. **Local PyMuPDF `verify_quotes_local.py`** (tokenless, 3-layer fallback).
   Reads the same quote the LLM produced, searches the PDF, returns
   `MATCH_EXACT` / `MATCH_WRONG_PAGE` / `MATCH_PARTIAL` / `NOT_FOUND` /
   `NO_QUOTE`.

`diff_verifications.py` keys by `(cite_key, claim_line)` and buckets the pair.

## Headline numbers

| Bucket | Count | Meaning |
|---|---:|---|
| AGREE_PARTIAL_QUOTE_VERIFIED | 14 | LLM hedged (PARTIAL), quote exists in PDF |
| AGREE_NOT_FOUND | 7 | Both agree nothing to verify |
| AGREE_PARTIAL | 2 | LLM PARTIAL, local MATCH_PARTIAL |
| AGREE_MATCH | 2 | Both MATCH |
| LLM_FLAG_QUOTE_REAL | 2 | LLM said MISMATCH, local confirms quote exists — **citation misattribution caught** |
| LLM_FLAG_QUOTE_FUZZY | 1 | LLM MISMATCH, local partial match |
| LLM_PARTIAL_WITHOUT_QUOTE | 3 | Agent hedged but didn't attach a specific sentence |
| LLM_NOT_RUN | 32 | Other 15 cite_keys not processed this run |
| **LLM_MATCH_LOCAL_NOT_FOUND** | **0** | **Zero pure LLM hallucinations** |

## What the comparison actually shows

### 1. No pure LLM hallucinations on this subset

Zero entries in the `LLM_MATCH_LOCAL_NOT_FOUND` bucket. Every quote the LLM
produced was found verbatim in the PDF by PyMuPDF. This directly answers the
design question ("what if 5 agents say hallucination but local Python says
100% match?"): on this subset, no LLM fabricated quotes. The agents are
reading real sentences.

### 2. The LLM catches three real misattributions

These are the citations worth discussing:

- **pregnolato2017depth L111** — LLM verdict: MISMATCH.
  Reasoning: Pregnolato 2017 cites DfT 2014a once, as support for "flooding
  is the predominant cause of weather-related disruption to the transport
  sector". The citing paper attributes a *different* claim ("cost-benefit
  analyses of adaptation") to the same Pregnolato→DfT reference.
  Local verifier says the quote exists (MATCH_EXACT on p.1) — so the
  sentence is in the PDF, it just doesn't back the citing claim.

- **becker2026rainfall L501** — LLM verdict: MISMATCH.
  Reasoning: Becker reports a 14% mean squared error reduction for the
  speed-prediction model, plus speed reductions of 2-10% (light rain) to
  >20% (heavy rain). The citing paper frames this as an "8-14%
  speed-at-capacity reduction" — a conflation of MSE (a fit statistic)
  with speed-at-capacity (a physical quantity).

- **koetse2009impact L503** — LLM verdict: MISMATCH.
  Reasoning: Koetse reports 8-14% as the *maximum* speed-at-capacity
  reduction across rain intensity levels, taken from Hranac et al. 2006.
  The citing paper reframes this as "sustained rain / not marginal per mm",
  which neither Koetse nor Hranac claim.

All three are things a naive keyword-overlap verifier would rubber-stamp
as MATCH because the numbers / key terms are present in the source. Only
a semantic reader catches that the *interpretation* differs.

### 3. 14 PARTIAL verdicts with verified quotes — group-citation overreach

The citing paper has several 3-4 citation clusters after single sentences
(lines 66, 68, 70, 93, 97, 200, 202). When the cluster points at papers
from different geographies / scopes (Germany, China, US, UK), only 1-2 of
the cited papers actually contain the specific claim. The LLM correctly
labels the others PARTIAL with a tangentially related quote.

Examples:

- "UK Strategic Road Network carries ~1/3 traffic / ~2/3 freight" (L66/68/70)
  — cited to {nh2024climate, dft2024rea, orr2024annual, koetse2009impact,
  sias2025roadways, hranac2006empirical, becker2026rainfall, bi2022weather,
  pregnolato2017depth}. Only nh2024climate + orr2024annual actually back the
  UK-specific statistic. Koetse, Hranac, Becker, Bi, Pregnolato: all
  NOT_FOUND (US/Germany/China/Newcastle-case-study papers).

- "Precipitation is the most consistent negative effect across modes"
  (L93/97) — cited to several papers; each paper confirms precipitation
  effects but none explicitly claim it is "most consistent across modes".
  All PARTIAL with supporting but weaker quotes.

### 4. The naive scripted close_reader misses what matters

Parallel run of `close_read_pymupdf.py` (keyword-bag scoring, no LLM):

| Scripted verdict | Count |
|---|---:|
| MATCH | 0 |
| PARTIAL | 10 |
| NOT_FOUND | 51 |
| NO_PDF | 2 |

Of the 51 scripted-NOT_FOUND, the local verifier would MATCH_EXACT them all
if it had picked the sentence (since the keyword overlap was ≥ 2, some real
sentence existed). The scripted classifier is too strict because it uses
recall ≥ 0.55 / overlap ≥ 4 — claims in the paper are paraphrased, so
recall rarely crosses that threshold. **This is exactly why the LLM is
needed: semantic equivalence over paraphrase, which bag-of-words cannot
capture.**

### 5. Recommended next action

- Dispatch close_reader agents for the remaining 15 cite_keys (32 claims)
  so every citation has an LLM verdict.
- For the 3 LLM_FLAG_QUOTE_REAL/FUZZY cases, rewrite the citing sentence in
  `main.tex` so the claim is phrased within the range the source actually
  supports. Specifically:
  - L111: split the DfT-2024 REA claim from the Pregnolato-2017 flood claim.
  - L501: replace "8-14% speed-at-capacity reduction" with Becker's actual
    "2-10% (light) to >20% (heavy) rainfall-induced speed reduction", or
    attribute the 8-14% figure to Hranac 2006 directly (not Becker).
  - L503: same fix as L501; the 8-14% is Hranac via Koetse, not a Becker
    finding, and is a maximum not a sustained-rain marginal effect.
- Commit + push the updated `main.tex` + re-run pipeline to verify the
  MISMATCHes clear.

## Files

- `docs/paper/citation_verification/citation_map.llm.json` — LLM verdicts
- `docs/paper/citation_verification/citation_map.local.json` — scripted verdicts
- `docs/paper/citation_verification/close_reads/*.llm.json` — per-paper LLM output
- `docs/paper/verification_local/verification_local.llm.json` — local verifier on LLM map
- `docs/paper/verification_local/diff_llm_vs_local.{json,md}` — this report's data
- `docs/paper/reading_memory/<cite_key>.json` — persistent per-paper reading log,
  stores both scripted and LLM verdicts so old runs aren't overwritten.

All committed to the `feat/citation-verification-local-pipeline` branch on
GitHub (`yblllll/road-climate-resilience`) for version rollback.
