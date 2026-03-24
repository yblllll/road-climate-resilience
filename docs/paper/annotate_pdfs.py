#!/usr/bin/env python3
"""
Annotate literature PDFs with color-coded highlights.
Blue=Method, Green=Conclusion, Orange=Innovation, Red=Limitation
Uses PyMuPDF (fitz) 1.27.2
"""
import fitz
import os
import sys

PAPER_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(PAPER_DIR, "Literature_Review")

# RGB floats for PyMuPDF highlight annotations
COLORS = {
    "method":     (0.204, 0.596, 0.859),   # Blue #3498db
    "conclusion": (0.298, 0.686, 0.314),   # Green #4CAF50
    "innovation": (0.953, 0.612, 0.071),   # Orange #f39c12
    "limitation": (0.906, 0.298, 0.235),   # Red #e74c3c
}

# Search phrases: 5-10 words, distinctive enough to avoid false positives
ANNOTATIONS = {
    "Becker_2026_Impact_Rainfall_Driving_Speed.pdf": {
        "method": [
            "floating car data",
            "weather radar data",
            "linear regression",
        ],
        "conclusion": [
            "speed reduction of more than 30",
            "higher speed limits show larger",
            "heavy rainfall events",
        ],
        "innovation": [
            "high-resolution weather radar",
            "1.5 million road-section",
        ],
        "limitation": [
            "linear relationship between rainfall",
            "only highway",
            "German Autobahn",
        ],
    },
    "Gao_2024_Resilience_Road_Traffic_Rainfall.pdf": {
        "method": [
            "probabilistic model",
            "hierarchical clustering",
            "road environment",
        ],
        "conclusion": [
            "resilience decrease",
            "6.7%",
            "50 mm",
        ],
        "innovation": [
            "road environment characteristics",
            "land use",
        ],
        "limitation": [
            "Harbin",
            "single city",
            "winter conditions",
        ],
    },
    "Bergantino_2024_Transport_Network_Resilience.pdf": {
        "method": [
            "systematic review",
            "empirical studies",
            "PRISMA",
        ],
        "conclusion": [
            "spatial resilience",
            "topology and land use",
            "empirical evidence",
        ],
        "innovation": [
            "first systematic review",
            "empirical resilience",
        ],
        "limitation": [
            "English-language",
            "publication bias",
        ],
    },
    "Ganin_2017_Resilience_Efficiency_Transportation_Networks.pdf": {
        "method": [
            "percolation theory",
            "40 urban areas",
            "network topology",
        ],
        "conclusion": [
            "resilience and efficiency",
            "trade-off",
            "efficient networks",
        ],
        "innovation": [
            "large-scale",
            "resilience-efficiency",
        ],
        "limitation": [
            "purely topological",
            "ignores traffic flow",
        ],
    },
    "Calvert_2018_Road_Traffic_Resilience_Methodology.pdf": {
        "method": [
            "level of service",
            "resistance and recovery",
            "resilience indicator",
        ],
        "conclusion": [
            "resistance alone is insufficient",
            "recovery",
        ],
        "innovation": [
            "resistance and recovery",
            "single metric",
        ],
        "limitation": [
            "single corridor",
            "limited empirical validation",
        ],
    },
    "Pregnolato_2017_Flood_Impact_Road_Transport.pdf": {
        "method": [
            "depth-disruption",
            "curve fitting",
            "video analysis",
        ],
        "conclusion": [
            "nonlinear",
            "R-squared",
            "300 mm",
        ],
        "innovation": [
            "continuous function",
            "depth-disruption function",
            "binary",
        ],
        "limitation": [
            "Newcastle",
            "historical events",
            "limited sample",
        ],
    },
    "He_2026_Flood_ABM_Bristol.pdf": {
        "method": [
            "agent-based",
            "MATSim",
            "flood hazard",
        ],
        "conclusion": [
            "congestion propagates far beyond",
            "rerouting",
            "flooded areas",
        ],
        "innovation": [
            "coupled flood hazard",
            "dynamic traffic assignment",
        ],
        "limitation": [
            "Bristol",
            "computational cost",
            "binary flood",
        ],
    },
    "Huang_2022_Agent_Based_Models_Transport_Simulation.pdf": {
        "method": [
            "agent-based model",
            "MATSim",
            "TRANSIMS",
            "AnyLogic",
        ],
        "conclusion": [
            "emergent behaviour",
            "calibration",
            "computational",
        ],
        "innovation": [
            "taxonomy",
            "temporal scale",
        ],
        "limitation": [
            "no standard",
            "calibration guidelines",
            "computational resources",
        ],
    },
    "Zhou_2026_Bibliometric_Transport_Climate.pdf": {
        "method": [
            "VOSviewer",
            "CiteSpace",
            "bibliometric",
            "keyword co-occurrence",
        ],
        "conclusion": [
            "four major",
            "research cluster",
            "sustainability and resilience",
        ],
        "innovation": [
            "30-year",
            "bibliometric mapping",
        ],
        "limitation": [
            "Web of Science",
            "non-English",
            "quality of individual studies",
        ],
    },
    "Wassmer_2024_Resilience_Transportation_Infrastructure_Road_Failures.pdf": {
        "method": [
            "gravity model",
            "OpenStreetMap",
            "betweenness centrality",
        ],
        "conclusion": [
            "50 km",
            "cascading",
            "commuter time",
        ],
        "innovation": [
            "gravity-model",
            "spatial interaction",
        ],
        "limitation": [
            "binary",
            "open or closed",
            "static occupancy",
        ],
    },
    "Wan_2024_Paradox_Post_Pandemic_Travel.pdf": {
        "method": [
            "Gamma generalised linear model",
            "negative binomial",
            "Breusch-Pagan",
        ],
        "conclusion": [
            "11.6%",
            "journey times rose",
            "road space reallocation",
        ],
        "innovation": [
            "Gamma GLM",
            "post-pandemic",
            "natural experiment",
        ],
        "limitation": [
            "Cambridge",
            "preprint",
            "separate camera sets",
        ],
    },
    "Wan_2025_Transport_Emissions_Policy.pdf": {
        "method": [
            "latent profile",
            "National Travel Survey",
            "coefficient of variation",
        ],
        "conclusion": [
            "socio-economic",
            "insignificant",
            "compositional",
        ],
        "innovation": [
            "latent profile",
            "unobserved",
            "traveller groups",
        ],
        "limitation": [
            "descriptive",
            "one-week",
            "no built-environment",
        ],
    },
    "Stamos_2023_Transportation_Networks_Climate_Change_Centrality.pdf": {
        "method": [
            "centrality measures",
            "reformulation",
            "17",
        ],
        "conclusion": [
            "transit time",
            "information centrality",
            "betweenness",
        ],
        "innovation": [
            "systematic assessment",
            "transport-relevant",
        ],
        "limitation": [
            "purely theoretical",
            "no empirical validation",
            "node-based",
        ],
    },
    "Raccagni_2024_Urban_Road_Vehicle_Speed.pdf": {
        "method": [
            "multiple linear regression",
            "85th percentile",
            "spot speed",
        ],
        "conclusion": [
            "85.8%",
            "road geometry",
            "traffic calming",
        ],
        "innovation": [
            "48,000",
            "largest",
            "traffic calming measures",
        ],
        "limitation": [
            "normality",
            "OLS",
            "single city",
            "cross-sectional",
        ],
    },
    "Cai_2016_Rainfall_Speed_Dispersion.pdf": {
        "method": [
            "exponential",
            "loop detector",
            "speed dispersion",
        ],
        "conclusion": [
            "dispersion increases",
            "exponentially",
            "rainfall intensity",
        ],
        "innovation": [
            "heteroscedastic",
            "speed variance",
        ],
        "limitation": [
            "Hong Kong",
            "limited rainfall intensity",
            "fixed-point",
        ],
    },
    "Bi_2022_Weather_Urban_Traffic.pdf": {
        "method": [
            "decision tree",
            "regression",
            "city-level",
        ],
        "conclusion": [
            "precipitation",
            "congestion",
            "varies by city",
        ],
        "innovation": [
            "multiple cities",
            "data-driven",
        ],
        "limitation": [
            "aggregated",
            "limited weather",
            "Chinese cities",
        ],
    },
    "Li_2024_Percolation_Highway_Rainfall.pdf": {
        "method": [
            "percolation theory",
            "speed decline rate",
            "phase transition",
        ],
        "conclusion": [
            "critical rainfall",
            "threshold",
            "connectivity degrades sharply",
        ],
        "innovation": [
            "functional degradation",
            "percolation",
            "speed reduction",
        ],
        "limitation": [
            "East Midlands",
            "parameter",
            "static network",
        ],
    },
    "Liu_2026_Extreme_Rainfall_Resilience.pdf": {
        "method": [
            "Link Transmission Model",
            "dynamic traffic assignment",
            "three",
        ],
        "conclusion": [
            "multi-factor",
            "much larger",
            "cascading delays",
        ],
        "innovation": [
            "three rainfall pathways",
            "delay propagation",
            "first framework",
        ],
        "limitation": [
            "hypothetical",
            "simplified demand",
            "network-specific",
        ],
    },
    "Pulugurtha_2021_AADT_Local_Roads.pdf": {
        "method": [
            "geographically weighted regression",
            "ordinary least squares",
            "AADT",
        ],
        "conclusion": [
            "GWR",
            "outperforms",
            "road density",
        ],
        "innovation": [
            "spatially varying",
            "local roads",
        ],
        "limitation": [
            "low R-squared",
            "county-specific",
            "27%",
        ],
    },
    "Hranac_2006_Traffic_Inclement_Weather.pdf": {
        "method": [
            "loop detector",
            "empirical",
            "weather adjustment",
        ],
        "conclusion": [
            "free-flow speed",
            "2% to 6.5%",
            "capacity",
        ],
        "innovation": [
            "weather adjustment factors",
            "speed-at-capacity",
        ],
        "limitation": [
            "freeway",
            "limited weather",
            "fixed-point",
        ],
    },
    "DfT_2024_Climate_Transport_REA.pdf": {
        "method": [
            "rapid evidence assessment",
            "PRISMA",
            "thematic synthesis",
        ],
        "conclusion": [
            "6,600 km",
            "adaptation benefits outweigh",
            "2.2 times",
        ],
        "innovation": [
            "comprehensive",
            "UK government",
            "speed degradation",
        ],
        "limitation": [
            "English language",
            "post-2012",
            "no single database",
        ],
    },
}


