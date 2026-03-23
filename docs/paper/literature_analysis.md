# Literature Analysis: Road Climate Resilience

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total references | 27 |
| Year range | 1972--2026 (54 years; core empirical cluster 2016--2026) |
| Peer-reviewed journal articles | 21 |
| Technical reports / policy documents | 4 |
| News articles | 1 |
| Books | 1 |
| Median publication year | 2024 |

### Geographic Coverage

| Region | Papers |
|--------|--------|
| United Kingdom (Cambridge, Bristol, Newcastle, East Midlands, national) | 8 |
| China (Harbin, Hong Kong, multi-city) | 4 |
| Germany | 1 |
| Italy (Brescia) | 1 |
| United States (multi-city) | 2 |
| Multi-country / global | 5 |
| Theoretical / no specific geography | 6 |

### Method Distribution

| Method Category | Count | Papers |
|-----------------|-------|--------|
| Statistical / regression modelling | 7 | hranac2006, cai2016, pulugurtha2021, bi2022, gao2024, becker2026, raccagni2024 |
| Network topology / graph theory | 5 | freeman1977, ganin2017, wassmer2024, li2024, stamos2023 |
| Simulation (agent-based / traffic assignment) | 3 | huang2022, he2026, liu2026 |
| Literature review / bibliometric | 4 | bergantino2024, calvert2018, zhou2026, stamos2023 |
| Curve fitting / empirical function | 1 | pregnolato2017 |
| GLM framework (foundational) | 2 | nelder1972, mccullagh1989 |
| Climate-network integration | 1 | farahmand2024 |
| Policy / evidence assessment | 4 | unece2024, dft2024, nce2026, nh2024 |

---

## Theme-by-Theme Analysis

### Theme A: Climate-Transport Policy and Impact (14 papers)

**Supporting papers:** wan2024paradox, wan2025variability, bergantino2024, farahmand2024, he2026, unece2024, dft2024, zhou2026, stamos2023, liu2026, nce2026, nh2024

**Key convergence:** There is strong consensus that climate change poses escalating risks to transport networks. The DfT rapid evidence assessment (dft2024) concludes that adaptation benefits outweigh costs. The NCE report (nce2026) provides a stark statistic: only 7% of the UK's strategic road network meets drainage standards set two decades ago. National Highways (nh2024) projects that flood risk to English roads will rise from 38% to 46% by 2050.

**Policy gap identified:** While policy documents acknowledge the problem, there is limited evidence of systematic integration between climate projections and transport planning decisions. Farahmand et al. (2024) represent one of the few attempts to bridge this gap through probabilistic network analysis. The UNECE stress test framework (2024) offers a standardised methodology but has not yet been widely adopted.

**Contradictions:** Wan et al. (2024) demonstrate that reduced post-pandemic travel demand does not automatically improve network performance, complicating assumptions that demand management alone addresses resilience.

**Full-text insights (from detailed reading):**
- The DfT REA (2024) is based on screening 158 papers down to 34. It explicitly identifies that precipitation reduces visibility and forces reduced speeds even without road closures, validating speed degradation (not just closure) as a recognised impact pathway. The 2012 Newcastle pluvial flood (50mm in under 2 hours, flooding 377 road links) is cited as a key UK case study. Wider macroeconomic costs of transport disruption are estimated at 2.2 times direct repair costs.
- Zhou et al. (2026) analyse 2000+ publications bibliometrically and identify four major research clusters. Rainfall-transport resilience sits at the intersection of Cluster 1 (climate change impacts) and Cluster 2 (risk and vulnerability assessment). They call for integrated simulation platforms combining urban climatology and infrastructure network science.
- Wan et al. (2025) show substantial intra-week variability in UK travel behaviour using NTS data, cautioning that aggregate metrics mask heterogeneous effects across traveller types -- a methodological warning applicable to rainfall-speed studies.
- Wan et al. (2024) reveal a critical Cambridge-specific finding: post-pandemic car travel fell 11.6% but journey times rose 12% due to road space reallocation and peak-hour congestion shifts. Supply-side interventions for active travel may simultaneously reduce vehicular capacity -- a resilience trade-off.

### Theme B: Precipitation-Speed Relationship (10 papers)

**Supporting papers:** hranac2006, gao2024, pregnolato2017, he2026, becker2026, cai2016, bi2022, li2024, liu2026, raccagni2024

**Key convergence:** All studies confirm that precipitation reduces vehicle speeds. The magnitude varies by context:
- Hranac et al. (2006): 2--6.5% free-flow speed reduction in rain (US freeways)
- Cai et al. (2016): exponential speed-rainfall relationship on urban roads (Hong Kong)
- Gao et al. (2024): 6.7% resilience decrease per 10mm rainfall below 50mm (Harbin)
- Becker et al. (2026): >30% speed reduction under heavy rainfall at 130 km/h speed limits (Germany)
- Pregnolato et al. (2017): nonlinear depth-disruption function with R-squared=0.95 (Newcastle)

