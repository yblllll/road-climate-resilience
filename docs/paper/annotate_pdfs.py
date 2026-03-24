#!/usr/bin/env python3
"""
Annotate literature PDFs with color-coded highlights + explanatory notes.
Blue=Method, Green=Conclusion, Orange=Innovation, Red=Limitation
Uses PyMuPDF (fitz) 1.27.2

Key design: each annotation has a PHRASE (for search) and a NOTE (explaining why
this passage matters). The popup note is what the reader sees when hovering.
"""
import fitz
import os
import re

PAPER_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(PAPER_DIR, "Literature_Review")

COLORS = {
    "method":     (0.204, 0.596, 0.859),
    "conclusion": (0.298, 0.686, 0.314),
    "innovation": (0.953, 0.612, 0.071),
    "limitation": (0.906, 0.298, 0.235),
}

LABEL = {
    "method":     "[METHOD]",
    "conclusion": "[CONCLUSION]",
    "innovation": "[INNOVATION]",
    "limitation": "[LIMITATION]",
}

# Each entry: (search_phrase, explanatory_note)
# search_phrase: 10-25 word distinctive fragment from the paper
# explanatory_note: why this passage matters for our research
ANNOTATIONS = {
    "Wan_2024_Paradox_Post_Pandemic_Travel.pdf": {
        "method": [
            ("generalised linear model using Gamma distribution with a log-link",
             "KEY: This is the Gamma GLM with log-link — the same model family we use for rainfall-speed. Direct methodological precedent within the DARe project."),
            ("negative binomial regression",
             "NB regression handles overdispersed count data (traffic volumes). Complementary to Gamma GLM for continuous journey time."),
        ],
        "conclusion": [
            ("Car and cycle demand during the post-pandemic stabilised",
             "Core finding: car demand fell 11.6%, cycle 15.8% below pre-pandemic — yet congestion worsened. This is the 'paradox'."),
            ("daily average journey time on key transport corridors has increased by 12.0%",
             "Despite lower demand, journey times rose 12%. Attributed to road space reallocation for cycling infrastructure."),
        ],
        "innovation": [
            ("one of the first empirical studies identifying and probing into the paradoxical relationship",
             "Claims novelty as first empirical study of the demand-congestion paradox in post-pandemic cities."),
        ],
        "limitation": [
            ("generalisability of our findings is yet to be tested",
             "Cambridge-specific results. Our work on UK SRN provides broader geographic coverage."),
            ("inherent limitation with the analysis of traffic counts is the lack of information on socio-economic background",
             "No traveller demographics — only aggregate vehicle counts from cameras."),
        ],
    },
    "Wan_2025_Transport_Emissions_Policy.pdf": {
        "method": [
            ("latent traveller groups based on their weekly total travel emissions and intra-week emissions variability using a latent profile model",
             "Latent Profile Model: identifies unobserved groups of travellers with similar emission patterns. Applied to 2019 English NTS data."),
        ],
        "conclusion": [
            ("SEC variable is no longer significant after controlling for the effects of trip distance, day, mode and purpose",
             "KEY: Socio-economic status dissolves as a predictor once you control for compositional factors. Warning for our rainfall-speed work: aggregate correlations may be driven by confounders."),
        ],
        "innovation": [
            ("transferable method for identifying latent travel emissions groups",
             "Novel application of LPM to travel emissions. Shows that behaviour-based segmentation outperforms socio-economic categories."),
        ],
        "limitation": [
            ("analyses presented are descriptive in nature thus focusing on correlations only",
             "Cannot establish causation. Same limitation applies to our cross-sectional rainfall-speed analysis."),
        ],
    },
    "Becker_2026_Impact_Rainfall_Driving_Speed.pdf": {
        "method": [
            ("combine GNSS-based floating car data with such calibrated radar-based measurements",
             "Core method: FCD + weather radar fusion. Similar data integration approach to our work (traffic sensors + rain gauges)."),
            ("average driving speed of all vehicles contributing a measurement within a 5 min interval",
             "5-minute temporal resolution. Compare with our hourly aggregation — their granularity is finer."),
        ],
        "conclusion": [
            ("average speed reductions is -8% at speed limits of 50 km/h and -31% at 130 km/h",
             "KEY FINDING: Heavy rain cuts speeds 8-31% depending on speed limit zone. Higher-speed roads suffer more. Compare with Hranac (2006): 2-6.5%."),
        ],
        "innovation": [
            ("combination of floating car data with high-resolution radar-based rainfall estimates",
             "First study at this spatial/temporal resolution for rainfall-speed. Our innovation is different: Gamma GLM framework + open platform."),
        ],
        "limitation": [
            ("limited number of rainfall events",
             "Only 3 summer days with heavy rainfall. Our multi-year dataset provides much larger sample."),
            ("estimates of rainfall effects at higher intensities remain uncertain",
             "Small sample at extreme intensities. A general challenge — also relevant to our Gamma GLM tail estimates."),
        ],
    },
    "Gao_2024_Resilience_Road_Traffic_Rainfall.pdf": {
        "method": [
            ("probabilistic model",
             "Probabilistic resilience modelling framework. Classifies road segments by surrounding environment characteristics."),
        ],
        "conclusion": [
            ("resilience decrease",
             "Resilience decreases ~6.7% per 10mm rainfall below 50mm threshold. Key quantitative benchmark for rainfall-resilience relationship."),
        ],
        "innovation": [
            ("road environment characteristics",
             "Goes beyond rainfall intensity to consider road context (land use, geometry, connectivity). Our Gamma GLM could incorporate similar covariates."),
        ],
        "limitation": [
            ("single city",
             "Harbin-only study. Winter-dominated climate differs from UK maritime climate. Our UK SRN data fills this geographic gap."),
        ],
    },
    "Pregnolato_2017_Flood_Impact_Road_Transport.pdf": {
        "method": [
            ("depth-disruption",
             "Depth-disruption function: relates flood water depth to vehicle speed reduction. Curve fitted to observed data."),
        ],
        "conclusion": [
            ("nonlinear",
             "Nonlinear relationship: speed drops gradually at low depths then accelerates. R²=0.95. At 300mm most vehicles stop."),
        ],
        "innovation": [
            ("continuous function",
             "INNOVATION: Replaces the binary open/closed assumption with continuous degradation. Our Gamma GLM does the same for rainfall intensity (not flood depth)."),
        ],
        "limitation": [
            ("limited sample",
             "Based on limited historical Newcastle flood events. Small dataset — our multi-year FCD provides much larger sample."),
        ],
    },
    "Ganin_2017_Resilience_Efficiency_Transportation_Networks.pdf": {
        "method": [
            ("percolation",
             "Percolation theory applied to 40 US urban road networks. Tests network behaviour under progressive node removal."),
        ],
        "conclusion": [
            ("trade-off",
             "KEY: Efficiency and resilience are opposing network properties. Designing for one often sacrifices the other."),
        ],
        "innovation": [
            ("resilience-efficiency",
             "First large-scale empirical evidence of the resilience-efficiency trade-off in real transport networks. Published in Science Advances."),
        ],
        "limitation": [
            ("purely topological",
             "Ignores actual traffic flows, speeds, and weather. Our Gamma GLM addresses link-level performance, not just topology."),
        ],
    },
    "Calvert_2018_Road_Traffic_Resilience_Methodology.pdf": {
        "method": [
            ("resistance and recovery",
             "LPIR indicator: quantifies both how much performance drops (resistance) and how fast it returns (recovery)."),
        ],
        "conclusion": [
            ("recovery",
             "Recovery speed matters as much as resistance magnitude. Two networks with equal resistance can have very different resilience."),
        ],
        "innovation": [
            ("single metric",
             "First to combine resistance + recovery in one indicator. Our speed-rainfall model captures resistance; recovery measurement is future work."),
        ],
        "limitation": [
            ("single corridor",
             "Tested on one motorway corridor only. Limited scale validation."),
        ],
    },
    "He_2026_Flood_ABM_Bristol.pdf": {
        "method": [
            ("agent-based",
             "MATSim agent-based microsimulation coupled with flood hazard model. Each vehicle is an independent agent making routing decisions."),
        ],
        "conclusion": [
            ("congestion propagates far beyond",
             "KEY: Flood disruption cascades through rerouting — congested area much larger than flooded area."),
        ],
        "innovation": [
            ("dynamic traffic assignment",
             "First coupling of detailed flood hazard with full ABM for a UK city (Bristol). Captures emergent congestion patterns."),
        ],
        "limitation": [
            ("computational cost",
             "City-scale ABM is computationally expensive. Our empirical Gamma GLM + Streamlit is much faster for operational use."),
        ],
    },
    "Huang_2022_Agent_Based_Models_Transport_Simulation.pdf": {
        "method": [
            ("agent-based model",
             "Review of ABM platforms (MATSim, SUMO, TRANSIMS, AnyLogic, NetLogo) categorized by temporal scale."),
        ],
        "conclusion": [
            ("calibration",
             "KEY limitation of ABMs: no standard calibration guidelines exist. Supports our choice of empirical Gamma GLM as more practical."),
        ],
        "innovation": [
            ("taxonomy",
             "Comprehensive ABM toolkit taxonomy. Notes weather can be modelled as a 'disruptor agent'."),
        ],
        "limitation": [
            ("computational resources",
             "ABMs require significant computing power for city-scale analysis. Our statistical approach is orders of magnitude faster."),
        ],
    },
    "Zhou_2026_Bibliometric_Transport_Climate.pdf": {
        "method": [
            ("VOSviewer",
             "Bibliometric tools: VOSviewer for keyword co-occurrence, CiteSpace for burst detection. 2,133 publications analysed."),
        ],
        "conclusion": [
            ("sustainability and resilience",
             "Strongest keyword burst (strength 10.69, 2021-present). Validates that resilience is the hottest topic in transport-climate research."),
        ],
        "innovation": [
            ("bibliometric mapping",
             "First 30-year bibliometric survey of the field. Identifies four research clusters and three evolutionary phases."),
        ],
        "limitation": [
            ("Web of Science",
             "WoS-only database. Misses non-English literature (significant in Chinese transport research)."),
        ],
    },
    "Wassmer_2024_Resilience_Transportation_Infrastructure_Road_Failures.pdf": {
        "method": [
            ("gravity model",
             "Gravity-model-based spatial interaction betweenness centrality (SIBC). Uses OSM road network + GHSL population."),
        ],
        "conclusion": [
            ("cascading",
             "Disruption cascades 50km from Ahr Valley flood epicenter. One critical bridge caused most commuter delay."),
        ],
        "innovation": [
            ("spatial interaction",
             "Novel gravity-model centrality measure. Delta-T metric translates infrastructure failure to commuter time cost."),
        ],
        "limitation": [
            ("binary",
             "CONTRAST: Treats roads as binary open/closed. Our Gamma GLM captures continuous speed degradation — more realistic for rainfall."),
        ],
    },
    "Stamos_2023_Transportation_Networks_Climate_Change_Centrality.pdf": {
        "method": [
            ("centrality measures",
             "Reviews 17 centrality measures and assesses which are useful for transport climate adaptation. Proposes reformulations."),
        ],
        "conclusion": [
            ("transit time",
             "KEY: Betweenness/closeness should use transit time, not distance. Weather-degraded speeds change which nodes are critical."),
        ],
        "innovation": [
            ("transport-relevant",
             "First systematic assessment of centrality usability for transport. Notes traffic models assume ideal weather — the gap we fill."),
        ],
        "limitation": [
            ("no empirical validation",
             "Purely theoretical reformulations — not tested on real networks. An empirical test using our rainfall-speed data would be novel."),
        ],
    },
    "Raccagni_2024_Urban_Road_Vehicle_Speed.pdf": {
        "method": [
            ("85th percentile",
             "Models V85 (85th percentile operating speed) using 48,000+ spot speed measurements and 40+ road characteristics."),
        ],
        "conclusion": [
            ("traffic calming",
             "SURPRISING: Traffic calming measures (chicanes, bumps, islands) have NO significant effect on V85. Road geometry dominates."),
        ],
        "innovation": [
            ("48,000",
             "Largest urban V85 dataset in the literature. R²_adj = 85.8% from road geometry alone."),
        ],
        "limitation": [
            ("normality",
             "CONTRAST: Assumes normality for V85 and uses OLS. Our Gamma GLM is theoretically better for positive, right-skewed speed data."),
        ],
    },
    "Cai_2016_Rainfall_Speed_Dispersion.pdf": {
        "method": [
            ("speed dispersion",
             "Models both mean speed and speed variance (dispersion) as functions of rainfall intensity. Uses loop detector data from Hong Kong."),
        ],
        "conclusion": [
            ("exponentially",
             "Speed dispersion increases exponentially with rainfall — not just mean speed drops, variance widens. Safety implications."),
        ],
        "innovation": [
            ("heteroscedastic",
             "First to model heteroscedastic speed variance under rainfall. Directly supports our Gamma GLM choice (handles non-constant variance)."),
        ],
        "limitation": [
            ("Hong Kong",
             "Hong Kong-specific. Loop detector data only (fixed-point). Our FCD provides network-wide UK coverage."),
        ],
    },
    "Bi_2022_Weather_Urban_Traffic.pdf": {
        "method": [
            ("decision tree",
             "Regression + decision tree hybrid for weather-traffic analysis. City-level aggregated traffic index data."),
        ],
        "conclusion": [
            ("varies by city",
             "Rainfall-congestion relationship varies significantly across cities. One-size-fits-all adjustment factors are inappropriate."),
        ],
        "innovation": [
            ("multiple cities",
             "First multi-city comparison of weather-traffic. Demonstrates context-dependency of weather impacts."),
        ],
        "limitation": [
            ("aggregated",
             "City-level aggregation loses link-level detail. Our Gamma GLM operates at individual road segment level."),
        ],
    },
    "Li_2024_Percolation_Highway_Rainfall.pdf": {
        "method": [
            ("speed decline rate",
             "Uses speed decline rate as percolation indicator. Applied to East Midlands UK highway network with real traffic data."),
        ],
        "conclusion": [
            ("critical rainfall",
             "Critical thresholds exist: gradual degradation below, rapid connectivity collapse above. Phase transition behaviour."),
        ],
        "innovation": [
            ("functional degradation",
             "INNOVATION: First percolation theory for functional (speed) degradation, not just physical link removal. UK data."),
        ],
        "limitation": [
            ("East Midlands",
             "East Midlands only. Static network (no rerouting). Our Gamma GLM could provide speed inputs for dynamic percolation analysis."),
        ],
    },
    "Liu_2026_Extreme_Rainfall_Resilience.pdf": {
        "method": [
            ("Link Transmission Model",
             "Dynamic traffic assignment using LTM. Integrates three rainfall pathways: flooding + speed reduction + signal failure."),
        ],
        "conclusion": [
            ("multi-factor",
             "Multi-factor compound delays far exceed single-factor estimates. Most studies only model one pathway (e.g., just flooding)."),
        ],
        "innovation": [
            ("three rainfall pathways",
             "INNOVATION: First to integrate flooding + speed + signals in one framework. Our Gamma GLM provides the speed reduction component."),
        ],
        "limitation": [
            ("hypothetical",
             "Based on hypothetical scenarios, not observed events. Our approach uses actual observed rainfall and speed data."),
        ],
    },
    "Pulugurtha_2021_AADT_Local_Roads.pdf": {
        "method": [
            ("geographically weighted regression",
             "GWR vs OLS for AADT estimation. GWR allows regression coefficients to vary spatially — captures local context."),
        ],
        "conclusion": [
            ("outperforms",
             "GWR significantly outperforms OLS. Spatial non-stationarity is the key finding — relationships vary by location."),
        ],
        "innovation": [
            ("spatially varying",
             "Demonstrates that traffic-environment relationships are spatially non-stationary. Supports GWR-type extensions of our Gamma GLM."),
        ],
        "limitation": [
            ("low R-squared",
             "Low R² (0.20-0.33) for local road models. High variability in local road traffic is inherently harder to predict."),
        ],
    },
    "Hranac_2006_Traffic_Inclement_Weather.pdf": {
        "method": [
            ("weather adjustment",
             "Develops weather adjustment factors for the speed-flow relationship using empirical loop detector data from US freeways."),
        ],
        "conclusion": [
            ("free-flow speed",
             "Rain reduces free-flow speed by 2-6.5% and capacity by 4-11%. These are the benchmark figures cited for 20 years."),
        ],
        "innovation": [
            ("speed-at-capacity",
             "First comprehensive quantification of weather effects on speed-flow curves. Still the reference baseline."),
        ],
        "limitation": [
            ("freeway",
             "US freeway data only. Pre-2006 detector technology. Our Gamma GLM uses modern FCD with higher resolution."),
        ],
    },
    "DfT_2024_Climate_Transport_REA.pdf": {
        "method": [
            ("rapid evidence assessment",
             "UK government REA: screened 1,583 sources down to 34. PRISMA-compliant. Covers roads, rail, aviation, maritime."),
        ],
        "conclusion": [
            ("adaptation benefits outweigh",
             "KEY POLICY: Adaptation benefits outweigh costs. Wider economic costs are 2.2x direct repair costs. Emergency repairs 2-10x planned."),
        ],
        "innovation": [
            ("speed degradation",
             "Recognises speed degradation (not just road closure) as a valid impact pathway. Validates our Gamma GLM approach."),
        ],
        "limitation": [
            ("no single database",
             "No systematic database of weather-transport events exists in the UK. Our Streamlit platform begins to address this."),
        ],
    },
    "Bergantino_2024_Transport_Network_Resilience.pdf": {
        "method": [
            ("systematic review",
             "PRISMA-guided review of 53 empirical transport resilience papers. Classifies by method, scale, and hazard type."),
        ],
        "conclusion": [
            ("empirical evidence",
             "Empirical resilience evidence is growing but methods remain fragmented across disciplines. Standardisation needed."),
        ],
        "innovation": [
            ("first systematic review",
             "First review focused specifically on EMPIRICAL (not theoretical) resilience studies. Maps the methodological landscape."),
        ],
        "limitation": [
            ("publication bias",
             "English-language bias and likely publication bias toward positive findings."),
        ],
    },
}


