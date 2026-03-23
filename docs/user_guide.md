# User Guide: Road Climate Resilience Framework

## For Local Authority Users

This guide explains how to apply the Road Climate Resilience Framework to your own strategic road network.

## Step 1: Gather Your Data

You need four types of data, all available from open or semi-open sources:

### Traffic Data (hourly)
- **Source**: WebTRIS (National Highways) or local traffic sensors
- **Required fields**: datetime, average speed (mph), vehicle count, road link identifier
- **Coverage**: At least 1 year of hourly data recommended

### Weather Data (hourly)
- **Source**: CEDA / Met Office MIDAS (free registration required at ceda.ac.uk)
- **Required fields**: air temperature (°C), precipitation amount (mm)
- **Note**: Match to the nearest weather station for each traffic sensor

### Disruption Data
- **Source**: National Highways API or local records
- **Required fields**: Binary flags for accidents, maintenance works, obstructions
- **If unavailable**: Set all disruption columns to 0 (model will still work, but cannot control for disruptions)

### Road Features (for Stage 3)
- **Source**: DfT Road Condition and Maintenance Statistics
- **Required fields**: Number of lanes, speed limit, road class, average daily flow, link length

## Step 2: Merge and Prepare

Merge all data sources into a single CSV at the hourly level, with one row per road link per hour.

```bash
python scripts/01_data_preparation.py \
    --input your_merged_data.csv \
    --output prepared_data.csv \
    --speed-col "Avg mph" \
    --link-col "link name"
```

**Column name mapping**: If your columns have different names, use the `--speed-col` and `--link-col` flags. The script will auto-detect common variants for other columns.

## Step 3: Run the GLM

```bash
python scripts/02_glm_estimation.py \
    --input prepared_data.csv \
    --output-dir results/
```

**For large datasets**: Use `--sample 0.2` to test on 20% of data first. The full model on 7M+ rows takes approximately 10-30 minutes depending on hardware.

**Outputs**:
- `gamma_glm_full_results.csv` — all model coefficients with standard errors and p-values
- `precipitation_interaction_results.csv` — link-level precipitation sensitivity scores
- `gamma_glm_summary.txt` — full model summary

## Step 4: Interpret Results

Each road link gets a **total precipitation effect**:

```
total_effect_i = baseline_precipitation_coefficient + link_i_interaction_term
```

- **More negative** = speed drops more when it rains → less resilient
- **Less negative / closer to zero** = speed is more stable → more resilient
- **Positive** (rare) = speed actually increases slightly in rain (possible if rain reduces congestion through demand reduction)

## Step 5: Visualise

Launch the interactive platform to view your results on a map:

```bash
streamlit run app.py
```

Navigate to "Run Your Own Analysis" to upload your results CSV.

## Step 6: Feature Analysis (Optional)

To understand *why* some links are more resilient, merge the precipitation coefficients with road features and run:

```bash
python scripts/03_feature_analysis.py \
    --input link_coefficients_with_features.csv \
    --output-dir results/
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Model won't converge | Try a larger sample (`--sample 0.5`) or check for extreme outliers in speed data |
| Missing weather data | Ensure weather station matching covers your study period; interpolate gaps if < 5% missing |
| Too few link interactions | Need at least 500 observations per link for reliable interaction estimates |
| Memory error | Use `--sample 0.1` first, then increase; consider running on a machine with 16GB+ RAM for full datasets |