def annotate_pdf(filename, passages):
    """Open PDF, search for passages, add colored highlights, save annotated version."""
    input_path = os.path.join(PDF_DIR, filename)
    if not os.path.exists(input_path):
        print(f"  SKIP: {filename} not found")
        return False, {}

    base = os.path.splitext(filename)[0]
    output_path = os.path.join(PDF_DIR, f"{base}_annotated.pdf")

    doc = fitz.open(input_path)
    counts = {k: 0 for k in COLORS}

    for category, search_terms in passages.items():
        color = COLORS[category]
        for term in search_terms:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text_instances = page.search_for(term, quads=False)
                for inst in text_instances:
                    try:
                        highlight = page.add_highlight_annot(inst)
                        highlight.set_colors(stroke=color)
                        highlight.set_info(
                            title=category.upper(),
                            content=f"[{category.upper()}] {term}"
                        )
                        highlight.update()
                        counts[category] += 1
                    except Exception as e:
                        print(f"    WARN: Could not highlight '{term}' on page {page_num+1}: {e}")

    total = sum(counts.values())
    if total > 0:
        doc.save(output_path)
        print(f"  OK: {total} highlights ({counts['method']}M {counts['conclusion']}C {counts['innovation']}I {counts['limitation']}L) -> {os.path.basename(output_path)}")
    else:
        # Save anyway so the link works
        doc.save(output_path)
        print(f"  WARN: 0 highlights found, saved copy as {os.path.basename(output_path)}")

    doc.close()
    return True, counts


def main():
    print(f"PDF Annotation Tool for Literature Review")
    print(f"PDF directory: {PDF_DIR}")
    print(f"PyMuPDF version: {fitz.__version__}")
    print(f"Papers to annotate: {len(ANNOTATIONS)}")
    print("=" * 60)

    success = 0
    total_highlights = {k: 0 for k in COLORS}

    for filename, passages in ANNOTATIONS.items():
        print(f"\n{filename}")
        ok, counts = annotate_pdf(filename, passages)
        if ok:
            success += 1
            for k in counts:
                total_highlights[k] += counts[k]

    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"  PDFs processed: {success}/{len(ANNOTATIONS)}")
    print(f"  Total highlights: {sum(total_highlights.values())}")
    print(f"    Method (blue):     {total_highlights['method']}")
    print(f"    Conclusion (green): {total_highlights['conclusion']}")
    print(f"    Innovation (orange):{total_highlights['innovation']}")
    print(f"    Limitation (red):   {total_highlights['limitation']}")
    print(f"  Output directory: {PDF_DIR}")


if __name__ == "__main__":
    main()
