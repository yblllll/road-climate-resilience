# QA Critic Audit: Wan 2024 — The Paradox of Post-Pandemic Travel

**Auditor**: Critic Agent (Opus 4.6)  
**Date**: 2026-03-27  
**Paper**: Wan, L. & Huang, B. (2024). "The paradox of post-pandemic travel: Reduced car travel but unabated congestion? Insights from Cambridge, UK." SSRN Preprint.  
**Annotation key**: `Wan_2024_Paradox_Post_Pandemic_Travel.pdf`  
**Mode**: ADVERSARIAL (escalated — see Verdict Justification)

---

## VERDICT: REVISE

**Overall Assessment**: The annotations capture the paper's high-level narrative but systematically omit critical statistical methodology details that make this paper valuable for the user's own Gamma GLM + NB research. The method annotations miss the Gamma GLM specification entirely, the NB implementation details, diagnostic test results, sample sizes, and the software/packages used. Key quantitative findings in the conclusion are truncated. For the single most important paper in the literature review — from the same DARe project using the same statistical approach — this level of coverage is insufficient.

---

## Phase 1 — Pre-commitment Predictions

Before reading, I predicted these likely annotation gaps for a transport statistics paper:

1. **Model specification details omitted** — GLM family, link function, software/package not captured. CONFIRMED.
2. **Diagnostic test results missing** — overdispersion tests, Breusch-Pagan results not quantified. CONFIRMED.
3. **Key numbers truncated in annotations** — percentage changes cut off mid-sentence. CONFIRMED.
4. **Control variable list incomplete** — the full set of controls likely not enumerated. PARTIALLY CONFIRMED (controls are mentioned but not systematically annotated).
5. **Sample sizes / observation counts missing** — N for each model not captured. CONFIRMED.

All 5 predictions were confirmed or partially confirmed — this triggered escalation to ADVERSARIAL mode at Phase 2.

---

## Critical Findings

### C1. Gamma GLM with log-link specification is COMPLETELY ABSENT from method annotations

- **Confidence**: HIGH
- **Evidence**: Paper page 13 (PDF page 14) states: "this study adopts a generalised linear model using Gamma distribution with a log-link, implemented in base R." The method annotations contain ZERO entries about the Gamma GLM. The 6 method annotations cover: (1) camera aggregation x2, (2) accident controls, (3) Poisson overdispersion test, (4) Poisson as starting point, (5) Breusch-Pagan test. None mention "Gamma", "log-link", or "GLM" for journey time.
- **Why this matters**: This is the user's own statistical approach. The Gamma GLM specification is the single most directly relevant methodological detail in the entire literature review. Without it, the annotation fails its primary purpose of supporting the user's paper.
- **Fix**: Add method annotation: "Following the literature on journey time modelling (Arezoumandi, 2011; Guessous et al., 2014; Polus, 1979), this study adopts a generalised linear model using Gamma distribution with a log-link, implemented in base R." (page 13, Section 4.2)

### C2. Negative Binomial model specification and implementation details missing

- **Confidence**: HIGH
- **Evidence**: Paper page 12-13 (PDF pages 13-14) states: "This paper adopts the NB modelling approach, implemented in R using version 7.3-60.0.1 of the MASS package." The annotations mention Poisson as starting point and overdispersion testing but never capture the actual NB adoption decision, the software (R), or the package (MASS v7.3-60.0.1).
- **Why this matters**: For replicability and for citing this paper's methods in the user's own work, the specific implementation matters. The user needs to know Wan used R/MASS, not Stata, which is what the user uses.
- **Fix**: Add method annotation capturing the NB model adoption and R/MASS implementation detail from page 12.

### C3. Key quantitative conclusion numbers are truncated — the 12.0% figure is cut off

- **Confidence**: HIGH
- **Evidence**: Conclusion annotation 5 reads: "daily average journey time on key transport corridors has increased by 12." — the sentence is cut off before the critical "0%" completing "12.0%". The annotation text literally ends mid-number. Similarly, innovation annotation 2 reads: "recent car and cycle demand in Cambridge remains at 11." — truncated before "6%". Innovation annotation 3: "daily average journey time...has increased by 12." — again truncated.
- **Why this matters**: These are THE headline findings of the paper: 11.6% car reduction, 15.8% cycle reduction, 12.0% journey time increase. Truncating the numbers renders the annotations useless for citation.
- **Fix**: Complete all truncated numbers. The full text from page 2 (Abstract): "car and cycle demand in Cambridge remains at 11.6% and 15.8% below pre-pandemic levels, respectively" and "daily average journey time on key transport corridors in Cambridge has increased by 12.0% from 2022 to 2024."

---

## Major Findings

### M1. Overdispersion diagnostic test results not quantified

