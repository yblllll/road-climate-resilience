# Simulated Peer Review Panel — Transportation Research Part D

**Manuscript**: "Precipitation Sensitivity of Road Speeds on the UK Strategic Road Network"
**Authors**: Yibin Li and Li Wan
**Date of Review**: 2026-03-28

---

# Review by EIC: Prof. Maria Dolores Benavente

## Summary
This paper proposes a three-stage Estimate--Map--Explain framework to quantify how individual road segments on the UK Strategic Road Network respond to precipitation, using a Gamma GLM on ~9 million hourly observations from 460 links in Cambridgeshire. The second stage uses WLS to relate the estimated link-level sensitivity coefficients to road characteristics, and the third stage applies betweenness centrality analysis to identify network-level vulnerabilities. The paper contributes an open-source platform for replication by local authorities.

## Recommendation: Major Revision

## Major Comments (must address)
1. **Scope fit and generalisability**: The study covers only Cambridgeshire. While the methodology is transferable, a single-region study limits the contribution for a journal with an international readership. The authors should either (a) demonstrate replication in at least one additional region, or (b) provide a much more thorough discussion of what features of Cambridgeshire make results transferable versus idiosyncratic (flat terrain, East Anglian climate, specific SRN configuration).
2. **Incomplete tables and figures**: Multiple tables contain [STATA_OUTPUT_NEEDED] placeholders, and several figures are [FIGURE_NEEDED] placeholders. While I understand these will be filled before formal submission, the missing model diagnostics (deviance, AIC, BIC, Pearson chi-squared/df) make it impossible to fully evaluate model adequacy at this stage. I require these to be populated in the revised manuscript.
3. **Novelty claim calibration**: The claim of being "the first link-level precipitation sensitivity estimates for the UK SRN" needs careful phrasing. Liu et al. (2026) already model road transport resilience under extreme rainfall on the Cambridge network. The distinction (regression-based estimation of continuous sensitivity coefficients vs. scenario-based simulation) should be made more precise.
4. **The AI Disclosure section is appreciated but vague**. TRD now expects authors to specify which tools were used and for which tasks. Please revise to name the specific AI tools and describe their roles more concretely.

## Minor Comments (should address)
1. The Highlights section uses "tenfold" but the text says "an order of magnitude" and the actual range is roughly 0 to -0.08 vs. a baseline of -0.021. Strictly speaking, the ratio of most sensitive to baseline is about 4x, not 10x. The order-of-magnitude claim is about the range from near-zero to -0.08, which should be stated more precisely.
2. The paper is well-written but long for TRD. Consider whether the literature review (currently ~4 pages of content) could be tightened; some paragraphs repeat points already made in the introduction.
3. Keywords: "climate adaptation" is somewhat generic. Consider replacing with something more specific like "climate resilience assessment" or "infrastructure adaptation planning."

## Strengths
1. Clear three-stage framework that is easy to follow and logically structured.
2. Strong policy motivation grounded in specific UK policy documents (UNECE, DfT REA, NCE audit).
3. The open-source platform component elevates the paper from a pure research contribution to a practical tool, which aligns well with TRD's applied scope.
4. Honest limitations section that does not shy away from discussing endogeneity, measurement error, and unexplained variance.

## Questions for Authors
1. How were the 460 links selected? Are these all SRN links in Cambridgeshire, or a subset? If a subset, what were the exclusion criteria?
2. Has the platform been tested with any external users (e.g., local authority planners)? Even informal feedback would strengthen the practical contribution claim.
3. The AI Disclosure mentions "literature search, drafting assistance, and code development." Can you be more specific about which sections or analyses involved AI assistance?

---

# Review by R1 (Methodology): Prof. Henning W. Rust

## Summary
The paper fits a Gamma GLM with link-specific precipitation interaction terms to approximately 9 million hourly speed observations, then uses the estimated coefficients as a dependent variable in a WLS regression. This two-stage approach produces link-level sensitivity estimates and identifies road characteristics associated with heterogeneity. The statistical framework is sensible but raises several methodological questions that require attention.

## Recommendation: Major Revision

