# Final Integrity Report -- v4

Generated: 2026-03-28

## A. Reference Check

- **Citations in paper**: 39 unique keys
- **Entries in bib**: 38 entries
- **Ghost citations** (in paper, not in bib): **1 found**
  - `wooldridge2015control` -- cited on line 544 (Section 5.4, Endogeneity discussion) but missing from `references_v2.bib`
- **Orphan references** (in bib, not cited): **None**

### Full citation key list (paper)
becker2026rainfall, bergantino2024assessing, bi2022weather, cai2016rainfall, calvert2018methodology, dft2024rea, elfaouzi2012effects, farahmand2024integrating, freeman1977centrality, ganin2017resilience, gao2024resilience, greenshields1935study, he2026flood, hranac2006empirical, huang2022overview, jaroszweski2010effect, koetse2009impact, li2024percolation, liu2026extreme, maze2006weather, mccullagh1989glm, murphy1985estimation, nce2026srn, nelder1972glm, nh2024climate, pagan1984econometric, pregnolato2016impact, pregnolato2017depth, pulugurtha2021aadt, raccagni2024urban, stamos2023centrality, stern2007contribution, ukcp18, unece2024stress, wan2024paradox, wan2025variability, wassmer2024resilience, wooldridge2015control, zhou2026bibliometric

### Full bib key list
becker2026rainfall, bergantino2024assessing, bi2022weather, cai2016rainfall, calvert2018methodology, dft2024rea, elfaouzi2012effects, farahmand2024integrating, freeman1977centrality, ganin2017resilience, gao2024resilience, greenshields1935study, he2026flood, hranac2006empirical, huang2022overview, jaroszweski2010effect, koetse2009impact, li2024percolation, liu2026extreme, maze2006weather, mccullagh1989glm, murphy1985estimation, nce2026srn, nelder1972glm, nh2024climate, pagan1984econometric, pregnolato2016impact, pregnolato2017depth, pulugurtha2021aadt, raccagni2024urban, stamos2023centrality, stern2007contribution, ukcp18, unece2024stress, wan2024paradox, wan2025variability, wassmer2024resilience, zhou2026bibliometric


## B. Internal Consistency

### Numbers: Abstract vs Body
| Claim (Abstract) | Body location | Match? |
|---|---|---|
| ~9 million hourly observations | Line 170 (9M after weekday restriction), Line 285 (9M), Line 337 (~9,000,000), Line 593 (~9M) | YES |
| 460 SRN links | Lines 152, 197, 229, 285, 338, 370, 379, 405, 425, 593 | YES |
| 2022--2024 study period | Lines 170, 285, 579 | YES |
| Network baseline 2.1% per mm/hr | Line 353 (2.1% from coeff -0.0209) | YES |
| Speed reductions up to 4x baseline | Lines 379 (factor of ~4), 383 (-0.08 vs -0.021) | YES |
| WLS R-squared 34% | Lines 423 (0.34), 441 (34%), 506 (34%), 593 (34%) | YES |
| Lanes, speed limit, daily flow, rural classification as significant | Lines 431-438, 593 | YES |

### Three-stage framework consistency
The framework is described as "Estimate--Map--Explain" throughout:
- Abstract: "three-stage Estimate--Map--Explain framework" (line 35)
- Introduction: three enumerated stages (lines 70-74) -- Estimate, Map, Explain
- Section 3 heading: "Methodology" with subsections Stage 1 (GLM), Stage 2 (WLS), Stage 3 (Centrality)
- **INCONSISTENCY**: The section numbering labels Stage 2 as "Explaining heterogeneity via WLS" (sec:method:feature, line 226) and Stage 3 as "Network vulnerability analysis" (sec:method:centrality, line 245). However, the Introduction's three-stage enumeration lists: (1) Estimate = GLM, (2) Map = spatial projection, (3) Explain = WLS regression. The "Map" stage has no dedicated methodology subsection -- it is implicit. The centrality analysis is described as an additional step ("Betweenness centrality analysis ... then assesses", line 76), not a numbered stage. The Results section follows the same pattern: Stage 1 results, then "Stage 2: Feature analysis results", then "Stage 3: Betweenness centrality". So **"Map" is Stage 2 in the Introduction but has no dedicated section; "Explain" is Stage 3 in the Introduction but labeled Stage 2 in Methodology/Results; centrality is not a numbered stage in the Introduction but is labeled Stage 3 in Methodology/Results.** This is a **naming inconsistency** that should be reconciled.
- Conclusion (line 593): consistent with abstract

