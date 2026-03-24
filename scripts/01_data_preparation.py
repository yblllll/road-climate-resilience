"""
Step 1: Data Preparation for Road Climate Resilience Analysis
=============================================================
Prepares traffic + weather + disruption data for the Gamma GLM.

Input:  Raw merged CSV with columns:
        - Avg mph, Total Volume, time, link name / Road_Name
        - air_temperature, prcp_amt
        - Disruption flags (Accident, MaintenanceWorks, etc.)

Output: Cleaned CSV ready for GLM estimation (Step 02).

Usage:
    python 01_data_preparation.py --input <raw_data.csv> --output <cleaned_data.csv>
"""

import pandas as pd
import numpy as np
import holidays
import argparse
import os
import sys


def is_school_term(dt_series):
    """UK school term approximation based on month/day."""
    md = dt_series.dt.month * 100 + dt_series.dt.day
    autumn = ((md >= 901) & (md <= 1024)) | ((md >= 1103) & (md <= 1219))
    spring = ((md >= 105) & (md <= 213)) | ((md >= 223) & (md <= 327))
    summer = ((md >= 413) & (md <= 522)) | ((md >= 601) & (md <= 720))
    return (autumn | spring | summer).astype("float32")


def is_uni_term(dt_series):
    """Cambridge university term approximation."""
    month = dt_series.dt.month
    day = dt_series.dt.day
    michaelmas = (month == 10) | (month == 11) | ((month == 12) & (day <= 6))
    lent = ((month == 1) & (day >= 17)) | (month == 2) | ((month == 3) & (day <= 16))
    easter = ((month == 4) & (day >= 24)) | (month == 5) | ((month == 6) & (day <= 15))
    return (michaelmas | lent | easter).astype("float32")


