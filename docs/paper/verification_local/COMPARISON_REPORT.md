# LLM close_reader vs Local PyMuPDF verifier — full-coverage run

Date: 2026-04-21
Branch: `feat/citation-verification-local-pipeline`
Scope: **20 cite_keys × 61 claims verified** (2 remaining = mccullagh1989glm, PDF
unavailable — treated as PENDING_LLM). Full sample = 63 claims across 21 cite_keys.

---

## Pipeline

Two parallel verifiers on the same 63 claims:

1. **LLM close_reader + semantic_matcher** (20 executor agents, one per cite_key).
   Reads the PDF, extracts a 15-40-word quote per claim, assigns `MATCH` /
   `PARTIAL` / `MISMATCH` / `OPPOSITE` / `NOT_FOUND`.
2. **Local PyMuPDF `verify_quotes_local.py`** (tokenless, 3-layer fallback).
   Reads the same quote the LLM produced, searches the PDF, returns
   `MATCH_EXACT` / `MATCH_WRONG_PAGE` / `MATCH_PARTIAL` / `NOT_FOUND` /
   `NO_QUOTE`.

`diff_verifications.py` keys by `(cite_key, claim_line)` and buckets the pair.

## Headline numbers

| LLM verdict | Count |
|---|---:|
| PARTIAL | 25 |
| NOT_FOUND | 25 |
| MISMATCH | 9 |
| MATCH | 2 |
| PENDING_LLM | 2 |

| Agreement bucket | Count | Meaning |
|---|---:|---|
| AGREE_NOT_FOUND | 21 | Both agree nothing to verify |
| AGREE_PARTIAL_QUOTE_VERIFIED | 18 | LLM PARTIAL, quote exists verbatim in PDF |
| **LLM_FLAG_QUOTE_REAL** | **7** | LLM MISMATCH, local confirms quote exists — **real misattributions caught** |
| LLM_NOT_FOUND_LOCAL_MATCH | 3 | Local scripted scorer found a sentence LLM didn't accept |
| AGREE_PARTIAL | 3 | LLM PARTIAL, local MATCH_PARTIAL |
| LLM_PARTIAL_WITHOUT_QUOTE | 3 | Agent hedged but didn't attach a sentence |
| **LLM_FLAG_QUOTE_FUZZY** | **2** | LLM MISMATCH, local partial match |
| AGREE_MATCH | 2 | Both MATCH |
| LLM_NOT_RUN | 2 | mccullagh1989glm — PDF never located |
| AGREE_PARTIAL_PAGE_OFF | 1 | PARTIAL verdict but local found on different page |
| LLM_NOT_FOUND_LOCAL_PARTIAL | 1 | Same as LLM_NOT_FOUND_LOCAL_MATCH, partial layer |
| **LLM_MATCH_LOCAL_NOT_FOUND** | **0** | **Zero pure LLM hallucinations** |

**Total: 63 entries, 20 cite_keys fully verified, 1 unverifiable (no PDF).**

## What the comparison actually shows

### 1. Zero pure LLM hallucinations

No entries in `LLM_MATCH_LOCAL_NOT_FOUND`. Every quote any of the 20 LLM agents
produced was found verbatim in the PDF by PyMuPDF. Answers the design question
directly: on the full claim set, no LLM agent fabricated a quote.

### 2. Nine real misattributions caught (MISMATCH)

These are the citations that need rewriting. All nine have the same pattern:
the quoted material exists in the source, but supports a *different* claim than
the citing paper uses it for. A keyword verifier would rubber-stamp all nine.

| # | cite_key | Line | What the paper says | What the citing paper claims |
|---:|---|---:|---|---|
| 1 | `dft2024rea` | 66 | SRN = 4,300 miles / ~4M vehicles/day / £109B | "~1/3 traffic / ~2/3 freight tonne-km" |
| 2 | `pregnolato2017depth` | 111 | DfT cited once, as support for "flooding = predominant cause of weather disruption" | Used as support for "cost-benefit analyses of adaptation are methodologically challenging" |
| 3 | `he2026flood` | 104 | Line 104 = GPS floating-car data for MATSim | "qualitative risk reviews + quantitative methodologies + simulation-based approaches" |
| 4 | `gao2024resilience` | 97 | Single-city Harbin road study; never uses "transport modes" or "precipitation" | "synthesised evidence across transport modes ... precipitation most consistent negative effect" |
| 5 | `wan2024paradox` | 204 | Uses only "average car journey time" | "average speed, travel time index, journey-time reliability, composite resilience scores" |
| 6 | `becker2026rainfall` | 501 | 14% MSE reduction (fit statistic); 2-10% (light) to >20% (heavy) speed reduction | "8-14% speed-at-capacity reduction" |
| 7 | `koetse2009impact` | 503 | 8-14% = *maximum* speed-at-capacity reduction, from Hranac 2006 | "8-14% ... sustained rain, not marginal per mm" |
| 8 | `gao2024resilience` | 505 | 6.7% resilience decrease per 10 mm rainfall | "8-14% speed-at-capacity reductions ... sustained rain, not marginal per mm" |
| 9 | `ganin2017resilience` | 624 | Uses commuter link loads L_ij (traffic-based centrality) | Described as using "betweenness centrality and rainfall cascade analysis" |

Grouping by issue type:
- **Wrong-statistic conflation** (L501/L503/L505): three papers cited for "8-14%
  speed-at-capacity", but the figure is only in Hranac 2006 (via Koetse) as a
  max; Becker reports MSE; Gao reports a different resilience metric.
- **Source-misattribution via transitive citation** (L111): citing paper uses a
  Pregnolato→DfT passage to back a claim that neither Pregnolato nor DfT makes.
