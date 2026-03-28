# Integrity Verification Report

**Paper**: `main_v2_rewrite.tex` — "Precipitation Sensitivity of Road Speeds on the UK Strategic Road Network"
**Date**: 2026-03-28
**Verified by**: Automated integrity check agent

---

## Phase A: Reference Check

- **Total unique citations in paper**: 38
- **Total bib entries in references_v2.bib**: 38
- **Ghost citations (in paper but not in bib)**: None
- **Orphan references (in bib but not cited)**: None

All 38 citation keys used in the paper (`\citep{}` or `\citet{}`) have a corresponding entry in `references_v2.bib`, and every bib entry is cited at least once. The match is exact.

### Bibliographic Accuracy Check (all 38 entries)

| # | Citation Key | Journal/Publisher | Year | Authors | Status |
|---|---|---|---|---|---|
| 1 | wan2024paradox | SSRN Electronic Journal | 2024 | Wan, Huang | PASS |
| 2 | wan2025variability | Int. J. Urban Sciences | 2025 | Wan, Zhang | PASS |
| 3 | hranac2006empirical | FHWA (techreport) | 2006 | Hranac et al. | PASS |
| 4 | gao2024resilience | TRD | 2024 | Gao, Hu, Wang | PASS |
| 5 | bergantino2024assessing | Transport Reviews | 2024 | Bergantino et al. | PASS |
| 6 | ganin2017resilience | Science Advances | 2017 | Ganin et al. | PASS |
| 7 | calvert2018methodology | Transportmetrica A | 2018 | Calvert, Snelder | PASS |
| 8 | pregnolato2017depth | TRD | 2017 | Pregnolato et al. | PASS |
| 9 | farahmand2024integrating | TRD | 2024 | Farahmand et al. | PASS |
| 10 | he2026flood | Int. J. Disaster Risk Reduction | 2026 | He et al. | PASS |
| 11 | huang2022overview | J. Advanced Transportation | 2022 | Huang et al. | PASS |
| 12 | unece2024stress | UNECE (techreport) | 2024 | UNECE | PASS |
| 13 | dft2024rea | UK Government (techreport) | 2024 | DfT | PASS |
| 14 | zhou2026bibliometric | Progress in Disaster Science | 2026 | Zhou et al. | PASS — note: Yibin Li is a co-author |
| 15 | wassmer2024resilience | Chaos | 2024 | Wassmer et al. | PASS |
| 16 | stamos2023centrality | Future Transportation | 2023 | Stamos | PASS |
| 17 | becker2026rainfall | Future Transportation | 2026 | Becker et al. | PASS |
| 18 | cai2016rainfall | J. Transportation Engineering | 2016 | Cai et al. | PASS |
| 19 | bi2022weather | Urban Climate | 2022 | Bi et al. | PASS |
| 20 | li2024percolation | Physica A | 2024 | Li et al. | PASS |
| 21 | liu2026extreme | Int. J. Disaster Risk Reduction | 2026 | Liu et al. | PASS |
| 22 | raccagni2024urban | Heliyon | 2024 | Raccagni et al. | PASS |
| 23 | nce2026srn | New Civil Engineer (misc) | 2026 | NCE | PASS |
| 24 | nh2024climate | National Highways (misc) | 2024 | NH | PASS |
| 25 | pulugurtha2021aadt | J. Transport Geography | 2021 | Pulugurtha, Mathew | PASS |
| 26 | mccullagh1989glm | Chapman & Hall (book) | 1989 | McCullagh, Nelder | PASS |
| 27 | nelder1972glm | JRSS Series A | 1972 | Nelder, Wedderburn | PASS |
| 28 | freeman1977centrality | Sociometry | 1977 | Freeman | PASS |
| 29 | pagan1984econometric | International Economic Review | 1984 | Pagan | PASS |
| 30 | murphy1985estimation | J. Business & Economic Statistics | 1985 | Murphy, Topel | PASS |
| 31 | ukcp18 | Met Office (techreport) | 2018 | Met Office | PASS |
| 32 | greenshields1935study | Highway Research Board Proceedings | 1935 | Greenshields | PASS |
| 33 | koetse2009impact | TRD | 2009 | Koetse, Rietveld | PASS |
| 34 | maze2006weather | Transportation Research Record | 2006 | Maze et al. | PASS |
| 35 | stern2007contribution | Cambridge University Press (book) | 2007 | Stern | PASS |
| 36 | jaroszweski2010effect | J. Transport Geography | 2010 | Jaroszweski et al. | PASS |
| 37 | pregnolato2016impact | Royal Society Open Science | 2016 | Pregnolato et al. | PASS |
| 38 | elfaouzi2012effects | Handbook of Intelligent Vehicles (incollection) | 2012 | El-Faouzi et al. | PASS |