## Major Comments (must address)
1. **Simultaneity of volume and speed**: The paper acknowledges that volume is "simultaneously determined with speed through the fundamental speed-flow relationship" but includes it as a right-hand-side variable in the Gamma GLM. This is a textbook endogeneity problem. If rainfall reduces both speed and volume (through demand suppression), then conditioning on volume absorbs part of the rainfall effect, biasing the precipitation coefficient toward zero. The mention of a sensitivity analysis excluding volume is insufficient -- the authors should present this as a formal robustness table and discuss the magnitude of the difference. An instrumental variables approach (e.g., using lagged volume or upstream volume) would be preferable, though I acknowledge this is difficult in a GLM framework.
2. **The two-stage estimation and generated regressors**: The authors correctly identify the Pagan (1984) problem and propose a bootstrap correction. However, there is a deeper issue. In Equation (3), the dependent variable is $\hat{\theta}_i = \hat{\beta}_{precip} + \hat{\delta}_i$, which includes the common baseline $\hat{\beta}_{precip}$. Since this common component is estimated with error, all 460 dependent-variable observations share the same estimation error component, inducing correlation. The WLS standard errors (even bootstrapped) may not fully account for this. The authors should either (a) use only $\hat{\delta}_i$ as the dependent variable (the interaction deviations), or (b) demonstrate that inference is robust to this correlated-error structure.
3. **Model diagnostics are missing**: The [STATA_OUTPUT_NEEDED] placeholders for deviance, AIC, BIC, and Pearson chi-squared/df are critical. Without the Pearson chi-squared/df ratio, I cannot assess whether overdispersion is adequately handled. The Gamma GLM assumes variance proportional to the square of the mean; if the Pearson ratio substantially exceeds 1, the variance function may be misspecified and a negative binomial or quasi-likelihood approach might be warranted.
4. **460 interaction terms in a single GLM**: The model includes 459 link fixed effects and 459 link x precipitation interactions, totalling over 900 parameters estimated from ~9 million observations. While the data volume is adequate, I am concerned about (a) convergence properties -- did the IRLS algorithm converge smoothly? (b) the effective degrees of freedom after absorbing link fixed effects; and (c) whether some links have very few rainy-hour observations, leading to poorly identified interaction coefficients. The distribution of the number of rainy-hour observations per link should be reported.
5. **Distributional choice justification**: The paper mentions that "specification tests comparing deviance residuals across Gamma, Gaussian-log, and inverse Gaussian specifications confirmed the Gamma as the preferred choice" but provides no results. This claim needs to be substantiated with a table or at minimum the test statistics.

## Minor Comments (should address)
1. Equation (1): The notation mixes subscript conventions. $\beta_k$ and $X_{kit}$ use subscript $k$ for different controls, but the precipitation interaction $\delta_i$ uses only a link subscript. It would be cleaner to write $\delta_i \cdot \text{precip}_{it}$ as a special case of the interactions or to separate the equation into structural and interaction components.
2. The claim that "VIFs fall below 5" for non-interaction terms is reassuring but the actual values should be reported, especially for volume and the temporal fixed effects which could be correlated.
3. Clustering standard errors at the link level with 460 clusters is adequate for asymptotic cluster-robust inference (the common rule-of-thumb is >50 clusters), but the authors should verify that results are robust to two-way clustering on link and time (e.g., month-year).
4. The WLS weights $w_i = 1/\text{se}(\hat{\delta}_i)^2$ are standard for feasible GLS but assume the only source of heteroscedasticity in the Stage 2 regression is sampling variation in $\hat{\delta}_i$. If the true Stage 2 error $\epsilon_i$ is also heteroscedastic (e.g., proportional to link length or traffic volume), the weights are misspecified. A robustness check with heteroscedasticity-robust standard errors on the WLS would be useful.
5. The 99th percentile precipitation of ~5 mm/hr seems low for an "extreme rainfall" scenario. How does this compare to climate projections? Could the authors also present results at the 95th and 99.9th percentiles to show sensitivity?

## Strengths
1. The Gamma GLM with log link is a well-chosen distributional model for speed data -- it handles the positivity constraint naturally and the log link yields interpretable multiplicative effects.
2. The bootstrap procedure for the two-stage estimation is the correct approach and shows methodological awareness.
3. The sample size (~9 million observations) provides substantial statistical power for identifying even small interaction effects.
4. The paper engages with the econometric literature on generated regressors (Pagan 1984, Murphy & Topel 1985), which is unusual and commendable in a transport journal.