**Methodological note:** Earlier studies (hranac2006, cai2016) rely on fixed-point detectors, while recent work (becker2026, li2024) leverages floating car data and weather radar, enabling much higher spatial resolution.

**Unresolved tension:** The functional form of the speed-rainfall relationship remains debated -- linear (becker2026), exponential (cai2016), or threshold-based (li2024 percolation approach). This is likely context-dependent (urban vs. highway, intensity range).

**Full-text insights:**
- Raccagni et al. (2024) model V85 (85th percentile operating speed) as a function of 40+ road characteristics using MLR on 48,000+ spot speed records in Brescia, Italy. Their final model achieves R²_adj = 85.8%. Crucially, they assume normality for V85 and use OLS -- in contrast to a Gamma GLM approach which better handles the positive, right-skewed nature of speed data. Their finding that traffic calming measures (chicanes, speed bumps, traffic islands) have no significant effect on operating speed is surprising and suggests infrastructure interventions may be less effective than assumed.
- Wassmer et al. (2024) provide an important demand-side finding: analysis of the German Mobility Panel shows that car usage increases with rainfall intensity, meaning that rainfall simultaneously degrades road capacity (supply) and increases demand -- compounding congestion effects beyond what speed-reduction models alone capture.

### Theme C: Network Resilience Metrics and Topology (11 papers)

**Supporting papers:** gao2024, bergantino2024, ganin2017, calvert2018, farahmand2024, he2026, zhou2026, wassmer2024, stamos2023, li2024, liu2026

**Foundational reference:** Freeman (1977) provides the betweenness centrality measure that underpins much network resilience analysis.

**Key convergence:** Network topology significantly affects resilience outcomes. Ganin et al. (2017) demonstrate that efficiency and resilience can be opposing properties -- a finding with profound policy implications. Calvert & Snelder (2018) add the recovery dimension through their LPIR indicator, arguing that resistance alone is insufficient.

**Emerging approaches:**
- Percolation theory (li2024, ganin2017): treats network fragmentation as a phase transition
- Gravity-model analysis (wassmer2024): captures cascading disruption beyond directly damaged links
- Agent-based dynamic assignment (he2026, liu2026): models congestion propagation through rerouting behaviour

**Gap:** Stamos (2023) highlights that standard centrality measures require reformulation with traffic-specific parameters -- most current applications use purely topological measures that ignore flow dynamics.

**Full-text insights:**
- Stamos (2023) reviews 17 centrality measures across 4 categories (degree, closeness, betweenness, eigenvector). The key recommendation is that betweenness and closeness centrality should use transit time (not distance) to capture traffic dynamics. Information centrality (measuring efficiency change when a node is removed) is identified as most relevant for disruption assessment. The paper explicitly notes that current traffic flow models assume ideal weather conditions -- the exact gap rainfall-speed modelling addresses.
- Wassmer et al. (2024) apply a novel gravity-model-based traffic centrality measure to the 2021 Ahr Valley flood in Germany. They quantify cascading effects: bridge destruction caused bottlenecks affecting commuter travel times in areas far from the flood epicenter. Their commuter time metric (Delta-T) translates infrastructure failure into aggregate delay -- but treats road failure as binary (open/closed), not the continuous speed degradation that rainfall causes.

### Theme D: Simulation vs. Empirical Methods (16 papers)

**Supporting papers:** wan2024paradox, hranac2006, gao2024, calvert2018, pregnolato2017, he2026, huang2022, becker2026, cai2016, bi2022, li2024, liu2026, raccagni2024, pulugurtha2021, mccullagh1989, nelder1972

**Methodological landscape:**

*Empirical/statistical approaches* dominate the precipitation-speed literature (hranac2006, cai2016, bi2022, becker2026, raccagni2024). These offer external validity but are limited to observed conditions and locations.

*Simulation approaches* (he2026, liu2026, huang2022) enable scenario analysis and counterfactual reasoning but require extensive calibration and validation. Huang et al. (2022) note that agent-based models excel at capturing emergent behaviour but demand significant computational resources.

*Hybrid approaches* are emerging: Liu et al. (2026) embed empirical rainfall-speed relationships within a dynamic traffic assignment framework; Li et al. (2024) combine empirical speed data with percolation theory.

**GLM foundation:** Nelder & Wedderburn (1972) and McCullagh & Nelder (1989) provide the statistical framework for modelling non-normal response variables (e.g., speed, delay, counts) -- directly relevant to a Gamma GLM approach for rainfall-speed modelling.