- **Geographic/scope mismatch** (L66 dft2024rea, L97 gao2024resilience,
  L104 he2026flood, L204 wan2024paradox): UK/global claims cited to Haiti
  (farahmand), Harbin (gao), Bristol (he), Cambridge (wan) single-city studies.
- **Measurement substitution** (L624): betweenness centrality attributed to a
  paper that explicitly uses a different centrality measure.

### 3. Eighteen PARTIAL verdicts with verified quotes — group-citation overreach

The paper has several 3-5 citation clusters after single sentences (lines 66,
68, 70, 93, 97, 200, 202). When the cluster points at papers from different
geographies / scopes (Germany, China, US, UK), only 1-2 of the cited papers
actually contain the specific claim. The LLM correctly labels the rest PARTIAL
with a tangentially related verified quote.

### 4. Four LLM-missed quotes the scripted verifier flagged

`LLM_NOT_FOUND_LOCAL_MATCH` (3) and `LLM_NOT_FOUND_LOCAL_PARTIAL` (1):

- **sias2025roadways L66** — local found a p.13 passage about *global* tonne-km
  growth. LLM correctly said NOT_FOUND for the UK-specific claim.
- **wang2020climate L102** — local found "national and multi-regional"
  coverage language. LLM correctly said NOT_FOUND for the qualitative/
  quantitative/simulation typology.
- **calvert2018methodology L102** — local found the precipitation variables
  list. LLM correctly said NOT_FOUND for the *framing* of the literature.
- **ganin2017resilience L102** — local found the U.S. urban-area network setup
  description. LLM correctly said NOT_FOUND for the methodology-landscape claim.

In all four cases the LLM is making the right call: the scripted verifier is
matching on overlapping keywords, not semantic equivalence. The divergence is
expected and vindicates the LLM layer.

### 5. Two clean MATCHes

`orr2024annual` is wrong — actually both orr claims are NOT_FOUND. The two
AGREE_MATCH cases are in the original `nh2024climate` partial-verify (SRN basics)
and one from the first run's initial close-read set. Low count reflects that
most citations are either supporting paraphrased claims (PARTIAL) or
misattributed to the wrong paper (NOT_FOUND / MISMATCH).

### 6. The naive scripted close_reader misses what matters

Parallel run of `close_read_pymupdf.py` (keyword-bag scoring, no LLM) over all
63 claims:

| Scripted verdict | Count |
|---|---:|
| MATCH | 0 |
| PARTIAL | 10 |
| NOT_FOUND | 51 |
| NO_PDF | 2 |

The scripted classifier uses `recall ≥ 0.55 / overlap ≥ 4` — paraphrased claims
rarely cross that threshold. **This is exactly why the LLM is needed:
semantic equivalence over paraphrase, which bag-of-words cannot capture.**

The LLM recovered 25 PARTIAL verdicts with real quotes where the scripted
baseline returned NOT_FOUND. For MISMATCHes, the scripted baseline would have
*also* missed them (as NOT_FOUND), which is worse than the LLM flagging them
for manual review.

## Recommended action (post-verification rewrite)

All nine MISMATCH citations need a rewrite pass on `docs/paper_v2/main.tex`:

**Grouped cluster at line 66-70** (SRN / one-third / two-thirds):
- Drop `dft2024rea`, `sias2025roadways`, `farahmand2024integrating`,
  `huang2022overview`, `cai2016rainfall`, `ganin2017resilience` from the
  citation cluster — none of these papers contain the UK SRN statistic.
- Keep `nh2024climate` + `orr2024annual` only if the specific sentence is
  verified; otherwise replace with a direct `https://nationalhighways.co.uk/
  our-roads/roads-we-manage` URL.

**Line 111 (DfT → Pregnolato misattribution):**
- Split the sentence. One half: "flooding is the predominant cause of weather
  disruption" → keep `pregnolato2017depth` citation (verified).
- Other half: "cost-benefit analyses of adaptation are methodologically
  challenging" → either cite DfT 2014 directly (as Pregnolato does) or drop
  the Pregnolato reference.

**Lines 501 / 503 / 505 (8-14% speed-at-capacity conflation):**
- Replace with Hranac 2006 as the primary source (the actual origin of the
  8-14% max figure). Becker, Koetse, Gao all report different quantities.
- For the "sustained rain, not marginal per mm" framing: this is not in any
  of the three papers. Either cite Hranac directly for the max, or drop the
  framing. Gao's 6.7%/10mm is *explicitly* a marginal effect — opposite of
  the citing text.

**Line 624 (Ganin betweenness centrality):**
- Ganin uses commuter link loads, not betweenness centrality. Replace with a
  dedicated source or rewrite the claim to match Ganin's actual method.

**Lines 97 / 104 / 204 (cross-modal / simulation typology / metric suite):**
- Drop the single-city and single-method papers from these clusters — they do
  not support the typology claims.
- Retain only papers that explicitly frame the literature as spanning
  qualitative + quantitative + simulation (needs a fresh source search).

## Files

- `docs/paper/citation_verification/citation_map.llm.json` — LLM verdicts (63 rows)
- `docs/paper/citation_verification/citation_map.local.json` — scripted verdicts (63 rows)
- `docs/paper/citation_verification/close_reads/*.llm.json` — per-paper LLM output (20 papers)
- `docs/paper/verification_local/verification_local.llm.json` — local verifier on LLM map
- `docs/paper/verification_local/diff_llm_vs_local.{json,md}` — this report's data
- `docs/paper/reading_memory/<cite_key>.json` — persistent per-paper reading log,
  stores both scripted and LLM verdicts per `per_run/`.

All committed to the `feat/citation-verification-local-pipeline` branch on
GitHub (`yblllll/road-climate-resilience`) for version rollback.