## Questions for Authors
1. What is the distribution of the number of rainy-hour observations (precip > 0) per link? Are there links with fewer than, say, 100 rainy hours? If so, how reliable are their interaction coefficients?
2. Have you examined whether the precipitation effect is linear on the log scale, or whether there is evidence of non-linearity (e.g., a threshold effect or a quadratic term)?
3. Could you clarify the reference category structure? You mention "A14 Brampton Hut interchange link as the reference category" for link fixed effects. Does this mean $\gamma_{ref} = 0$ and $\delta_{ref} = 0$, so the baseline precipitation coefficient $\beta_{precip}$ is identified from this single link?
4. Were any links excluded from the estimation due to data quality issues (e.g., excessive missing data, sensor malfunctions)?

---

# Review by R2 (Domain): Dr. Maria Pregnolato

## Summary
The paper addresses precipitation-induced speed reductions on the UK SRN at a link-by-link level, combining a statistical model with network centrality analysis. The Cambridgeshire case study covers a meaningful section of the SRN including major freight corridors (A14) and growing residential areas (Cambourne). The work responds to a genuine policy need for evidence-based climate resilience tools in UK road transport.

## Recommendation: Minor Revision

## Major Comments (must address)
1. **Precipitation characterisation is oversimplified**: The paper uses hourly precipitation totals (mm/hr) as a single continuous variable. In practice, the impact of rainfall on road speeds depends on rainfall intensity profiles (sustained light rain vs. short intense burst), antecedent conditions (saturated vs. dry ground), and whether surface water accumulates. The absence of any antecedent moisture variable or intensity categorisation is a limitation that should be discussed more explicitly. At minimum, the authors should test whether adding a binary "sustained rain" indicator (e.g., rainfall in the preceding 3 hours) improves the model.
2. **Nearest-station weather assignment**: The paper matches weather data to road links using nearest-station assignment from the Met Office CEDA archive. How many weather stations are used, and what is the typical distance from a link to its nearest station? In East Anglia, station density can be sparse. If most links are assigned weather from the same 2-3 stations, the effective spatial variation in precipitation may be very low, and the link-level sensitivity estimates may be driven more by traffic characteristics than by genuine spatial variation in weather exposure. A map showing station locations relative to road links is needed (noted as [FIGURE_NEEDED] for the study area map).
3. **The flood/inundation distinction**: The paper positions itself relative to flood-transport models (including my own work -- Pregnolato et al., 2017) but should be clearer that it addresses routine precipitation effects on speed, not flood inundation. A road flooded to 300mm depth is a qualitatively different disruption from rain falling at 5 mm/hr on a drained carriageway. The paper conflates these at times, particularly in the policy implications when discussing "drainage investment." The link between the estimated precipitation sensitivity and actual flooding risk should be articulated more carefully.

## Minor Comments (should address)
1. The description of the SRN should note that Cambridgeshire's SRN is predominantly flat, which limits surface water accumulation compared to hilly regions (e.g., the Pennines, Peak District). This affects generalisability.
2. The A14 between Cambridge and Huntingdon was substantially rebuilt and upgraded between 2016 and 2020 (the A14 Cambridge to Huntingdon Improvement Scheme). Since the study period is 2022-2024, the data capture the post-improvement condition. This should be noted, as the old A14 would likely have shown much higher precipitation sensitivity.
3. Cambourne Road is not technically part of the SRN -- it is a local road managed by Cambridgeshire County Council. If it is included via WebTRIS monitoring, this should be clarified, as it complicates the "SRN" framing.
4. The phrase "growing residential areas west of Cambridge" is vague. The specific developments (Cambourne, Bourn Airfield, Northstowe) should be named if the paper intends to make claims about future demand growth.
5. The betweenness centrality analysis uses only the SRN links within Cambridgeshire. In reality, drivers can reroute onto local roads to avoid disrupted SRN segments. An analysis limited to the SRN overstates centrality concentration because it excludes alternative routes. This limitation should be discussed.