def prepare_data(input_path, output_path, speed_col="Avg mph", link_col="link name",
                 time_col="time", temp_col="air_temperature", precip_col="prcp_amt",
                 volume_col="Total Volume", sample_frac=None):
    """
    Clean and prepare data for GLM estimation.

    Parameters
    ----------
    input_path : str
        Path to raw merged CSV.
    output_path : str
        Path to save cleaned CSV.
    speed_col : str
        Column name for average speed.
    link_col : str
        Column name for road link identifier.
    sample_frac : float or None
        If set, randomly sample this fraction of data (for testing).
    """
    # Estimate file size to decide whether to use chunked reading
    file_size_gb = os.path.getsize(input_path) / (1024**3)
    print(f"Reading data from {input_path} ({file_size_gb:.2f} GB)...")

    # Build dtype map using user-specified column names
    dtype_map = {}
    for col in [speed_col, volume_col, temp_col, precip_col]:
        if col:
            dtype_map[col] = "float32"

    if file_size_gb > 1.0:
        # Chunked reading for large files (>1GB) to limit peak memory
        print(f"  Using chunked reading (file > 1GB)...")
        print(f"PROGRESS:2:Reading large file ({file_size_gb:.1f} GB) in chunks — this may take several minutes...", flush=True)
        chunks = []
        chunk_size = 500_000
        total_rows = 0
        # Estimate total rows from file size (rough: ~100 bytes per row for traffic data)
        est_total = int(file_size_gb * 1e9 / 100)
        for i, chunk in enumerate(pd.read_csv(input_path, low_memory=False,
                                               dtype=dtype_map, chunksize=chunk_size)):
            total_rows += len(chunk)
            chunks.append(chunk)
            # Report progress during reading
            read_pct = min(40, int(total_rows / max(est_total, 1) * 40))
            if (i + 1) % 5 == 0:
                print(f"PROGRESS:{2 + read_pct}:Reading... {total_rows:,} rows loaded", flush=True)
        print(f"PROGRESS:42:Concatenating {len(chunks)} chunks...", flush=True)
        data = pd.concat(chunks, ignore_index=True)
        del chunks
        import gc; gc.collect()
    else:
        data = pd.read_csv(input_path, low_memory=False, dtype=dtype_map)

    print(f"PROGRESS:45:Raw data loaded: {len(data):,} rows", flush=True)
    print(f"  Columns: {list(data.columns[:15])}{'...' if len(data.columns) > 15 else ''}")

    # Parse datetime — use user-specified column, with fallbacks
    actual_time_col = time_col
    if time_col not in data.columns:
        for fallback in ["time", "Report Date", "datetime", "timestamp", "date"]:
            if fallback in data.columns:
                actual_time_col = fallback
                break
    data["datetime"] = pd.to_datetime(data[actual_time_col])
    print(f"  Using datetime column: '{actual_time_col}'")

    # Filter: need valid speed, temperature, precipitation
    actual_temp = temp_col if temp_col in data.columns else "air_temperature"
    actual_precip = precip_col if precip_col in data.columns else "prcp_amt"
    mask = (
        data[speed_col].notna()
        & (data[speed_col] > 0)
        & data[actual_precip].notna()
        & data[actual_temp].notna()
    )
    data = data[mask].reset_index(drop=True)
    print(f"  After cleaning: {len(data):,} rows")

    if sample_frac and sample_frac < 1.0:
        data = data.sample(frac=sample_frac, random_state=42).reset_index(drop=True)
        print(f"  After sampling ({sample_frac*100:.0f}%): {len(data):,} rows")

    # Build UK holiday set
    years = data["datetime"].dt.year.unique()
    uk_holidays = holidays.UnitedKingdom(years=years)
    holiday_set = set(uk_holidays.keys())

    # Construct features
    print("Building features...")
    result = pd.DataFrame()
    result["speed"] = data[speed_col].astype("float32")

    # Volume: use user-specified column, fall back to zero if not available
    actual_vol = volume_col if volume_col in data.columns else None
    if actual_vol:
        result["totalvolume"] = data[actual_vol].fillna(0).astype("float32")
    else:
        result["totalvolume"] = pd.Series(0, index=data.index, dtype="float32")
        print("  Note: No volume column found, using 0 (will not affect precipitation estimates)")

    result["link_name"] = data[link_col]
    result["datetime"] = data["datetime"]

    # Calendar controls
    result["schoolterm_t"] = is_school_term(data["datetime"])
    result["universityterm_t"] = is_uni_term(data["datetime"])
    result["bankholiday_t"] = data["datetime"].dt.date.isin(holiday_set).astype("float32")

    # Disruption controls — use whatever columns are available
    event_cols = ["AnimalPresenceObstruction", "AbnormalTraffic", "GeneralObstruction",
                  "EnvironmentalObstruction", "VehicleObstruction"]
    event_found = [c for c in event_cols if c in data.columns]
    if event_found:
        result["event_t"] = data[event_found].fillna(0).max(axis=1).clip(upper=1).astype("float32")
    else:
        result["event_t"] = pd.Series(0, index=data.index, dtype="float32")

    maint_cols = ["MaintenanceWorks", "RoadOrCarriagewayOrLaneManagement"]
    maint_found = [c for c in maint_cols if c in data.columns]
    if maint_found:
        result["roadworks_t"] = data[maint_found].fillna(0).max(axis=1).clip(upper=1).astype("float32")
    else:
        result["roadworks_t"] = pd.Series(0, index=data.index, dtype="float32")

    accident_col_name = "Accident" if "Accident" in data.columns else None
    if accident_col_name:
        result["accident_t"] = data[accident_col_name].fillna(0).astype("float32")
    else:
        result["accident_t"] = pd.Series(0, index=data.index, dtype="float32")

    n_disrupt = sum(1 for x in [event_found, maint_found, [accident_col_name]] if x and x[0])
    if n_disrupt == 0:
        print("  Note: No disruption columns found. Model will estimate without disruption controls.")
    else:
        print(f"  Disruption columns found: events={len(event_found)}, maintenance={len(maint_found)}, accident={'yes' if accident_col_name else 'no'}")

    # Weather
    result["temperature_t"] = data[actual_temp].astype("float32")
    result["precipitation_t"] = data[actual_precip].astype("float32")
    print(f"  Using temperature: '{actual_temp}', precipitation: '{actual_precip}'")

    # Time features
    result["hour"] = data["datetime"].dt.hour
    result["month"] = data["datetime"].dt.month
    result["year"] = data["datetime"].dt.year
    result["dow"] = data["datetime"].dt.dayofweek  # 0=Mon, 6=Sun

    # ---- Filter to weekdays only (matches Stata: day_sat==0 & day_sun==0) ----
    weekday_mask = result["dow"].isin([0, 1, 2, 3, 4])
    n_before = len(result)
    result = result[weekday_mask].reset_index(drop=True)
    print(f"  Weekday filter: {n_before:,} → {len(result):,} rows (removed {n_before - len(result):,} weekend rows)")

    # ---- Construct temp_below0_past6h (matches Stata variable) ----
    # For each observation, check if temperature was below 0 in any of the preceding 6 hours
    print("  Building temp_below0_past6h (rolling 6-hour min temperature)...")
    result = result.sort_values(["link_name", "datetime"]).reset_index(drop=True)
    result["temp_below0_past6h"] = (
        result.groupby("link_name")["temperature_t"]
        .transform(lambda x: (x.rolling(6, min_periods=1).min() < 0).astype("float32"))
    )

    # Save
    result.to_csv(output_path, index=False)
    print(f"Saved prepared data to {output_path} ({len(result):,} rows, {len(result.columns)} cols)")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare data for road climate resilience GLM")
    parser.add_argument("--input", required=True, help="Path to raw merged CSV")
    parser.add_argument("--output", required=True, help="Path to save cleaned CSV")
    parser.add_argument("--speed-col", default="Avg mph", help="Speed column name")
    parser.add_argument("--link-col", default="link name", help="Link identifier column name")
    parser.add_argument("--time-col", default="time", help="Datetime column name")
    parser.add_argument("--temp-col", default="air_temperature", help="Temperature column name")
    parser.add_argument("--precip-col", default="prcp_amt", help="Precipitation column name")
    parser.add_argument("--volume-col", default="Total Volume", help="Volume column name")
    parser.add_argument("--sample", type=float, default=None, help="Sample fraction (e.g., 0.2)")
    args = parser.parse_args()

    prepare_data(args.input, args.output,
                 speed_col=args.speed_col, link_col=args.link_col,
                 time_col=args.time_col, temp_col=args.temp_col,
                 precip_col=args.precip_col, volume_col=args.volume_col,
                 sample_frac=args.sample)