COLOR_RGB_255 = {
    "method":     (52, 152, 219),
    "conclusion": (76, 175, 80),
    "innovation": (243, 156, 18),
    "limitation": (231, 76, 60),
}

CATEGORY_TITLES = {
    "method":     "METHOD (Blue highlights in text)",
    "conclusion": "CONCLUSION (Green highlights in text)",
    "innovation": "INNOVATION (Orange highlights in text)",
    "limitation": "LIMITATION (Red highlights in text)",
}


def draw_cover_page(doc, filename, passages):
    """Insert a summary cover page at the beginning of the PDF."""
    # A4-ish page
    width, height = 595, 842
    page = doc.new_page(pno=0, width=width, height=height)

    # Title bar
    title_rect = fitz.Rect(0, 0, width, 60)
    page.draw_rect(title_rect, color=(0, 0.16, 0.37), fill=(0, 0.16, 0.37))
    page.insert_text((20, 40), "LITERATURE REVIEW ANNOTATION SUMMARY",
                     fontsize=16, color=(1, 1, 1), fontname="helv")

    # Paper name
    short_name = filename.replace(".pdf", "").replace("_", " ")
    page.insert_text((20, 85), short_name,
                     fontsize=12, color=(0, 0.16, 0.37), fontname="helv")

    # Color legend
    page.insert_text((20, 110), "Color Legend:",
                     fontsize=9, color=(0.4, 0.4, 0.4), fontname="helv")
    legend_y = 125
    for cat, (r, g, b) in COLOR_RGB_255.items():
        rf, gf, bf = r/255, g/255, b/255
        dot_rect = fitz.Rect(25, legend_y - 6, 35, legend_y + 4)
        page.draw_rect(dot_rect, color=(rf, gf, bf), fill=(rf, gf, bf))
        page.insert_text((42, legend_y + 2), f"= {cat.upper()}",
                         fontsize=8, color=(0.3, 0.3, 0.3), fontname="helv")
        legend_y += 16

    # Separator
    y = legend_y + 10
    page.draw_line((20, y), (width - 20, y), color=(0.8, 0.8, 0.8), width=0.5)
    y += 20

    # Annotations content
    for category in ["method", "conclusion", "innovation", "limitation"]:
        items = passages.get(category, [])
        if not items:
            continue

        r, g, b = COLOR_RGB_255[category]
        rf, gf, bf = r/255, g/255, b/255

        # Category header with colored bar
        bar_rect = fitz.Rect(20, y - 2, 24, y + 12)
        page.draw_rect(bar_rect, color=(rf, gf, bf), fill=(rf, gf, bf))
        page.insert_text((30, y + 10), CATEGORY_TITLES[category],
                         fontsize=10, color=(rf, gf, bf), fontname="helv")
        y += 22

        for phrase, note in items:
            if y > height - 60:
                # New page if running out of space
                page = doc.new_page(pno=doc.page_count - (doc.page_count - 1), width=width, height=height)
                y = 40

            # Search phrase (what's highlighted in the paper)
            search_label = f'Search: "{phrase}"'
            if len(search_label) > 90:
                search_label = search_label[:87] + '..."'
            page.insert_text((35, y + 10), search_label,
                             fontsize=8, color=(0.3, 0.3, 0.3), fontname="helv")
            y += 14

            # Explanatory note (the important part)
            # Word-wrap the note to fit page width
            note_lines = wrap_text(note, max_chars=80)
            for line in note_lines:
                if y > height - 40:
                    page = doc.new_page(pno=doc.page_count - (doc.page_count - 1), width=width, height=height)
                    y = 40
                page.insert_text((45, y + 10), line,
                                 fontsize=9, color=(0.15, 0.15, 0.15), fontname="helv")
                y += 13

            y += 8  # spacing between entries

        y += 10  # spacing between categories

    # Footer
    if y < height - 30:
        page.insert_text((20, height - 25),
                         "Generated by DARe Literature Review Annotation Tool | Highlights appear in the paper text with matching colors",
                         fontsize=7, color=(0.6, 0.6, 0.6), fontname="helv")