## Strengths
1. The paper fills a genuine gap in the UK evidence base. The DfT REA (2024) and NCE audit are correctly cited as establishing policy demand for exactly this type of tool.
2. The link-level granularity is a real advance over corridor-level averages. The finding that motorway segments are near-zero sensitivity while single-carriageway connectors show 4x baseline effects is both intuitive and empirically valuable.
3. The open-source platform and emphasis on publicly available data directly address the accessibility barrier that prevents local authorities from conducting their own resilience assessments.
4. The honest acknowledgement that 66% of variance is unexplained, and the sensible attribution to drainage quality, pavement condition, and gradient.

## Questions for Authors
1. Is Cambourne Road included in the National Highways WebTRIS system? If so, under what classification? If not, how were the data obtained?
2. Were any links affected by major roadworks during 2022-2024 (e.g., the A428 Black Cat to Caxton Gibbet scheme, which was under construction)? How were these links handled?
3. The paper mentions "Alchera Technologies" as the source for disruption indicators. Can you describe what this dataset covers and how complete it is? Are there systematic gaps in disruption reporting?
4. Have you considered validating the model against a held-out time period (e.g., training on 2022-2023, testing on 2024)?

---

# Review by R3 (Interdisciplinary): Prof. Igor Linkov

## Summary
The paper develops a quantitative framework linking micro-level road segment precipitation sensitivity to macro-level network vulnerability through betweenness centrality analysis. It positions itself as a rapid screening tool complementary to detailed simulation, responding to the UNECE stress test framework's call for accessible resilience assessment methods. The work bridges statistical climatology, transport engineering, and network science.

## Recommendation: Minor Revision

## Major Comments (must address)
1. **Resilience is not just sensitivity**: The paper uses "resilience" and "sensitivity" somewhat interchangeably, but they are distinct concepts in the resilience literature (Calvert & Snelder, 2018, which the paper cites). Resilience encompasses robustness, redundancy, resourcefulness, and rapidity of recovery. The paper measures only one component -- robustness (speed reduction during precipitation). It does not measure recovery time, adaptive capacity, or redundancy. The title and framing should be more precise: this is a "precipitation sensitivity" study, not a full "resilience" assessment. The current title is appropriately specific, but several passages in the discussion overreach (e.g., "the information required for targeted adaptation investment" -- sensitivity alone is necessary but not sufficient for adaptation planning).
2. **Network analysis is underdeveloped**: The betweenness centrality analysis, while conceptually sound, is presented at a very high level with most results in [STATA_OUTPUT_NEEDED] placeholders. More critically, the analysis uses only betweenness centrality as the network metric. The resilience literature (Ganin et al., 2017, which the paper cites) shows that different centrality measures can produce different vulnerability rankings. At minimum, the authors should also compute closeness centrality or network efficiency and show whether the vulnerability rankings are robust to the choice of metric.
3. **The micro-to-macro bridge is incomplete**: The framework estimates link-level sensitivity (micro) and computes network centrality (macro), but the connection is simply overlaying one on the other. There is no formal model of how link-level degradation propagates through the network. Traffic rerouting, cascading delays, and capacity constraints are not modelled. The betweenness centrality under "extreme rainfall" simply adjusts travel times without considering that flows will redistribute. This is a significant limitation that should be acknowledged more prominently.

## Minor Comments (should address)
1. The paper would benefit from connecting to the broader critical infrastructure resilience literature, not just transport. The interdependence of road transport with other infrastructure systems (energy, communications, emergency services) during extreme weather events is well-documented and could strengthen the policy relevance.
2. The three scenarios (normal weekday, weekend, extreme rainfall) feel somewhat ad hoc. A more systematic sensitivity analysis across precipitation percentiles (e.g., 90th, 95th, 99th, 99.9th) would be more informative than a single extreme scenario.
3. The Gini coefficient for centrality distribution (mentioned in Table 4 but not yet populated) is an interesting metric. If centrality becomes more concentrated under extreme rainfall, this implies reduced redundancy -- a key resilience indicator. This point deserves elaboration.
4. Consider citing the ASCE resilience framework or the National Infrastructure Commission's work on infrastructure resilience alongside the UNECE reference.

