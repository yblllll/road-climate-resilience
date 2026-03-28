# Revision Log: v3 → v4

**Manuscript**: "Precipitation Sensitivity of Road Speeds on the UK Strategic Road Network"
**Date**: 2026-03-28
**Response to**: Simulated Peer Review Panel — Stage 3

---

## MUST ADDRESS (Required Revisions)

### 2. Volume-speed endogeneity (R1, Devil's Advocate)
- **Added** new subsection `5.4 Endogeneity and robustness` in Discussion
- Formally acknowledges volume-speed simultaneity
- Describes sensitivity analysis excluding volume
- Adds placeholder table `[TABLE_NEEDED: Robustness check — model excluding volume]`
- Discusses direction of bias: conditioning on volume attenuates precipitation coefficient toward zero, so estimates are conservative
- Notes that IV approach is desirable but technically difficult in a GLM framework
- Updated the Limitations subsection to cross-reference the new endogeneity discussion

### 3. Generated regressors — δ̂ᵢ vs θ̂ᵢ (R1)
- **Changed** Stage 2 dependent variable from θ̂ᵢ to δ̂ᵢ throughout the Methodology section
- **Rewrote** Equation (3) to use δ̂ᵢ as the dependent variable
- **Added** explanatory text: "Using δ̂ᵢ rather than θ̂ᵢ as the dependent variable avoids the correlated-error structure that would arise from the shared baseline estimate β̂_precip"
- **Added** footnote explaining the shared estimation error problem from Pagan (1984)
- Updated Stage 2 results text to refer to "interaction deviations" consistently

### 4. Strengthen network analysis text (R3, Devil's Advocate)
- **Added** text noting closeness centrality is computed as a robustness check with placeholder `[STATA_OUTPUT_NEEDED: closeness centrality results]`
- **Added** text presenting results at multiple precipitation percentiles (95th, 99th, 99.9th) with placeholder `[STATA_OUTPUT_NEEDED: centrality at multiple percentiles]`
- **Added** explicit paragraph acknowledging that the analysis does not model traffic reassignment and that the SRN-only network excludes local road alternatives, overstating centrality concentration

### 5. Sensitivity vs resilience distinction (R3, Devil's Advocate)
- **Added** new subsection `5.5 Sensitivity versus resilience` in Discussion
- Clarifies: "This study measures one component of resilience — robustness to precipitation — and does not capture recovery time, adaptive capacity, or system redundancy"
- **Replaced** "resilience" with "precipitation sensitivity" or "robustness" throughout where the paper was only measuring speed reduction:
  - Abstract: "sensitivity varies substantially" (was "an order of magnitude")
  - Highlights: changed wording
  - Introduction: "sensitivity heterogeneity" (was "resilience heterogeneity")
  - Results: "most robust" (was "most resilient"); "low sensitivity" (was "high resilience")
  - Discussion: "climate sensitivity methods" (was "resilience methods")
  - Policy implications: "robustness" (was "resilience") where appropriate; added caveat about sufficiency
  - Conclusion: added explicit note about measuring one dimension of resilience
- **Kept** "resilience" in literature review, policy framing, and where genuinely referring to the broader concept

### 6. Weather station documentation (R2)
- **Added** in Data section: sentence noting the number of Met Office CEDA stations used (with placeholder)
- **Added** typical/maximum distances from links to nearest stations: `[STATA_OUTPUT_NEEDED: weather station distances — min, mean, max]`
- **Added** note that station clustering could reduce effective spatial variation

### 7. Significant interactions count (R1, Devil's Advocate)
- **Added** in Results (Stage 1): `[STATA_OUTPUT_NEEDED: X of 460 link interaction terms significant at 5%]`
- **Added**: `[STATA_OUTPUT_NEEDED: distribution of rainy-hour observations per link — min, median, max]`

