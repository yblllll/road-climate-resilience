# Paper Quality Audit Report
**Target**: Transportation Research Part D (TRD)
**Date**: 2026-03-28

---

## CRITICAL Issues (Must Fix Before Submission)

1. **Placeholder text at lines 269-272** — "to be reported from Stata" for Deviance, AIC, BIC, Log pseudolikelihood. Will be desk-rejected.
2. **No spatial coefficient map** — Paper is called "Estimate-Map-Explain" but has NO map figure. The "Map" stage is entirely missing visually.

## HIGH Priority

3. **No study area map** — Must show Cambridgeshire SRN with link locations and weather stations
4. **Betweenness centrality results are qualitative** — No numbers, no figure, no table. Section 4.4 is narrative only.
5. **Only 25 references** — TRD expects 40-60. Six .bib entries exist but are never cited (wan2025, zhou2026, li2024, liu2026, raccagni2024, pulugurtha2021)
6. **Platform description too long** — ~700 words on hex colors, sparse matrices, chunk sizes. Reads like a README, not a paper. Trim by ~400 words.

## MEDIUM Priority

7. **Generated regressors problem** — Solution (WLS) is partial. Need Murphy-Topel or bootstrap SE correction. Cite Pagan (1984).
8. **No model diagnostics** — No residual plots, VIF table, overdispersion test, specification comparison
9. **AI-sounding/promotional language** — "fills a critical gap", "rapid, lightweight, and fully replicable", "powerful lens", "double jeopardy", "defining contribution"
10. **Robustness checks mentioned but not shown** — "yields qualitatively similar" without a table

## Current State

| Metric | Current | TRD Standard |
|--------|---------|-------------|
| Word count | ~6,500 | 7,000-10,000 |
| References | 25 | 40-60 |
| Figures | 1 | 5-8 |
| Tables | 3 (1 incomplete) | 3-5 |
| Maps | 0 | 2-3 |

## Worst 10 Sentences

1. Hex color codes (#00295e, #4CAF50) in paper — DELETE
2. "sparse matrix...28 GB to 200 MB...15-20 minutes" — Software README not paper
3. "rapid, lightweight, and fully replicable" — Promotional stacking
4. "double jeopardy" — Colloquial, legal term
5. "defining contribution" — Self-aggrandizing
6. "deliberate design choice" — Redundant
7. "[to be reported from Stata]" x4 — PLACEHOLDERS
8. "powerful lens" — Journalistic
9. "remarkably thin" — Informal intensifier
10. "template for...adopted nationwide" — Overstated from single-county study

## Missing Figures (Essential)

1. Study area map with links + weather stations
2. Spatial map of precipitation sensitivity coefficients
3. Betweenness centrality map (normal vs extreme)
4. Platform screenshot(s)
5. Speed-precipitation relationship plot
6. Model diagnostics (residuals, Q-Q)
7. Temporal patterns (dry vs wet day speed profiles)