## Strengths
1. The paper correctly identifies the practical gap between simulation-heavy resilience assessment and the needs of resource-constrained local authorities. The "rapid screening tool" positioning is appropriate and valuable.
2. The three-stage framework is modular and scalable -- each stage can be improved independently as better data or methods become available.
3. The integration of empirically estimated sensitivity into network centrality analysis (rather than assumed degradation) is a genuine methodological contribution to the network resilience literature.
4. The emphasis on open-source tools and publicly available data aligns with current infrastructure resilience policy priorities around transparency and reproducibility.

## Questions for Authors
1. How would the vulnerability ranking change if you used a different network metric (e.g., closeness centrality, network efficiency, or percolation threshold)?
2. Have you considered dynamic network effects -- for example, how does traffic redistribution during rainfall change the effective centrality of links?
3. Could the framework be extended to model compound events (e.g., rainfall + high wind, or rainfall + tidal surge for coastal SRN segments)?
4. The paper mentions connecting to UKCP18 projections as future work. Have you done any preliminary calculations showing what the framework would project for, say, RCP8.5 at 2070?

---

# Review by Devil's Advocate: Anonymous

## Summary
The paper presents a statistically competent but ultimately incremental contribution that dresses up a straightforward exercise -- running a GLM on traffic speed data with weather interactions -- in the language of "climate resilience" and "network vulnerability." The three-stage framework is more a sequence of standard analyses than a methodological innovation.

## Recommendation: Major Revision

## Major Comments (must address)
1. **The "framework" is three standard analyses stapled together**: Stage 1 is a GLM with interaction terms -- a standard technique. Stage 2 is a WLS regression on estimated coefficients -- meta-regression, also standard. Stage 3 is betweenness centrality -- a textbook network metric. Each is well-executed, but the paper oversells their combination as a "framework" or "pipeline." The novelty claim needs to be more honest: the contribution is the application to UK SRN data, not the methodology itself.
2. **The 34% R-squared is presented as a success, but it is weak**: Two-thirds of the variation in precipitation sensitivity is unexplained. The authors attribute this to "drainage quality, pavement condition, road gradient, and local topography" -- but if these are the actual determinants of resilience, then the observable characteristics (lanes, speed limit, flow) are poor proxies. The policy implication ("targeted drainage investment on rural A-roads") is not well-supported by a model that cannot distinguish between a well-drained rural road and a poorly-drained one. The paper should be more cautious about actionable recommendations.
3. **Endogeneity is acknowledged but not resolved**: The volume-speed simultaneity, the nearest-station weather measurement error, and the post-pandemic behavioural shifts are all acknowledged in the limitations but not addressed. Each of these could meaningfully bias the precipitation coefficients. The paper should present at minimum an instrumental variables robustness check for volume, or explicitly argue why the bias direction is known.
4. **The centrality analysis is illustrative at best**: With all key results in [STATA_OUTPUT_NEEDED] placeholders, the centrality analysis contributes nothing concrete to the current manuscript. Even in principle, computing betweenness centrality on 460 links of a subnetwork without considering local road alternatives or traffic reassignment produces results that are artefacts of the network boundary, not genuine vulnerability assessments. The A14 would be central in any Cambridgeshire analysis simply because it is the main east-west road.
5. **The "open-source platform" claim is unsubstantiated**: The paper describes a Streamlit platform with four modules but provides no repository URL, no screenshot, no user testing results. The claim that "any local authority" can replicate the analysis is aspirational, not demonstrated. Has any local authority actually used it? If not, this contribution should be substantially downweighted.
6. **Overstated contrast with simulation approaches**: The paper repeatedly contrasts itself favourably with agent-based microsimulation and coupled flood-traffic models, claiming these require "substantial data, computational resources, and city-specific calibration" while the proposed framework uses "only publicly available data." But the proposed framework also requires city-specific estimation (the GLM is fit to Cambridgeshire data), and the data requirements (3 years of hourly link-level speed data from WebTRIS, matched weather data, Alchera disruption data) are not trivial. The barrier-to-entry comparison is overstated.