### Equation numbering
- Eq 1 (line 193): eq:glm -- Gamma GLM specification
- Eq 2 (line 215): eq:sensitivity -- Link-specific sensitivity
- Eq 3 (line 232): eq:wls -- WLS regression
- Eq 4 (line 259): eq:traveltime -- Travel time calculation
- **Sequential and correct.**

### Table/Figure cross-references
| Reference in text | Label defined? | Match? |
|---|---|---|
| Figure~\ref{fig:framework} (line 134) | \label{fig:framework} (line 145) | YES |
| Figure~\ref{fig:study_area} (line 152) | \label{fig:study_area} (line 164) | YES |
| Figure~\ref{fig:coef_dist} (line 370) | \label{fig:coef_dist} (line 376) | YES |
| Figure~\ref{fig:spatial_coef} (line 387) | \label{fig:spatial_coef} (line 396) | YES |
| Figure~\ref{fig:centrality} (line 472) | \label{fig:centrality} (line 483) | YES |
| Table~\ref{tab:desc} (line 285) | \label{tab:desc} (line 290) | YES |
| Table~\ref{tab:glm} (line 315) | \label{tab:glm} (line 320) | YES |
| Table~\ref{tab:wls} (line 405) | \label{tab:wls} (line 410) | YES |
| Table~\ref{tab:centrality} (line 453) | \label{tab:centrality} (line 458) | YES |
| Table~\ref{tab:robustness_volume} (line 533) | \label{tab:robustness_volume} (line 538) | YES |
| Table~\ref{tab:spectest} -- **no text reference** | \label{tab:spectest} (line 362) | ISSUE: tab:spectest is defined but never referenced via \ref in body text (the table simply follows the paragraph on line 357) |

### Section cross-references
| Reference | Target | Match? |
|---|---|---|
| Section~\ref{sec:lit} (line 80) | \label{sec:lit} (line 87) | YES |
| Section~\ref{sec:method} (line 80) | \label{sec:method} (line 132) | YES |
| Section~\ref{sec:results} (line 80) | \label{sec:results} (line 280) | YES |
| Section~\ref{sec:discussion} (line 80) | \label{sec:discussion} (line 499) | YES |
| Section~\ref{sec:conclusion} (line 80) | \label{sec:conclusion} (line 591) | YES |
| Section~\ref{sec:results:glm} (line 186) | \label{sec:results:glm} (line 311) | YES |
| Section~\ref{sec:method:glm} (line 315) | \label{sec:method:glm} (line 180) | YES |
| Section~\ref{sec:method:data} (line 577) | \label{sec:method:data} (line 150) | YES |
| Section~\ref{sec:disc:endogeneity} (line 571) | \label{sec:disc:endogeneity} (line 529) | YES |

### Other consistency notes
- Abstract says "single-carriageway connectors" for Cambourne; body confirms this (line 383, 399)
- Abstract says "betweenness centrality analysis identifies segments where individual vulnerability and network importance compound"; body confirms A14 corridor (line 486)
- "93% of the SRN falls short of climate adaptation standards" (line 595 in Conclusion) is consistent with "only 7% meets" (line 62 in Introduction): 100% - 7% = 93%. **Consistent.**


## C. Placeholder Inventory

### STATA_OUTPUT_NEEDED placeholders (45 individual occurrences across 28 lines)