def wrap_text(text, max_chars=80):
    """Simple word-wrap."""
    words = text.split()
    lines = []
    current = ""
    for w in words:
        if len(current) + len(w) + 1 > max_chars:
            lines.append(current)
            current = w
        else:
            current = f"{current} {w}" if current else w
    if current:
        lines.append(current)
    return lines


def search_and_highlight(page, phrase, color, note, category):
    """Search for phrase on page. If found, add highlight. Returns count."""
    instances = page.search_for(phrase, quads=False)
    count = 0
    for rect in instances:
        try:
            hl = page.add_highlight_annot(rect)
            hl.set_colors(stroke=color)
            hl.set_info(title=LABEL[category], content=note)
            hl.update()
            count += 1
        except Exception:
            pass
    return count


def annotate_pdf(filename, passages):
    """Insert cover page + highlight text in a single PDF."""
    input_path = os.path.join(PDF_DIR, filename)
    if not os.path.exists(input_path):
        print(f"  SKIP: not found")
        return False, {}

    base = os.path.splitext(filename)[0]
    output_path = os.path.join(PDF_DIR, f"{base}_annotated.pdf")

    doc = fitz.open(input_path)

    # 1) Insert summary cover page at the beginning
    draw_cover_page(doc, filename, passages)

    # 2) Highlight phrases in the paper (pages shifted by cover page count)
    counts = {k: 0 for k in COLORS}
    # Find how many cover pages were inserted (usually 1, maybe 2 for long annotations)
    # We start searching from page index after cover pages
    # Actually, since cover pages are inserted at pno=0, the original pages shift.
    # We search ALL pages — cover page text won't match paper phrases.
    for category, items in passages.items():
        color = COLORS[category]
        for phrase, note in items:
            found = False
            for page_num in range(len(doc)):
                page = doc[page_num]
                n = search_and_highlight(page, phrase, color, note, category)
                if n > 0:
                    counts[category] += n
                    found = True
            if not found:
                # Fallback: try first 6 words
                words = phrase.split()
                if len(words) > 6:
                    short = " ".join(words[:6])
                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        n = search_and_highlight(page, short, color, f"(partial) {note}", category)
                        if n > 0:
                            counts[category] += min(n, 2)
                            found = True
                            break
                if not found:
                    print(f"    MISS: [{category}] \"{phrase[:50]}...\"")

    total = sum(counts.values())
    doc.save(output_path)
    print(f"  Cover page + {total} highlights (M:{counts['method']} C:{counts['conclusion']} I:{counts['innovation']} L:{counts['limitation']})")
    doc.close()
    return True, counts


def main():
    print(f"PDF Annotation Tool v3 (cover page + highlights)")
    print(f"Directory: {PDF_DIR}")
    print(f"PyMuPDF: {fitz.__version__}")
    print(f"Papers: {len(ANNOTATIONS)}")
    print("=" * 60)

    success = 0
    totals = {k: 0 for k in COLORS}

    for filename, passages in ANNOTATIONS.items():
        print(f"\n{filename}")
        ok, counts = annotate_pdf(filename, passages)
        if ok:
            success += 1
            for k in counts:
                totals[k] += counts[k]

    print(f"\n{'=' * 60}")
    print(f"Done: {success}/{len(ANNOTATIONS)} PDFs")
    print(f"Highlights: {sum(totals.values())} (M:{totals['method']} C:{totals['conclusion']} I:{totals['innovation']} L:{totals['limitation']})")


if __name__ == "__main__":
    main()