## Minor Comments (should address)
1. The paper cites itself twice (Wan & Huang, 2024; Wan & Zhang, 2025). While self-citation is acceptable, neither citation is essential to the argument. Consider whether they are included for citation-building rather than necessity.
2. The constant coefficient of variation assumption of the Gamma distribution is stated but not tested. A simple plot of residual variance versus fitted values would suffice.
3. The "order of magnitude" claim (sensitivity varies from near-zero to -0.08) is technically a factor of ~16 from the most resilient to most sensitive links. But many of the near-zero links may have imprecisely estimated coefficients that are not statistically distinguishable from zero. How many of the 460 links have statistically significant interaction terms?
4. The paper does not report any goodness-of-fit measure for the Gamma GLM beyond the placeholder deviance statistics. A pseudo-R-squared or McFadden R-squared would help readers assess explanatory power.
5. The 500-iteration bootstrap is adequate but not generous. Standard practice for publication is often 1000+ iterations. Was 500 chosen for computational reasons?
6. "Bank holiday" is listed as a control variable but its coefficient is not reported in Table 2. Is it significant?

## Strengths
1. The dataset is genuinely impressive -- 9 million hourly observations across 460 links over 3 years is a substantial empirical contribution.
2. The writing quality is high. The paper is clearly structured, well-argued, and appropriately caveated (especially in the limitations section).
3. The generated-regressors discussion is a technically literate treatment of a problem that many applied papers would ignore entirely.

## Questions for Authors
1. How many of the 460 link-specific interaction terms are individually statistically significant at the 5% level? If most are insignificant, the "heterogeneity" story is less compelling.
2. What happens to the Stage 2 results if you exclude links with fewer than 500 rainy-hour observations?
3. The baseline precipitation coefficient of -0.021 is estimated at the Brampton Hut interchange reference link. Is this link representative? What if you chose a different reference link?
4. Can you provide the actual Streamlit platform URL or repository link? Without it, the "open-source" claim cannot be verified.
5. The AI Disclosure is refreshingly honest but raises the question: which findings in this paper were primarily generated by the human authors versus by AI tools?

---

# Editorial Decision

## Decision: Major Revision

## Summary of Reviewer Consensus

All five reviewers agree that the paper addresses a genuine and timely gap in the UK transport-climate evidence base, and that the dataset (9 million observations, 460 links, 3 years) is a significant empirical asset. The three-stage framework is clearly presented and the writing quality is high.

Reviewers converge on several concerns:
- **Incomplete results**: All reviewers note the [STATA_OUTPUT_NEEDED] and [FIGURE_NEEDED] placeholders. While understood as pre-submission drafts, the missing model diagnostics prevent full methodological evaluation (R1, EIC).
- **Endogeneity of volume**: R1 and the Devil's Advocate both flag the volume-speed simultaneity as unresolved. The sensitivity analysis excluding volume must be presented formally.
- **Network analysis underdevelopment**: R3 and the Devil's Advocate find the centrality analysis insufficiently developed -- limited to one metric, one extreme scenario, and no traffic reassignment modelling.
- **Generated regressors**: R1 raises a subtle but important point about the common estimation error component in $\hat{\theta}_i$.

Reviewers diverge on:
- **Scope of contribution**: R2 and R3 view the paper as making a valuable applied contribution meriting minor revision; the Devil's Advocate considers it methodologically incremental requiring major rethinking of novelty claims; R1 and EIC take intermediate positions.
- **Resilience framing**: R3 and the Devil's Advocate want more careful use of "resilience" versus "sensitivity"; R2 is less concerned.
- **Platform**: R2 views the platform as a genuine strength; the Devil's Advocate demands evidence of actual use.

## Required Revisions (prioritized)

### Must Address (from Major comments)

1. **Populate all [STATA_OUTPUT_NEEDED] placeholders and produce all [FIGURE_NEEDED] figures** -- The manuscript cannot be re-evaluated without complete model diagnostics, centrality results, and robustness checks. (All reviewers)

