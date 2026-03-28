# Road Climate Resilience Framework

A lightweight, open-data analytical framework for assessing road-level climate sensitivity on strategic road networks. Developed as part of the DARe Flex Fund Project.

## Overview

This framework quantifies how precipitation and temperature affect travel speeds at the road-link level, maps the results interactively, and explains the variation using road characteristics.

**Framework: Estimate → Map → Explain**

1. **Estimate** — Gamma GLM with link × precipitation interactions on hourly travel speed data
2. **Map** — Interactive web map showing link-level climate sensitivity scores
3. **Explain** — OLS regression linking sensitivity to road features (lanes, speed limit, road class, etc.)

## Quick Start

### View the Cambridgeshire Example

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the interactive platform
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

### Run Your Own Analysis

```bash
# Step 1: Prepare your traffic + weather data
python scripts/01_data_preparation.py \
    --input your_data.csv \
    --output prepared_data.csv \
    --speed-col "Avg mph" \
    --link-col "link name"

# Step 2: Estimate the Gamma GLM
python scripts/02_glm_estimation.py \
    --input prepared_data.csv \
    --output-dir results/

# Step 3: Analyse road features (after merging coefficients with road features)
python scripts/03_feature_analysis.py \
    --input results/link_coefficients_with_features.csv \
    --output-dir results/
```

## Data Requirements

Your input CSV needs these columns:

| Column | Description | Typical Source |
|--------|-------------|----------------|
| `time` | Datetime (hourly) | Traffic sensors |
| `Avg mph` | Average travel speed | WebTRIS / MIDAS |
| `Total Volume` | Vehicle count | Traffic sensors |
| `link name` | Road link identifier | Your network definition |
| `air_temperature` | Temperature (°C) | Met Office / CEDA |
| `prcp_amt` | Precipitation (mm) | Met Office / CEDA |
| `Accident` | Binary disruption flag | National Highways |
| `MaintenanceWorks` | Binary disruption flag | National Highways |

Optional: `AbnormalTraffic`, `GeneralObstruction`, `EnvironmentalObstruction`, `VehicleObstruction`, `AnimalPresenceObstruction`, `RoadOrCarriagewayOrLaneManagement`

## Methodology

### Stage 1: Gamma GLM

The model estimates **weekday** travel speed as:

```
log(speed) = β₀ + β_vol·volume + Σ βₜ·time_controls + β_precip·precipitation
             + β_temp·temperature + β_cold·temp_below0_past6h
             + Σ γᵢ·link_i + Σ δᵢ·(link_i × precipitation) + ε
```

- **Sample**: Weekdays only (Monday–Friday). Weekend traffic patterns differ substantially and are excluded to avoid confounding climate sensitivity estimates.
- **Standard errors**: Clustered at the road-link level.
- **Time controls**: Hour (ref: 12), month, year, day-of-week (ref: Wednesday).
- **Calendar controls**: School term, university term, bank holidays.
- **Disruption controls**: Events, roadworks, accidents.

Where `δᵢ` captures how each road link's speed responds differently to precipitation relative to the baseline.

### Stage 2: Feature Analysis

Link-level precipitation coefficients (`β_precip + δᵢ`) are regressed on road features:

```
total_precip_effect_i = α + β₁·lanes + β₂·speed_limit + β₃·delay
                        + β₄·daily_flow + β₅·length + β₆·rural + ε
```

## Key Advantages

- **Lightweight**: Runs on a standard laptop — no microsimulation or HPC needed
- **Open data**: Uses publicly available traffic, weather, and road feature data
- **Transferable**: Any local authority can apply this to their own strategic road network
- **Interpretable**: Coefficients map directly to planning-relevant quantities

## Academic Dashboard

An interactive research management platform for the project's literature review, journal analysis, and paper writing workflow.

```bash
cd docs/academic-dashboard
python3 run.py
```

Opens at `http://localhost:8765/literature_viewer.html` with 10 interactive tabs:

| Tab | Function |
|-----|----------|
| Overview | Paper counts, themes, method distribution |
| Matrix Table | Sortable/filterable literature table |
| Citation Graph | D3 force-directed citation network |
| Citation Chain | Chronological knowledge flow |
| Paper Cards | Expandable 4-color annotated cards |
| Knowledge Gaps | Research gap identification |
| PDF Reader | Full-text reader with annotation sidebar |
| Research Pipeline | 9-stage workflow tracker |
| Journal Rankings | 32 transport journals with IF/tier/relevance |
| Paper | LaTeX editor with live preview and AI assistant |

See [`docs/academic-dashboard/README.md`](docs/academic-dashboard/README.md) for details.

## Paper

Target journal: **Transportation Research Part D** (IF 8.62, Q1)

Current status: v4 revised draft, peer review passed (Accept conditional on Stata output).

See [`docs/paper/README.md`](docs/paper/README.md) for the full paper pipeline documentation.

## Project Structure

```
road-climate-resilience/
├── app.py                      # Streamlit interactive map platform
├── requirements.txt            # Python dependencies
├── README.md
├── data/
│   └── example/                # Cambridgeshire demonstration data
├── scripts/
│   ├── 01_data_preparation.py  # Clean & merge input data
│   ├── 02_glm_estimation.py    # Gamma GLM with interactions
│   └── 03_feature_analysis.py  # Road features regression
├── docs/
│   ├── academic-dashboard/     # Academic Dashboard (10-tab HTML platform)
│   │   ├── literature_viewer.html
│   │   ├── literature_reader.html
│   │   ├── annotation_data_final.json
│   │   ├── d3.v7.min.js
│   │   └── run.py
│   ├── paper/                  # Paper manuscript and review artifacts
│   │   ├── main_v4_revised.tex
│   │   ├── references_v2.bib
│   │   ├── Literature_Review/  # Source PDFs (not tracked)
│   │   └── *.md                # Review/audit reports
│   └── user_guide.md           # Detailed usage guide
├── uploads/                    # User-uploaded data (gitignored)
└── backup/                     # Original analysis files
```

## Citation

> [Paper reference to be added upon publication]

## License

This project is open source. See LICENSE file for details.

## Acknowledgements

Developed as part of the DARe (Digital Architecture for Resilience) Flex Fund Project, University of Cambridge, Department of Land Economy.