- **Confidence**: HIGH
- **Evidence**: The annotation says "To test for overdispersion in our traffic counts data, a tentative Poisson model was built" but omits the actual test results. Page 12-13 gives: (a) Dean & Lawless (1989) z-score test confirms overdispersion, and (b) residual deviance/df ratio = 2,545,314 / 23,617 >> 1. These quantitative diagnostics are methodologically important.
- **Why this matters**: The user's own paper needs to justify NB over Poisson. Having the exact diagnostic approach and numbers from a same-project paper is directly useful.
- **Fix**: Expand the overdispersion annotation to include: "the z-score test developed by Dean & Lawless (1989) was applied, which confirms the overdispersion. The ratio between the residual deviance (2,545,314) and the degrees of freedom (23,617) of the tentative Poisson model was calculated, which is significantly larger than 1."

### M2. The Breusch-Pagan annotation captures the test but not the GLM solution

- **Confidence**: HIGH
- **Evidence**: Method annotation 6 reads: "Using a Breusch-Pagan test on a tentative linear model with log-transformed journey time data, it was found that heteroscedasticity exists, which may lead to inaccurate coefficient estimates and confidence intervals." This captures the problem but not the solution — the very next sentence says "A generalised linear model should thus be considered" and then specifies Gamma with log-link. The annotation stops at the problem statement.
- **Why this matters**: The logical chain (heteroscedasticity detected -> therefore Gamma GLM) is the methodological justification the user needs for their own paper.
- **Fix**: Extend this annotation or add a new one that completes the reasoning chain through to the Gamma GLM adoption.

### M3. Thursday peak shift and evening peak worsening — the two primary decomposition findings — are absent from conclusion annotations

- **Confidence**: HIGH
- **Evidence**: Page 25-26 (Conclusion section) explicitly states: "1) the increase of average journey time is caused by worsening congestion at evening peaks and on Thursdays, with the former being the primary factor; 2) the increase of peak-time congestion is not associated with increasing demand across major modes of road transport; and 3) the recent increase of journey time in Cambridge is thus likely to be caused by supply-side factors." None of the 6 conclusion annotations capture these three numbered findings from the Conclusion section.
- **Why this matters**: These are the paper's core analytical contributions — the decomposition of the paradox into specific temporal and causal components.
- **Fix**: Add a conclusion annotation capturing the three-part finding from page 25-26 of the Conclusion section.

### M4. Sample sizes and observation counts not captured anywhere

- **Confidence**: HIGH
- **Evidence**: Table 2 (pages 10-11) provides detailed observation counts: long-term car/cycle = 24,969 records each; recent car/cycle = 6,712 each; journey time = 64,189 records. Also: 5 cameras for long-term, 13 cameras for recent trends, 9 cameras for journey time across 5 corridors. None of these appear in any annotation.
- **Why this matters**: Sample sizes are essential for assessing statistical power and for the user's own paper when comparing methodological approaches.
- **Fix**: Add method annotation(s) capturing the final sample sizes from Table 2 and the camera counts.

### M5. Innovation annotation 1 is the abstract/title block, not an innovation claim

- **Confidence**: HIGH
- **Evidence**: Innovation annotation 1 reads: "Insights from Cambridge, UK Li Wan* and Byron Huang Department of Land Economy, University of Cambridge * Corresponding author Abstract The growing prevalence of flexible/remote working..." — this is the paper header and opening of the abstract, not an innovation statement.
- **Why this matters**: This annotation is noise. It does not capture any specific innovation claim and wastes annotation space.
- **Fix**: Remove this annotation. The actual innovation claims are on page 4: "Firstly, this paper is one of the first empirical studies..." (already captured in innovation annotation 5), "Secondly, the novel intra-day/week perspective unfolds fresh insights...", and "Lastly, despite using an exclusive data set, similar traffic monitoring data exists in most local transport authorities...Our study provides a robust and transferrable method."

### M6. Second and third innovation contributions from page 4 are missing

- **Confidence**: HIGH
- **Evidence**: Page 4 lists three contributions: (1) first empirical study of post-pandemic paradox [captured], (2) "the novel intra-day/week perspective unfolds fresh insights into the nuanced effects of flexible/remote working on travel demand, which contests its presumed benefit of reducing commuting demand and hence mitigating peak-time traffic congestion" [NOT captured], (3) "Our study provides a robust and transferrable method that can be readily deployed by in-house analysts in local transport authorities" [NOT captured].
- **Why this matters**: Contribution 2 directly contests the assumption that flexible working reduces congestion — this is the intellectual core of the paper. Contribution 3 is about transferability, which is relevant to the user's own work.
- **Fix**: Add innovation annotations for contributions 2 and 3 from page 4.

---

## Minor Findings

### m1. Periodisation scheme — a methodological novelty — not annotated

The paper distinguishes four periods (pre-pandemic, during pandemic, PP-T, PP-S) and explicitly calls the PP-T/PP-S distinction a "novelty of our periodisation" (page 8). This is not captured in any method annotation.

### m2. Reference case selection rationale not captured

Page 13: Wednesday selected as reference day because it is "most representative of a typical workday and is less likely to be affected by flexible working arrangements." 1200-1300 as reference hour. This methodological choice is important for interpreting coefficients.

### m3. Journey time data temporal granularity not captured