2. **Address volume-speed endogeneity formally** -- Present the sensitivity analysis excluding volume as a full robustness table. Discuss the direction and magnitude of bias. Consider an IV approach or, at minimum, argue convincingly why the bias is bounded. (R1, Devil's Advocate)

3. **Resolve the generated regressors issue with $\hat{\theta}_i$** -- Either use $\hat{\delta}_i$ alone as the Stage 2 dependent variable, or demonstrate that inference is robust to the common estimation error component in $\hat{\beta}_{precip}$. (R1)

4. **Strengthen the network analysis** -- (a) Add at least one additional network metric (closeness centrality or network efficiency). (b) Present results across multiple precipitation percentiles (95th, 99th, 99.9th). (c) Explicitly acknowledge that the analysis does not model traffic reassignment and discuss implications. (R3, Devil's Advocate)

5. **Clarify the sensitivity-vs-resilience distinction** -- Ensure the paper does not overreach from "precipitation sensitivity" to "resilience" without acknowledging the missing components (recovery, redundancy, adaptive capacity). (R3, Devil's Advocate)

6. **Document weather station assignment** -- Report the number of stations, distances to links, and whether spatial clustering of station assignment affects the results. (R2)

7. **Report the number of statistically significant link interactions** -- State how many of the 460 $\hat{\delta}_i$ terms are individually significant and how many rainy-hour observations support each estimate. (R1, Devil's Advocate)

8. **Provide distributional specification test results** -- The Gamma vs. Gaussian-log vs. inverse Gaussian comparison is claimed but not shown. Present the test statistics. (R1)

### Should Address (from Minor comments)

1. Clarify whether Cambourne Road is part of the SRN or a local road, and explain its inclusion. (R2)
2. Note the A14 Cambridge-Huntingdon improvement scheme (2016-2020) and its implications for the study period. (R2)
3. Present VIF values explicitly, not just the "below 5" claim. (R1)
4. Consider two-way clustering (link and time) as a robustness check. (R1)
5. Report the bank holiday coefficient. (Devil's Advocate)
6. Increase bootstrap replications to 1000 (or justify 500). (Devil's Advocate)
7. Tighten the "order of magnitude" / "tenfold" claim in the Highlights and abstract. (EIC, Devil's Advocate)
8. Calibrate novelty claims relative to Liu et al. (2026). (EIC)
9. Discuss the flat Cambridgeshire terrain and its implications for generalisability. (R2)
10. Consider a held-out temporal validation (e.g., train on 2022-2023, predict 2024). (R2)
11. Revise the AI Disclosure to be more specific per emerging TRD guidelines. (EIC)
12. Acknowledge that the centrality analysis is limited to SRN links and excludes local road alternatives. (R2)
13. Add a pseudo-R-squared or equivalent for the Gamma GLM. (Devil's Advocate)

### Optional Improvements

1. Extend the centrality analysis to include closeness centrality or network efficiency for robustness. (R3)
2. Test a non-linear precipitation specification (quadratic or threshold). (R1)
3. Connect to broader critical infrastructure resilience literature beyond transport. (R3)
4. Name specific housing developments (Cambourne, Bourn Airfield, Northstowe) when discussing future demand growth. (R2)
5. Add an antecedent moisture or sustained-rain indicator to the GLM. (R2)
6. Provide a preliminary UKCP18 projection calculation as a worked example. (R3)
7. Consider adding a plot of residual variance vs. fitted values to validate the Gamma constant-CV assumption. (Devil's Advocate)

## Revision Roadmap

**Phase 1 -- Complete the manuscript (highest priority)**
- Fill all [STATA_OUTPUT_NEEDED] placeholders with actual Stata output
- Produce all [FIGURE_NEEDED] figures
- This is a precondition for all other revisions

**Phase 2 -- Address core methodological concerns**
- Present the volume-exclusion robustness table
- Resolve the $\hat{\theta}_i$ vs $\hat{\delta}_i$ question for Stage 2
- Report specification test results (Gamma vs alternatives)
- Report number of significant interactions and rainy-hour observation counts per link
- Document weather station assignment details

**Phase 3 -- Strengthen the network analysis**
- Add a second centrality metric
- Present results at multiple precipitation percentiles
- Add explicit discussion of traffic reassignment limitations

**Phase 4 -- Refine framing and claims**
- Calibrate resilience vs sensitivity language throughout
- Tighten the "order of magnitude" / novelty claims
- Clarify Cambourne Road classification
- Revise AI Disclosure
- Address remaining minor comments

**Phase 5 -- Optional enhancements**
- Non-linear precipitation specification
- Antecedent moisture variable
- Held-out temporal validation
- UKCP18 projection example

---

*End of Review Package*
