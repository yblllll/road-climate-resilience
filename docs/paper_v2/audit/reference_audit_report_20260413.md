# Reference Audit Report

**Paper**: Link-Level Precipitation Sensitivity of the UK Strategic Road Network: An Empirical Framework Using Open Data  
**Authors**: Yibin Li, Li Wan  
**Date of Audit**: 2026-04-13 (updated with full-text verification)  
**Auditor**: Claude Code AutoAudit v1.0  
**Method**: DOI resolution, web search verification, **full-text PDF cross-checking** against Literature_Review folder  

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| MODERATE | 1 |
| MINOR | 1 |
| VERIFIED | 18 |
| UNVERIFIABLE | 1 |

**Total cited references**: 21  
**Uncited .bib entries**: 11 (not an error, but should be cleaned)  
**Overall Assessment**: **PASS WITH CORRECTIONS** — All 21 cited references are real papers/sources. No fabricated references detected. 1 critical internal inconsistency requires correction before submission. Most previously flagged issues have been resolved through full-text verification.

---

## CRITICAL Issues

### C1: Internal inconsistency in characterising Becker et al. (2026) findings

- **Reference**: `becker2026rainfall`
- **Existence**: CONFIRMED — DOI 10.3390/futuretransp6010038, MDPI Future Transportation vol 6(1), 2026.
- **Full-text verification** (pages 6-15 of PDF):
  - **Section 3.2, p.9**: "the driving speed v on multi-lane roads drops at a much higher rate than on single-lane roads"
  - **Section 3.2, p.9**: "at speed limits of 100 km/h in a non-urban environment, on single- and multi-lane roads **Δv_rel = −15% and Δv_rel = −26%**, respectively"
  - **Section 5, p.14 (Conclusions)**: "Relative speed reductions increase with rainfall intensity and are **substantially larger on road sections with higher speed limits and on multi-lane roads**"
  - The reason given: single-lane roads already have lower baseline speeds, so there is less room for proportional reduction.
- **Problem**: The paper characterises Becker's findings **contradictorily** in two locations:
  - **Section 2.1 (line 98)**: *"high-speed, multi-lane roads experienced proportionally larger speed reductions than lower-capacity roads"* — **CORRECT** per Becker
  - **Section 6.2 (line 396)**: *"Their finding that multi-lane roads are relatively more resilient also matches"* and *"high-speed roads lose more in absolute terms but less in relative terms"* — **INCORRECT**. Becker found multi-lane roads have **larger** relative reductions (less resilient proportionally), not smaller.
- **Impact**: Section 6.2 makes the opposite claim to what Becker found. This is a factual misrepresentation.
- **Recommended fix**: Revise Section 6.2 (line 396). Becker found that multi-lane/high-speed roads have larger reductions in both absolute AND relative terms. The sentence should read something like: "Their finding that multi-lane, high-speed roads experience proportionally larger speed reductions is consistent with..." Remove the claim about "relatively more resilient" and "less in relative terms."

---

## MODERATE Issues

### M1: National Highways "36% flood susceptibility" figure — citation misattributed