**Full-text insights:**
- **Critical finding:** Wan et al. (2024) use a **Gamma GLM with log-link** for modelling journey time in Cambridge -- providing a direct methodological precedent within the same DARe project for our rainfall-speed approach. They cite Arezoumandi (2011), Guessous et al. (2014), and Polus (1979) as justification. They also use Breusch-Pagan testing to confirm heteroscedasticity, supporting the choice of Gamma over OLS. Their comprehensive control variable set (hour, day, month, school term, bank holidays, events, roadworks, accidents, weather) provides a template for confounders to account for.
- Raccagni et al. (2024) assume normality and use MLR for speed prediction, achieving R²_adj = 85.8%. This provides a useful comparison: our Gamma GLM is theoretically better suited for speed/time data (positive, right-skewed), and the Wan et al. (2024) precedent from the same project validates this choice.
- Huang et al. (2022) provide a taxonomy of ABM tools (MATSim, SUMO, TRANSIMS, etc.) across time scales. Weather can be modelled as a "disruptor agent" that modifies link speeds. The key limitation is computational cost: microscopic ABMs require large memory and long processing times for city-scale networks. This supports our empirical Gamma GLM approach as a faster, more practical alternative for operational analysis.
- Pulugurtha & Mathew (2021) demonstrate that GWR significantly outperforms OLS for AADT estimation, with spatial non-stationarity as the key finding. This is methodologically relevant if our rainfall-speed model spans heterogeneous geography, supporting the case for spatially-varying coefficients.

**Gap:** Few studies validate simulation results against empirical observations in the same network under the same weather events. Cross-validation between methods remains rare.

### Theme E: Open Data and Platform Approaches (2 papers)

**Supporting papers:** becker2026, li2024

**Key finding:** This is the most under-represented theme. Becker et al. (2026) combine publicly available weather radar data with floating car data. Li et al. (2024) use open traffic data from the East Midlands, UK.

**Critical gap:** No study in this corpus describes an open, reproducible platform for road climate resilience analysis. Most studies use proprietary or restricted datasets. This represents a significant opportunity for new contributions -- particularly platforms that integrate open weather data (e.g., CEDA, Met Office) with open traffic data (e.g., DfT traffic counts, Highways England WebTRIS) and open road network data (e.g., OSM, OS Open Roads).

---

## Full-Text Reading: Critical Discoveries (March 2026)

The following insights emerged only from full-text reading and were not apparent from abstracts or web-search summaries:

1. **Gamma GLM precedent within DARe:** Wan et al. (2024) use Gamma GLM with log-link for Cambridge journey time modelling. This is the strongest methodological precedent for our approach -- same model family, same project, same city. They cite Arezoumandi (2011), Guessous et al. (2014), and Polus (1979) as statistical justification.

2. **Demand-side rainfall effect:** Wassmer et al. (2024) document from the German Mobility Panel that car usage increases with rainfall intensity. This means rainfall simultaneously reduces road capacity (supply) and increases vehicle demand -- a compounding effect that speed-reduction models alone underestimate.

3. **Traffic calming ineffectiveness:** Raccagni et al. (2024) find that chicanes, speed bumps, and traffic islands have no statistically significant effect on V85 in Brescia, despite being widely assumed to reduce speeds. This challenges common assumptions about infrastructure-based speed management.

4. **Macro costs multiplier:** The DfT REA (2024) reports that wider macroeconomic costs of transport disruption are 2.2 times direct repair costs, providing a multiplier for converting speed-based delay estimates to broader economic impact.

5. **Binary vs. continuous degradation:** Wassmer et al. (2024) model road failure as binary (open/closed), while our Gamma GLM approach captures continuous speed degradation. This highlights a gap: most network resilience studies use binary link failure, but rainfall typically causes graduated performance loss -- exactly what our approach addresses.

6. **Bibliometric validation:** Zhou et al. (2026) confirm from 2000+ publications that rainfall-transport resilience sits at the intersection of the two most active research clusters (climate impacts + risk assessment), validating our research positioning.

7. **ABM computational cost:** Huang et al. (2022) document that city-scale agent-based models require significant computational resources and calibration. This supports our empirical statistical approach (Gamma GLM + Streamlit platform) as a faster, more accessible alternative for practitioners and policymakers.

---

## Citation Chain: How Papers Build on Each Other

### Foundational Layer (1972--1989)
```
nelder1972glm --> mccullagh1989glm
                  (GLM theory established)

freeman1977centrality
(Betweenness centrality defined)
```