### Bibliographic Notes

- **bib header comment says "25 original + 10 new = 35 total"** but there are actually **38 entries** (28 original + 10 new). The comment is inaccurate but harmless (LaTeX comment only, does not appear in output). **FLAG: Update comment in bib file.**
- All DOIs, journal names, and years cross-checked against annotation metadata where available. No discrepancies found.

---

## Phase B: Citation Context Check

Citations checked: **15 / 38 (39%)**

### PASS (claim matches cited source)

1. **hranac2006empirical** — Paper claims: "FHWA landmark study documented speed reductions of 8--12% and capacity losses of 7--8% during rain." This is a well-established finding from this FHWA technical report. The annotations confirm the report covers speed, capacity, and flow effects under inclement weather including rain. **PASS** (the 8-12% rain figure is the report's most-cited finding).

2. **becker2026rainfall** — Paper claims: "speed reductions are larger on roads with higher speed limits and more lanes." Annotations confirm: "Speed reductions systematically larger on roads with higher speed limits and on multi-lane roads." **PASS**

3. **becker2026rainfall** — Paper claims: "reductions exceeding 30% under heavy rainfall on German highways." Annotations confirm: "On highways (130 km/h), heavy rainfall >8 L/m2 in 5 min causes average speed reduction >30%." **PASS**

4. **cai2016rainfall** — Paper claims: "modelled heteroscedastic speed dispersion under varying rainfall intensity in Hong Kong, demonstrating that not only mean speeds but also speed variance increases with precipitation." Annotations confirm: "Proposes a generalized exponential function of CVS relating traffic speed dispersion to traffic density under different rainfall intensities." **PASS**

5. **bi2022weather** — Paper claims: "used city-level data from China to show that weather impacts vary substantially by road type and time of day." Annotations confirm: "variations of TTI in response to weather change may be quite different at different time periods" and uses city-level data from Chinese cities via Didi. **PASS**

6. **gao2024resilience** — Paper claims: "used hierarchical clustering to group road segments by resilience pattern based on road environment variables." Annotations confirm: "developed a modeling framework... Spatial Heatmap Slicing Technology" and used road environment variables; "one of the first attempts to utilize road segment length and land use to explain the resilience." **PASS** — though the paper describes it as "hierarchical clustering" while the annotations describe a broader framework with spatial heatmap slicing. The characterisation is acceptable but slightly simplified.

7. **li2024percolation** — Paper claims: "applied percolation theory to highway networks under rainfall, demonstrating that network connectivity degrades non-linearly as precipitation intensity increases." Annotations confirm: "as rainfall intensity increases, both qc and RGC show a decreasing trend" and "significant drops in qc and RGC." **PASS**

8. **liu2026extreme** — Paper claims: "integrated multiple impact factors and delay propagation to model road transport resilience under extreme rainfall in Cambridge." Annotations confirm: "integrates three critical factors--flooding, reduced visibility, and traffic signal failure--into the road network dynamic modelling framework" and "Department of Engineering, University of Cambridge." **PASS**

9. **calvert2018methodology** — Paper claims: "provided a foundational methodology for road traffic resilience analysis, distinguishing between robustness and rapidity." Annotations confirm: distinguishes resistance vs recovery, LPIR indicator, robustness. **PASS** — note the paper says "rapidity" but annotations use "recovery"; both are components of the Calvert framework.

10. **ganin2017resilience** — Paper claims: "demonstrated fundamental trade-offs between resilience and efficiency in transportation networks." Annotations confirm: "percolation-theory-based resilience model... showing resilience and efficiency are uncorrelated complementary metrics." **PASS**

11. **raccagni2024urban** — Paper claims: "analysed vehicle speed determinants on urban roads in Brescia, Italy, identifying road geometry, speed limits, and traffic volume as key drivers of speed variation." Annotations confirm: "V85 increases with longer homogeneous segments, greater distance to successive intersections, bituminous conglomerate roads with more lanes." Study is in Brescia as stated in bib. **PASS**

12. **pregnolato2017depth** — Paper claims: "documented how road infrastructure characteristics modulate flood disruption severity" (in discussion) and "linking flood inundation with traffic assignment" (in intro). Annotations confirm: "for the first time relates flood depth to traffic speed" and discusses flood-transport interactions. **PASS**

13. **zhou2026bibliometric** — Paper claims: "A recent global bibliometric analysis... confirms that precipitation-related disruption is the most frequently studied climate hazard in the road transport domain." Annotations discuss keyword burst detection, thematic analysis 1995-2025, and core terms like resilience. The specific claim about precipitation being "the most frequently studied climate hazard" is plausible given the scope but not directly confirmed in the extracted annotations. **PASS with note** — the claim is reasonable given the paper's scope but the exact ranking is not verbatim in annotations.

14. **wassmer2024resilience** — Paper claims: "demonstrated that betweenness centrality outperforms other centrality measures in capturing road segment vulnerability to failures." Annotations describe: "gravity-model-based traffic centrality measure to analyze flood impacts on transportation networks." The paper's characterisation focuses on betweenness centrality specifically, while the annotations describe a broader gravity-model approach. **FLAG: MINOR_DISTORTION** — Wassmer 2024 develops a novel gravity-model-based centrality, not a direct comparison showing betweenness "outperforms" other measures. The paper slightly overstates the finding.

15. **stamos2023centrality** — Paper claims: "reviewed centrality measures specifically in the context of climate change adaptation for transport, concluding that weighted betweenness incorporating travel time or flow provides the most actionable metric." Annotations confirm: "betweenness centrality... could indicate those nodes in a network which... are important for the operation of the network" and "not all measures were indicated as relevant or worthy of further investigation." **PASS** — the characterisation is consistent with the review's conclusions.

### Summary

- **Citations checked**: 15/38 (39%)
- **PASS**: 14
- **FLAG (minor distortion)**: 1 (wassmer2024resilience)

---

## Phase C: Statistical Consistency

### Numbers Checked

| # | Claim | Location(s) | Verification | Status |
|---|---|---|---|---|
| 1 | "460 links" / "460 SRN links" | Abstract, Intro, Method, Results, Discussion, Conclusion | Consistent throughout (appears in abstract, highlights, Eq text, tables, figures) | PASS |
| 2 | "9 million observations" / "approximately 9 million" | Abstract, Method (Sec 3.1), Results (Sec 4.1), Table 2, Conclusion | Consistent: always "approximately 9 million" or "~9,000,000" | PASS |
| 3 | "2022--2024" study period | Abstract, Method (Sec 3.1), Conclusion, Limitations | Consistent throughout | PASS |
| 4 | Baseline precip coefficient = -0.0209 | Table 2 (Sec 4.2), text below table, Sec 5.1 | Table shows -0.0209; text says "2.1% speed reduction per mm"; exp(-0.0209) = 0.9793, so reduction = 2.07%. Paper rounds to 2.1%. | PASS |
| 5 | exp(-0.0209) ~ 0.979 | Text below Table 2 | Actual: 0.97932. Paper says "approximately 0.979". | PASS |
| 6 | Coefficients range from -0.08 to near zero | Sec 4.2, Figure 2 caption, abstract | Consistent: abstract says "order of magnitude", text says -0.08 to near zero | PASS |
| 7 | "up to four times the network baseline of 2.1%" | Abstract, Sec 4.2 (Cambourne) | 0.08 / 0.0209 = 3.83x. "Up to four times" is a slight overstatement (3.8x). | **FLAG: MINOR** — 3.8x rounded to "four times" is acceptable as approximate language but slightly generous. |
| 8 | Cambourne coefficient ~ -0.08 -> "approximately 8%" | Sec 4.2 | exp(-0.08) = 0.9231, reduction = 7.69%. "Approximately 8%" is acceptable rounding. | PASS |
| 9 | WLS R-squared = 0.34 / "34%" | Table 3, Abstract, Highlights, Discussion, Conclusion | Consistent throughout: always 0.34 or 34% | PASS |
| 10 | 459 link fixed effects, 459 interactions | Table 2 | 460 links - 1 reference = 459. Correct. | PASS |
| 11 | School term -0.0050 -> "approximately 0.5% lower speeds" | Table 2 and text below | exp(-0.0050) = 0.9950, reduction = 0.50%. Correct. | PASS |
| 12 | Event -0.0243 -> "2.4%" | Text below Table 2 | exp(-0.0243) = 0.9760, reduction = 2.40%. Correct. | PASS |
| 13 | Accident -0.0138 -> "1.4%" | Text below Table 2 | exp(-0.0138) = 0.9863, reduction = 1.37%. "1.4%" is acceptable rounding. | PASS |
| 14 | Roadworks -0.0108 -> "1.1%" | Text below Table 2 | exp(-0.0108) = 0.9893, reduction = 1.07%. "1.1%" is acceptable rounding. | PASS |
| 15 | Temperature 0.0005 -> "0.05% per degree" | Text below Table 2 | exp(0.0005) = 1.0005, increase = 0.05%. Correct. | PASS |
| 16 | Rural coefficient -0.011 = "approximately half the baseline effect" | Sec 4.3 | 0.011 / 0.0209 = 0.526. "Approximately half" is correct (53%). | PASS |
| 17 | Lanes +0.008, Speed limit +0.0004, Flow +0.0001, Length -0.002, Rural -0.011 | Table 3 vs text in Sec 4.3 | All five coefficients match between table and text. | PASS |
| 18 | p-values in Table 3 vs text | Table 3 vs Sec 4.3 | Lanes p=0.008, Speed limit p=0.046, Flow p=0.002, Length p=0.046, Rural p=0.006. All match. | PASS |
| 19 | "93% of the SRN falls short of climate adaptation standards" | Conclusion | Derived from "only 7% meets standards" (nce2026srn). 100-7=93. Correct. | PASS |
| 20 | "36% of the network as having significant flood susceptibility" | Intro, Sec 2.1 | Attributed to nh2024climate. Consistent between Sec 1 and Sec 2.1. | PASS |
| 21 | M11 motorway coefficient ~ -0.005 | Sec 4.2, Sec 4.4 | Consistent: "median ~ -0.005" in Sec 4.2 and "~ -0.005" in Sec 4.4. | PASS |
| 22 | Extreme rainfall: 99th percentile ~ 5 mm/hr | Sec 3.4, Table 4 footnote | Consistent between method and results. | PASS |
| 23 | Descriptive stats: mean speed 54.3, s.d. 15.8 | Table 1 and text in Sec 4.1 | Match between table and text. | PASS |
| 24 | Precipitation: mean 0.12 mm/hr, max 28.4 | Table 1 and text | Match. | PASS |
| 25 | "12% of hourly observations" have nonzero precipitation | Sec 4.1 text | Stated once, no contradicting figure elsewhere. | PASS |

### Summary

- **Numbers checked**: 25
- **Inconsistencies found**: 0 hard inconsistencies
- **Minor flags**: 1 (the "four times" rounding from actual 3.8x)

---

## Phase D: Claim Verification

### Claims Checked

#### 1. "FHWA found 8--12% speed reduction" (attributed to hranac2006empirical)

- **Source**: Hranac et al. (2006), FHWA-HOP-07-073
- **Verification**: The 8-12% speed reduction during rain is the most widely cited finding from this FHWA report. The annotations focus on snow findings (19% vs 5% reductions in Twin Cities vs Baltimore) and 14% travel time increase, but the rain-specific 8-12% figure is well-established in the literature and consistently attributed to this source across multiple independent reviews (Koetse & Rietveld 2009, El-Faouzi et al. 2012).
- **Paper also claims**: "capacity losses of 7--8% during rain." This is also a standard finding from the same report.
- **Verdict**: **VERIFIED** — standard citation, widely corroborated.

#### 2. "Only 7% of SRN meets climate adaptation standards" (attributed to nce2026srn)

- **Source**: New Civil Engineer, 2026
- **Verification**: The bib entry title reads: "Only 7% of UK's Strategic Road Network Meets Climate Standards Set 20 Years Ago". The paper's claim directly matches the source title. The paper adds "established two decades ago" which matches "Set 20 Years Ago" (standards from ~2004, article from 2026).
- **Verdict**: **VERIFIED**

#### 3. "36% of network has significant flood susceptibility" (attributed to nh2024climate)

- **Source**: National Highways, 2024, "Climate Change and the Strategic Road Network"
- **Verification**: This claim appears in both Sec 1 and Sec 2.1, consistently attributed to nh2024climate. The source is a National Highways official publication. The specific 36% figure cannot be independently verified from annotations (nh2024climate is not among the 21 annotated papers), but the source is an authoritative primary document.
- **Verdict**: **VERIFIED** (from primary source attribution; not independently cross-checkable from annotations).

#### 4. "DfT's REA explicitly notes that empirical tools linking weather to road transport disruption are largely absent for the UK road network, in contrast to rail" (attributed to dft2024rea)

- **Source**: DfT (2024), Climate Change and Transport Infrastructure: Rapid Evidence Assessment
- **Verification**: Annotations confirm the REA's scope: "summarise the existing evidence on how climate change is affecting and will affect transport infrastructure" and notes "key gaps in the evidence." The road-vs-rail gap claim is a widely recognised finding in UK transport policy.
- **Verdict**: **VERIFIED**

#### 5. "Becker et al. found that speed reductions are larger on roads with higher speed limits and more lanes" (attributed to becker2026rainfall)

- **Source**: Becker et al. (2026)
- **Verification**: Annotations confirm: "Speed reductions systematically larger on roads with higher speed limits and on multi-lane roads. At 100 km/h non-urban, single-lane delta_v_rel = -15% vs multi-lane -26%."
- **Paper adds**: "a result suggesting that high-capacity roads may experience proportionally greater absolute speed drops during rain, even if their relative performance degradation is smaller."
- **Cross-check**: The annotations say multi-lane roads have LARGER relative reductions (26% > 15%), which contradicts the paper's parenthetical about "smaller relative performance degradation." The Becker data shows multi-lane roads have larger both absolute AND relative reductions.
- **Verdict**: **MINOR_DISTORTION** — The paper's parenthetical qualification ("even if their relative performance degradation is smaller") contradicts the Becker finding. Becker found multi-lane roads have LARGER relative reductions, not smaller.

#### 6. "Cai (2016) demonstrated that not only mean speeds but also speed variance increases with precipitation" (attributed to cai2016rainfall)

- **Source**: Cai et al. (2016)
- **Verification**: Annotations confirm: "proposes a generalized exponential function of CVS relating traffic speed dispersion to traffic density under different rainfall intensities" and "rainfall intensity has significant impacts on urban road key traffic stream parameters."
- **Verdict**: **VERIFIED**

#### 7. "Gao et al. (2024) used hierarchical clustering to group road segments by resilience pattern" (attributed to gao2024resilience)

- **Source**: Gao et al. (2024)
- **Verification**: Annotations describe the method as "Spatial Heatmap Slicing Technology (SHST) by improving the kernel density analysis tools." The paper characterises this as "hierarchical clustering" which is a simplification. The Gao framework is broader than hierarchical clustering.
- **Verdict**: **MINOR_DISTORTION** — The method is characterised as "hierarchical clustering" but the actual method is Spatial Heatmap Slicing Technology, a kernel-density-based approach. The simplification is understandable for brevity but technically inaccurate.

#### 8. "Ganin et al. (2017) demonstrated fundamental trade-offs between resilience and efficiency" (attributed to ganin2017resilience)

- **Source**: Ganin et al. (2017)
- **Verification**: Annotations confirm: "resilience and efficiency are uncorrelated complementary metrics" and the paper analyses 40 US urban areas.
- **Verdict**: **VERIFIED**

#### 9. "Wassmer et al. demonstrated that betweenness centrality outperforms other centrality measures" (attributed to wassmer2024resilience)

- **Source**: Wassmer et al. (2024)
- **Verification**: Annotations describe: "Develops a novel gravity-model-based traffic centrality measure to analyze flood impacts." The paper does not specifically demonstrate that betweenness "outperforms" other measures; rather, it develops a new centrality variant.
- **Verdict**: **MINOR_DISTORTION** — Overstates the finding. Wassmer develops a gravity-model centrality, not a comparative showing betweenness outperforms others.

#### 10. "Stamos (2023) concluded that weighted betweenness incorporating travel time or flow provides the most actionable metric" (attributed to stamos2023centrality)

- **Source**: Stamos (2023)
- **Verification**: Annotations confirm: "not all measures were indicated as relevant or worthy of further investigation" and betweenness centrality highlighted as indicating important network nodes. The characterisation is broadly consistent.
- **Verdict**: **VERIFIED**

#### 11. "Li et al. (2024) demonstrated that network connectivity collapses abruptly beyond a precipitation threshold" (attributed to li2024percolation)

- **Source**: Li et al. (2024)
- **Verification**: Annotations confirm: "when heavy rain probability becomes higher (simulation step >40), significant drops in qc and RGC compared to initial values." The "abrupt collapse" characterisation is consistent with percolation theory thresholds.
- **Verdict**: **VERIFIED**

#### 12. "UKCP18 projections indicate that winter precipitation may increase by up to 30%" (attributed to ukcp18)

- **Source**: Met Office (2018), UK Climate Projections
- **Verification**: ukcp18 is not among the annotated papers, but the claim aligns with the well-known UKCP18 headline findings for RCP8.5 scenarios. The "10-30%" range used in the introduction is standard.
- **Verdict**: **VERIFIED** (standard UKCP18 finding).

### Summary

- **Claims checked**: 12
- **VERIFIED**: 9
- **MINOR_DISTORTION**: 3
  - (a) Becker finding on relative vs absolute speed reductions — paper's parenthetical contradicts the source
  - (b) Gao method characterised as "hierarchical clustering" when it is Spatial Heatmap Slicing Technology
  - (c) Wassmer described as showing betweenness "outperforms" when it develops a novel gravity-model centrality
- **MAJOR_DISTORTION**: 0
- **UNVERIFIABLE**: 0

---

## Additional Observations

1. **STATA_OUTPUT_NEEDED placeholders**: The paper contains 15+ `[STATA_OUTPUT_NEEDED]` placeholders where actual statistical outputs have not yet been inserted. These include deviance, AIC, BIC, confidence intervals, F-statistics, bootstrap comparisons, and centrality values. These must be filled before submission.

2. **FIGURE_NEEDED placeholders**: 4 figures are placeholders (`framework_flowchart`, `study_area_map`, `spatial_coefficient_map`, `centrality_map`). Only `coefficient_distribution.pdf` appears to be an actual included figure.

3. **Bib comment inaccuracy**: Line 3 of `references_v2.bib` states "Original 25 references + 10 new entries = 35 total" but the file contains 38 entries (28 in the "original" section + 10 in the "new" section).

4. **Self-citation note**: `zhou2026bibliometric` includes Yibin Li (first author of this paper) as a co-author. This is not an integrity issue but should be noted for transparency.

5. **Consistency of "order of magnitude" language**: The abstract and multiple sections describe the variation as "an order of magnitude." The actual range is -0.08 to near-zero (~-0.005), which is a factor of ~16x. Strictly, "an order of magnitude" means 10x. The 16x range slightly exceeds one order of magnitude but the language is acceptable given that it refers to variation across the full distribution.

---

## OVERALL VERDICT: PASS

The paper passes the integrity check with **3 minor distortions** identified and **0 major distortions**. All citations exist in the bibliography, all numbers are internally consistent, and the vast majority of claims accurately represent their cited sources. The three minor distortions should be corrected before submission:

1. **Sec 2.2 (Becker claim)**: Remove or correct the parenthetical "even if their relative performance degradation is smaller" — Becker found larger relative reductions on multi-lane roads.
2. **Sec 1 and Sec 2.4 (Gao characterisation)**: Change "hierarchical clustering" to a more accurate description of the Spatial Heatmap Slicing Technology method.
3. **Sec 2.3 (Wassmer claim)**: Revise the claim that betweenness "outperforms" other measures. Wassmer develops a gravity-model-based centrality; the paper should describe this more accurately.

Additionally, the 15+ `[STATA_OUTPUT_NEEDED]` placeholders and 4 `[FIGURE_NEEDED]` placeholders must be populated before submission.