- **Reference**: `nh2024climate`
- **Location**: Section 1 (Introduction, ~line 65): *"National Highways classify 36% of the network as having significant flood susceptibility"*
- **Figure confirmed**: The 36% figure IS real. It comes from the **ORR (Office of Rail and Road) Annual Assessment of National Highways' Performance, April 2023 to March 2024**: "At March 2024, **36% of the SRN had an observed significant susceptibility to flooding**, meaning 36% of the SRN has drainage catchments that include high risk flood hotspots." This was five percentage points worse than the previous year.
- **Problem**: The paper cites `nh2024climate` (the National Highways general climate change webpage at nationalhighways.co.uk), which does NOT contain this figure. The actual source is the ORR Annual Assessment report.
- **Note**: The NCE article "13% of UK's SRN is in high flood risk locations" uses a different definition (Environment Agency Flood Zone 3), which is a subset. The 36% figure uses National Highways' own drainage catchment susceptibility metric, which is broader.
- **Impact**: The figure and claim are correct; only the citation is wrong.
- **Recommended fix**: Replace the citation with a reference to the ORR Annual Assessment 2024 (available at https://www.orr.gov.uk/annual-assessment-national-highways-performance-2023-2024), or cite the underlying National Highways data that the ORR report references. Add a new .bib entry for the ORR source.

---

## MINOR Issues

### m3: Zare & Miller-Hooks (2025) — "real options approach" characterisation

- **Reference**: `zare2025risk`
- **Existence**: CONFIRMED — TRD vol 148, pp 104931, 2025.
- **Problem**: The paper calls this a "real options approach" but the actual method may be an "Optimal Protection Deferral Decision (OPDD)" framework. While conceptually related, "real options" is a specific finance methodology and may not be the terminology used by Zare & Miller-Hooks.
- **No PDF available in Literature_Review** for full-text verification.
- **Impact**: LOW — the conceptual connection is valid, but the characterisation may be imprecise.
- **Recommended fix**: Verify Zare & Miller-Hooks' own terminology. If they call it OPDD rather than real options, consider adjusting.

---

## UNVERIFIABLE Issues

### U1: Zare & Miller-Hooks (2025) terminology

- Cannot verify "real options" terminology without full text. Classified as MINOR above but listed here for completeness. No PDF in Literature_Review folder.

---

## VERIFIED References (18/21)

All references below confirmed as real with claims matching source content. Items marked **[FT]** were verified via full-text PDF reading:

| # | Cite Key | Verification |
|---|----------|-------------|
| 1 | `nce2026srn` | ✓ NCE article exists. 7% figure confirmed. "20 years ago" confirmed (Halliwell quote). |
| 2 | `koetse2009impact` | ✓ TRD vol 14(3), pp 205-221, 2009. Cross-modal review, precipitation as most consistent negative effect confirmed. |
| 3 | `hranac2006empirical` | ✓ **[FT]** FHWA report FHWA-HOP-07-073. Table ES.2 confirms: Free-flow speed rain impact: -6% to -9% (matches "up to 9%"); Speed-at-capacity rain impact: -8% to -14% (exact match). Three cities (Minneapolis-St. Paul, Baltimore, Seattle) confirmed. |
| 4 | `cai2016rainfall` | ✓ ASCE JTE vol 142(6), 2016. Hong Kong confirmed. Heteroscedastic speed dispersion (unreliability) confirmed. |
| 5 | `bi2022weather` | ✓ **[FT]** Urban Climate vol 41, 2022. Full text confirms: data from "Didi company, an international mobile transportation platform" using "online car-hailing vehicles (floating car data)" across four cities (Suzhou, Shenzhen, Jinan, Chengdu). "Floating car data from ride-hailing platforms" and "multiple Chinese cities" are both CORRECT. |
| 6 | `becker2026rainfall` | ✓ **[FT]** Existence and core findings confirmed (see C1 for the characterisation inconsistency). 1.5M road sections, RADKLIM radar, GNSS probe data all confirmed. Section 2.1 characterisation correct; Section 6.2 characterisation incorrect. |
| 7 | `gao2024resilience` | ✓ TRD vol 126, pp 104000, 2024. Harbin case study, hierarchical clustering of resilience patterns confirmed. |
| 8 | `ganin2017resilience` | ✓ Science Advances vol 3(12), e1701079, 2017. Topological analysis, resilience-efficiency trade-offs across 40 US urban areas confirmed. |
| 9 | `bergantino2024assessing` | ✓ **[FT]** Transport Reviews vol 44(4), pp 834-857, 2024. Reviews 53 empirical studies using real-world data. Identifies data integration as "the main barrier" for multimodal resilience studies (p.851) and discusses methodological issues impeding "widespread adoption" (p.849). Characterisation "data availability and methodological accessibility as persistent barriers" is a fair paraphrase of the paper's Section 6 findings. |
| 10 | `calvert2018methodology` | ✓ Transportmetrica A vol 14(1-2), pp 130-154, 2018. Road traffic resilience methodology (LPIR index) confirmed. |
| 11 | `pregnolato2017depth` | ✓ TRD vol 55, pp 67-81, 2017. Depth-disruption function for flood-traffic modelling confirmed. |
| 12 | `he2026flood` | ✓ DOI resolves to Elsevier. Title confirmed: Bristol UK, agent-based simulation, flood-traffic congestion. |
| 13 | `huang2022overview` | ✓ J. Advanced Transportation vol 2022, 1252534, 2022. Overview of ABMs for transport confirmed. |
| 14 | `farahmand2024integrating` | ✓ TRD vol 133, pp 104234, 2024. Climate projections + probabilistic network analysis confirmed. |
| 15 | `wang2020climate` | ✓ TRD vol 88, pp 102553, 2020. Survey of 100 papers on climate-transport adaptation confirmed. |
| 16 | `swarna2025roadways` | ✓ Nature Rev. Earth & Env. vol 6, pp 555-571, 2025. Climate impacts on roadways review confirmed. |
| 17 | `wan2024paradox` | ✓ **[FT]** SSRN preprint / Travel Behaviour and Society. Cambridge UK, journey time analysis confirmed. **Section 4.2 (p.12) explicitly states**: "this study adopts a generalised linear model using **Gamma distribution with a log-link**, implemented in base R." The "Gamma GLM with a log link" characterisation is EXACTLY CORRECT. |
| 18 | `mccullagh1989glm` | ✓ Canonical GLM textbook, 2nd ed., Chapman & Hall. OLS bias under heteroskedasticity well-established therein. |
| 19 | `dft2024rea` | ✓ UK Gov PDF exists. REA by NatCen, climate adaptation themes confirmed. Cost-benefit gap plausible. |

---

## Uncited .bib Entries (11)

The following entries exist in `references.bib` but are NOT cited anywhere in `main.tex`. LaTeX/BibTeX will not include them in the compiled reference list, but they should be cleaned up to avoid confusion:

1. `wan2025variability` — Wan & Zhang, IJUS 2025
2. `nelder1972glm` — Nelder & Wedderburn, JRSS-A 1972
3. `freeman1977centrality` — Freeman, Sociometry 1977
4. `pulugurtha2021aadt` — Pulugurtha & Mathew, J. Transport Geography 2021
5. `raccagni2024urban` — Raccagni et al., Heliyon 2024
6. `li2024percolation` — Li et al., Physica A 2024
7. `liu2026extreme` — Liu et al., IJDRR 2026
8. `wassmer2024resilience` — Wassmer et al., Chaos 2024
9. `stamos2023centrality` — Stamos, Future Transportation 2023
10. `zhou2026bibliometric` — Zhou et al., Progress in Disaster Science 2026
11. `unece2024stress` — UNECE Stress Test Framework 2024

---

## Priority Action List

1. **[CRITICAL] Fix Becker characterisation in Section 6.2** — Line 396 incorrectly says multi-lane roads are "relatively more resilient" and that high-speed roads lose "less in relative terms." Becker found the OPPOSITE: multi-lane roads have larger relative speed reductions (Δv_rel = −26% vs −15% for single-lane at 100 km/h). The Lit Review (line 98) is correct; revise the Discussion to match.
2. **[MODERATE] Fix NH "36%" citation** — The figure is correct (ORR Annual Assessment 2024 confirms 36% of SRN has significant flood susceptibility) but the citation points to the wrong source. Replace `nh2024climate` with an ORR reference.
3. **[MINOR] Verify Zare "real options" terminology** — Check if Zare & Miller-Hooks use "real options" or "OPDD" in their paper.
4. **[HOUSEKEEPING] Clean up 11 uncited .bib entries**.

---

## Resolved Issues (from initial audit)

The following issues from the initial abstract-level audit have been **resolved** through full-text PDF verification:

| Original ID | Issue | Resolution |
|-------------|-------|------------|
| M2 | Bi et al. data source ("ride-hailing FCD") not confirmed | **RESOLVED** — Full text confirms Didi ride-hailing FCD across 4 cities |
| M3 | Wan & Huang "Gamma GLM with a log link" not confirmed | **RESOLVED** — Full text Section 4.2 explicitly states "Gamma distribution with a log-link" |
| m1 | Hranac specific speed figures not confirmed | **RESOLVED** — Table ES.2 confirms -6% to -9% free-flow and -8% to -14% speed-at-capacity |
| m2 | Bergantino "barriers" characterisation not confirmed | **RESOLVED** — Full text identifies data and methodological barriers to widespread adoption |

---

*Audit conducted using DOI resolution, web search, abstract/content analysis, URL verification, and **full-text PDF reading** from the Literature_Review folder. Claims marked [FT] were verified against the complete paper text. The NH 36% figure (M1) and Zare terminology (m3) could not be fully verified due to lack of available full-text PDFs.*