The journey time data is at 5-minute intervals (page 8), which is notably finer than the hourly traffic count data. This granularity difference is methodologically relevant.

### m4. The supply-side explanation for the paradox is not explicitly annotated

Pages 21-22: the paper provides specific supply-side factors (cycling lane widening, traffic signalising changes, school street pedestrianisation) as the likely cause of worsening congestion despite reduced demand. The conclusion annotations reference the paradox generally but not these specific mechanisms.

### m5. Evening peak congestion worsening quantified but not captured

Page 21: "the most congested hour (1600-1700) is about 66% more congested than the reference hour (1200-1300) in Period 1, compared to about only 30% in Period 0." This dramatic doubling of peak congestion intensity is a key finding not in any annotation.

---

## What's Missing (Gap Analysis)

1. **Gamma GLM specification** — the entire journey time modelling approach (Critical — see C1)
2. **R/MASS implementation details** — software and package version
3. **Complete headline numbers** — 11.6%, 15.8%, 12.0% all truncated
4. **Overdispersion test quantitative results** — deviance/df ratio
5. **Sample sizes** — 24,969 / 6,712 / 64,189 records
6. **Camera network details** — 5 long-term, 13 recent, 9 journey time cameras; 5 travel corridors named
7. **Periodisation scheme** — the 4-period framework and its novelty
8. **Three-part decomposition finding** from the Conclusion
9. **Supply-side causal explanation** — cycling lanes, signalising, school streets
10. **66% vs 30% evening peak congestion** quantification
11. **Second and third innovation contributions** from page 4
12. **Control variable table** (Table 3) — 10 control variables systematically listed
13. **Interaction term approach** — period*day and period*hour models
14. **Morning peak shift** — from 0800-0900 in Period 0 to 0700-0800 in Period 1

---

## Multi-Perspective Notes

### As STATISTICIAN:
The model specifications are critically incomplete. A statistician reading these annotations would know the paper uses NB for counts (partially captured) but would have NO IDEA the paper uses Gamma GLM with log-link for journey times. The diagnostic chain (Breusch-Pagan -> heteroscedasticity -> Gamma GLM) is broken at the critical step. The interaction term approach (period*day, period*hour) that drives the paper's key findings is not captured at all.

### As DOMAIN EXPERT:
A transport researcher would get the general narrative (reduced demand but worse congestion) but would miss the analytical depth. The three-part decomposition (evening peaks primary, Thursday secondary; not demand-driven; therefore supply-side) is the paper's intellectual contribution and is absent from annotations. The specific mechanisms (road space reallocation, cycling infrastructure) are also missing.

### As METHODOLOGIST:
Replication from these annotations is impossible. Missing: software (R), packages (MASS, base R), model families (NB2 vs NB1 not specified, Gamma family), link functions (log), reference categories (Wednesday, 1200-1300), sample sizes, number of cameras, data granularity (hourly vs 5-minute), data cleaning workflow. A researcher wanting to apply the same approach would need to read the full paper.

---

## Verdict Justification

**REVISE** — not REJECT, because:
- The limitation annotations are thorough and accurately capture all three limitations (Firstly/Secondly/Lastly structure).
- The conclusion annotations, while incomplete, do capture the stabilised demand narrative and the policy implications.
- The innovation annotations partially capture the paper's contributions (despite one being header noise).

However, the three CRITICAL findings (missing Gamma GLM, missing NB implementation, truncated numbers) collectively mean the annotations fail their primary purpose for this specific paper — which is to support the user's own Gamma GLM research within the same DARe project. The 6 MAJOR findings compound this: diagnostic details, decomposition findings, sample sizes, and innovation claims are all incomplete.

**Escalation to ADVERSARIAL mode** was triggered at Phase 2 when the first three pre-commitment predictions were immediately confirmed. The adversarial investigation revealed the additional gaps in m1-m5 and the full gap analysis list.

**Realist Check**: No downgrades applied. These are not theoretical concerns — the user explicitly stated this is "the MOST IMPORTANT paper in the LR because it's from the same DARe project and uses the same statistical approach." Every missing Gamma GLM detail is a citation the user cannot make from their annotation platform. The truncated numbers mean the user literally cannot read the key findings from the annotations without going back to the PDF. These findings survive pressure-testing at their current severity levels.

**To upgrade to ACCEPT**: Fix all 3 Critical findings, fix at least M1-M4 and M6 from Major findings, and address gaps 5-8 and 13 from the gap list. This would bring the annotation quality to the level expected for the most important paper in the review.

---

## Open Questions (unscored)

1. The paper is a preprint (SSRN) — has it since been published in a peer-reviewed journal? If so, the annotations should reference the published version.
2. The annotations use `original_texts` with truncated `text` fields (always ~70 chars). Is this a platform limitation or a bug in the extraction pipeline? The truncation at 70 characters is what causes the number truncation in C3.
3. Should the 15 models (1, 1A, 1B, 2, 2A, 2B, etc.) be annotated individually, or is the current summary-level approach sufficient for the LR?