| # | Type | Line | Description |
|---|------|------|-------------|
| 1 | STATA_OUTPUT | 171 | Number of Met Office CEDA stations used |
| 2 | STATA_OUTPUT | 171 | Weather station distances -- min, mean, max (km) |
| 3 | STATA_OUTPUT | 186 | Deviance comparison across Gamma, Gaussian-log, and inverse Gaussian specifications |
| 4 | STATA_OUTPUT | 223 | VIF table for key variables |
| 5 | STATA_OUTPUT | 242 | Bootstrap standard errors for Stage 2 coefficients, comparison with analytic WLS SEs |
| 6 | STATA_OUTPUT | 265 | Closeness centrality results |
| 7-10 | STATA_OUTPUT | 329 | Bank holiday coefficient, SE, z-value, significance (4 placeholders) |
| 11 | STATA_OUTPUT | 341 | Deviance |
| 12 | STATA_OUTPUT | 342 | AIC |
| 13 | STATA_OUTPUT | 343 | BIC |
| 14 | STATA_OUTPUT | 344 | Log pseudolikelihood |
| 15 | STATA_OUTPUT | 345 | Pearson chi-squared / d.f. |
| 16 | STATA_OUTPUT | 346 | McFadden pseudo-R-squared |
| 17 | STATA_OUTPUT | 366 | Number of link interaction terms significant at 5% |
| 18 | STATA_OUTPUT | 366 | Distribution of rainy-hour observations per link -- min, median, max |
| 19 | STATA_OUTPUT | 382 | 95% CI for M11 median coefficient |
| 20 | STATA_OUTPUT | 383 | 95% CI for Cambourne max coefficient |
| 21 | STATA_OUTPUT | 424 | F-statistic and p-value for WLS |
| 22 | STATA_OUTPUT | 441 | Bootstrap SEs percentage larger/smaller than analytic |
| 23 | STATA_OUTPUT | 441 | Whether effect is modest or negligible |
| 24 | STATA_OUTPUT | 445 | Robustness table: unweighted OLS, WLS excl. <1000 obs, log daily flow, subsamples |
| 25 | STATA_OUTPUT | 447 | Two-way clustered standard errors comparison |
| 26-37 | STATA_OUTPUT | 463-466 | Centrality table: 12 cells (4 rows x 3 scenarios) |
| 38 | STATA_OUTPUT | 472 | Centrality at multiple percentiles (95th, 99.9th) |
| 39 | STATA_OUTPUT | 486 | A14 normal centrality value |
| 40 | STATA_OUTPUT | 486 | A14 centrality percentage increase under extreme rainfall |
| 41 | STATA_OUTPUT | 486 | A14 speed reduction percentage per mm |
| 42 | STATA_OUTPUT | 490 | Cambourne centrality value |
| 43 | STATA_OUTPUT | 526 | Percentage difference between bootstrap and analytic SEs |
| 44 | STATA_OUTPUT | 542 | Comparison of precip coefficients with/without volume control |
| 45 | STATA_OUTPUT | 542 | Whether magnitudes increase modestly or are largely unchanged |

### FIGURE_NEEDED placeholders (4 occurrences, in comments)

| # | Type | Line | Description |
|---|------|------|-------------|
| 1 | FIGURE | 138-142 | framework_flowchart -- Three-column flowchart of Estimate-Map-Explain pipeline |
| 2 | FIGURE | 156-161 | study_area_map -- Map of Cambridgeshire SRN with 460 links and weather stations |
| 3 | FIGURE | 391-393 | spatial_coefficient_map -- Map with links colour-coded by precipitation sensitivity |
| 4 | FIGURE | 476-480 | centrality_map -- Side-by-side normal vs extreme rainfall betweenness centrality |

Note: Figure `fig:coef_dist` (line 374) uses `\includegraphics{figures/coefficient_distribution.pdf}` -- this is the **only** figure with an actual file reference rather than a placeholder. Verify that `figures/coefficient_distribution.pdf` exists.

### TABLE_NEEDED placeholders (2 occurrences)

| # | Type | Line | Description |
|---|------|------|-------------|
| 1 | TABLE | 363 | tab:spectest -- Specification test: Gamma vs Gaussian-log vs inverse Gaussian |
| 2 | TABLE | 539 | tab:robustness_volume -- Robustness check: model with and without traffic volume |

### Totals
- **STATA_OUTPUT_NEEDED**: 45 individual placeholders across 28 lines
- **FIGURE_NEEDED**: 4 (all in LaTeX comments, with corresponding fbox placeholders in rendered output)
- **TABLE_NEEDED**: 2 (table environments exist but content is placeholder text)


## D. LaTeX Structure