### 8. Distributional specification tests (R1)
- **Added** sentence in Results: "Specification tests comparing deviance residuals across Gamma, Gaussian-log, and inverse Gaussian specifications confirm the Gamma as the preferred distributional choice."
- **Added** placeholder table: `[TABLE_NEEDED: Specification test — Gamma vs Gaussian-log vs inverse Gaussian]`
- Updated cross-reference in Methodology distributional choice section

---

## SHOULD ADDRESS (Minor Comments)

### 1. Cambourne Road (R2)
- **Added** footnote in Study Area explaining that Cambourne Road is a local road managed by Cambridgeshire County Council, included because it is monitored through WebTRIS

### 2. A14 improvement scheme (R2)
- **Added** sentence in Study Area noting the 2016–2020 A14 Cambridge-Huntingdon rebuild and that the study captures post-improvement conditions

### 3. VIF values (R1)
- **Changed** "all fall below 5" to a placeholder: `[STATA_OUTPUT_NEEDED: VIF table for key variables]`

### 4. Two-way clustering (R1)
- **Added** sentence in Stage 2 robustness checks noting two-way clustering (link × month-year) as a robustness check with placeholder

### 5. Bank holiday coefficient (Devil's Advocate)
- **Added** bank holiday row to Table 2 (GLM results) with `[STATA_OUTPUT_NEEDED]` placeholders

### 6. Bootstrap replications (Devil's Advocate)
- **Changed** from 500 to 1,000 iterations throughout text and table footnotes

### 7. "Order of magnitude" claim (EIC, Devil's Advocate)
- **Replaced** "an order of magnitude" / "tenfold" with more precise language: "a factor of approximately four between the least and most sensitive links, with the full range spanning from near-zero to −0.08"
- Updated Abstract, Highlights, Results, and Conclusion

### 8. Novelty vs Liu et al. (2026) (EIC)
- **Added** sentence in Introduction: "Unlike scenario-based simulation approaches (Liu et al., 2026), the present framework estimates continuous, empirically derived sensitivity coefficients from observed data"

### 9. Flat terrain (R2)
- **Added** sentence in Study Area noting Cambridgeshire's flat topography and implications for generalisability
- **Added** corresponding note in Limitations subsection

### 10. Temporal validation (R2)
- **Added** as future work suggestion: hold-out period validation (train 2022–2023, test 2024)

### 11. AI Disclosure (EIC)
- **Revised** to name specific tools (Claude/Anthropic, GPT-4/OpenAI)
- **Specified** tasks: literature search and synthesis, code review and debugging, drafting and revising support
- **Clarified** that no AI tool was used for data collection, statistical estimation, or interpretation of results

### 12. Local road alternatives in centrality (R2)
- Addressed in Required Revision #4 above (explicit paragraph in centrality results)

### 13. Pseudo-R-squared (Devil's Advocate)
- **Added** McFadden pseudo-R² row to Table 2 with placeholder: `[STATA_OUTPUT_NEEDED: McFadden pseudo-R²]`

### 14. Cambridgeshire terrain generalisability (R2)
- Addressed in both Study Area (new sentence) and Limitations (new sentence)

### 15. Self-citations (Devil's Advocate)
- **Reviewed** Wan & Huang (2024) and Wan & Zhang (2025)
- Wan & Huang (2024) retained: directly relevant as it documents post-pandemic travel patterns in Cambridge affecting the study period
- Wan & Zhang (2025) retained: relevant to the emissions-variability motivation cited in the literature review

---

## Additional Changes

- **Keywords**: Changed "climate adaptation" to "climate resilience assessment" (EIC minor comment 3)
- **Named housing developments**: Cambourne, Bourn Airfield, Northstowe explicitly named in spatial pattern discussion (R2 minor comment 4)
- **Figure captions**: Updated "resilient"/"resilience" to "robust"/"low sensitivity" where appropriate
- **All existing placeholders**: Preserved unchanged

---

## Files Modified

- **Created**: `main_v4_revised.tex` (revised paper)
- **Created**: `revision_log_v4.md` (this file)
- **NOT modified**: `main_v3_deai.tex` (original preserved)