### Empirical Foundations (2006--2017)
```
nelder1972/mccullagh1989 --> Statistical modelling tradition
                             |
hranac2006 --------> Establishes weather-traffic speed relationships
                     |
cai2016 -----------> Extends to heteroscedastic speed dispersion
                     |
pregnolato2017 ----> Develops depth-disruption function
                     |
freeman1977 --> ganin2017 --> Resilience-efficiency paradox in networks
                |
calvert2018 -----> LPIR: resistance + recovery framework
```

### Modern Integration (2021--2024)
```
hranac2006/cai2016 --> bi2022 --> City-level weather-traffic analysis
                                   |
pregnolato2017 --> gao2024 ------> Resilience to rainfall (road environment)
                    |
ganin2017/calvert2018 --> bergantino2024 --> Systematic review of empirical evidence
                           |
freeman1977/ganin2017 --> stamos2023 --> Centrality measures for climate adaptation
                           |
                    wassmer2024 --> Gravity-model network analysis
                           |
                    li2024 -------> Percolation theory for rainfall resilience
                           |
farahmand2024 ------------> Climate projections + network analysis
                           |
pulugurtha2021 -----------> AADT estimation for local roads (data input)
```

### Cutting Edge (2025--2026)
```
pregnolato2017 + huang2022 --> he2026 --> Agent-based flood-traffic simulation
                                |
hranac2006 + ganin2017 --> liu2026 --> Multi-factor rainfall impact + delay propagation
                                |
becker2026 ----------------> High-resolution radar-FCD speed analysis
                                |
zhou2026 ------------------> Bibliometric synthesis of 30-year field
                                |
wan2024/wan2025 -----------> Post-pandemic travel demand + emissions context
```

### Policy Parallel Track
```
dft2024 ----> UK evidence assessment
nh2024 ----> Strategic road network adaptation
nce2026 ---> Infrastructure deficit reporting
unece2024 -> International stress test framework
```

---

## Knowledge Gaps Identified

1. **Open platform gap (Theme E):** No study provides a reproducible, open-source platform integrating weather, traffic, and network data for road climate resilience analysis. This is the primary gap this research could fill.

2. **UK-specific empirical gap:** Despite strong UK policy interest (dft2024, nh2024, nce2026), most empirical precipitation-speed studies use non-UK data (US, China, Germany). UK-specific quantification using Gamma GLM with local traffic count and rainfall data would be novel.

3. **Functional form consensus gap:** The speed-rainfall relationship lacks a consensus functional form. A Gamma GLM approach offers a principled alternative to ad hoc regression choices, as the Gamma distribution naturally handles positive, right-skewed response variables like speed.

4. **Multi-factor integration gap:** Liu et al. (2026) is the only study integrating multiple rainfall impact pathways (flooding, visibility, signals). Most studies isolate a single mechanism, underestimating compound effects.

5. **Temporal resolution gap:** Most studies aggregate to hourly or daily time scales. Sub-hourly analysis linking rainfall intensity bursts to real-time speed changes is rare (only becker2026 approaches this with 5-minute radar data).

6. **Recovery dynamics gap:** Calvert & Snelder (2018) highlight recovery as essential to resilience, but few empirical studies measure how quickly traffic speeds return to normal after rainfall cessation.

7. **Local road gap:** Most network resilience studies focus on highways and strategic roads. Pulugurtha & Mathew (2021) address local road traffic estimation, but resilience of local road networks under rainfall is largely unstudied.

8. **Validation gap:** Cross-validation between simulation predictions and empirical observations under the same conditions is almost entirely absent from the literature.

---

## Methodological Trends

1. **Shift from fixed-point to floating car data:** Earlier studies (hranac2006, cai2016) rely on loop detectors and video; recent work (becker2026, li2024) uses GPS-based floating car data enabling network-wide coverage.

2. **Growing use of network science:** Percolation theory (li2024, ganin2017), centrality measures (stamos2023, freeman1977), and gravity models (wassmer2024) are increasingly applied to transport resilience -- imported from physics and complex systems science.

3. **Agent-based modelling emergence:** MATSim and similar platforms (he2026, huang2022) are becoming standard for simulating flood-traffic interactions, enabling scenario analysis that empirical methods cannot provide.

4. **Climate projection integration:** Farahmand et al. (2024) represent an emerging trend of coupling downscaled climate projections with transport network models -- still rare but likely to grow.

5. **Policy-research convergence:** The UNECE framework (2024) and DfT REA (2024) signal that policymakers are actively seeking evidence-based tools for climate-transport decision-making, creating demand for the type of platform-based, empirical approach this research proposes.

6. **Bibliometric maturation:** Zhou et al. (2026) and Bergantino et al. (2024) indicate the field has accumulated enough literature for systematic review and bibliometric analysis -- a sign of disciplinary maturation.