### Section nesting
```
\section{Introduction}                                    OK
\section{Literature Review}                               OK
  \subsection{Climate change and UK road transport...}    OK
  \subsection{Precipitation effects on traffic speed}     OK
  \subsection{Transport network resilience and topology}  OK
  \subsection{Limitations of existing approaches...}      OK
\section{Methodology}                                     OK
  \subsection{Study area and data}                        OK
  \subsection{Stage 1: Gamma GLM estimation}              OK
    \subsubsection{Distributional choice}                 OK
    \subsubsection{Model specification}                   OK
    \subsubsection{Model diagnostics}                     OK
  \subsection{Stage 2: Explaining heterogeneity via WLS}  OK
    \subsubsection{Generated regressors and inference}    OK
  \subsection{Stage 3: Network vulnerability analysis}    OK
  \subsection{Open-source interactive platform}           OK
\section{Results}                                         OK
  \subsection{Descriptive statistics}                     OK
  \subsection{Stage 1: Gamma GLM results}                 OK
    \subsubsection{Overall model fit}                     OK
    \subsubsection{Link-level heterogeneity...}           OK
  \subsection{Stage 2: Feature analysis results}          OK
    \subsubsection{Robustness checks}                     OK
  \subsection{Stage 3: Betweenness centrality...}         OK
\section{Discussion}                                      OK
  \subsection{Interpretation of key findings}             OK
  \subsection{Comparison with prior literature}           OK
  \subsection{Methodological considerations}              OK
  \subsection{Endogeneity and robustness}                 OK
  \subsection{Sensitivity versus resilience}              OK
  \subsection{Policy implications}                        OK
  \subsection{Limitations}                                OK
  \subsection{Future research}                            OK
\section{Conclusion}                                      OK
\section*{Acknowledgements}                               OK
\section*{CRediT authorship contribution statement}       OK
\section*{Declaration of competing interest}              OK
\section*{Data availability}                              OK
\section*{AI Disclosure}                                  OK
```
Nesting is correct throughout.

### Environment matching
| Environment | \begin count | \end count | Match? |
|---|---|---|---|
| figure | 5 | 5 | YES |
| table | 6 | 6 | YES |
| equation | 4 | 4 | YES |
| tabular | 6 (inside tables) | 6 | YES |
| document | 1 | 1 | YES |
| frontmatter | 1 | 1 | YES |
| abstract | 1 | 1 | YES |
| keyword | 1 | 1 | YES |
| itemize | 7 | 7 | YES |
| enumerate | 2 | 2 | YES |

**All environments properly paired.**

### Other structural notes
- `\bibliographystyle{elsarticle-harv}` and `\bibliography{references_v2}` present (lines 625-626)
- `\linenumbers` enabled (line 14) -- appropriate for review submission
- No unclosed braces detected in spot checks
- `\journal{Transportation Research Part D}` set (line 16)


## VERDICT: FAIL

### Must fix before submission

1. **Ghost citation**: `wooldridge2015control` (line 544) is cited but missing from `references_v2.bib`. Add the bib entry:
   - Wooldridge, J.M. (2015). Control function methods in applied econometrics. *Journal of Human Resources*, 50(2), 420-445.

2. **45 STATA_OUTPUT_NEEDED placeholders** remain across 28 lines. All numerical results from Stata estimation must be filled in before the paper can be submitted.

3. **4 FIGURE_NEEDED placeholders**: All four figures (framework flowchart, study area map, spatial coefficient map, centrality map) need to be created and inserted.

4. **2 TABLE_NEEDED placeholders**: The specification test table (tab:spectest) and volume robustness table (tab:robustness_volume) need content.

5. **Verify** that `figures/coefficient_distribution.pdf` exists (the only figure with an actual file path).

### Should fix (non-blocking but recommended)

6. **Stage numbering inconsistency**: The Introduction defines three stages as (1) Estimate, (2) Map, (3) Explain. But in the Methodology and Results sections, the numbering is (1) GLM = Estimate, (2) WLS = Explain, (3) Centrality = network analysis. The "Map" stage has no dedicated section and the centrality analysis is not part of the original three-stage enumeration. Reconcile by either: (a) making "Map" a brief standalone subsection in Methodology/Results, or (b) redefining the framework as a three-stage pipeline where Stage 2 = Explain and centrality is a separate analysis step (matching the current section structure).

7. **Table tab:spectest** (line 362): The label is defined but never referenced via `\ref` in body text. Add "Table~\ref{tab:spectest}" to the preceding paragraph (line 357) for proper cross-referencing.
