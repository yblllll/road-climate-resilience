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
                 sample_frac=None):
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

    dtype_map = {speed_col: "float32", "Total Volume": "float32",
                 "air_temperature": "float32", "prcp_amt": "float32"}

    if file_size_gb > 1.0:
        # Chunked reading for large files (>1GB) to limit peak memory
        print(f"  Using chunked reading (file > 1GB)...")
        chunks = []
        chunk_size = 500_000
        total_rows = 0
        for i, chunk in enumerate(pd.read_csv(input_path, low_memory=False,
                                               dtype=dtype_map, chunksize=chunk_size)):
            total_rows += len(chunk)
            chunks.append(chunk)
            if (i + 1) % 10 == 0:
                print(f"    Read {total_rows:,} rows...")
        data = pd.concat(chunks, ignore_index=True)
        del chunks
        import gc; gc.collect()
    else:
        data = pd.read_csv(input_path, low_memory=False, dtype=dtype_map)

    print(f"  Raw data: {len(data):,} rows")

    # Parse datetime
    time_col = "time" if "time" in data.columns else "Report Date"
    data["datetime"] = pd.to_datetime(data[time_col])

    # Filter: need valid speed, temperature, precipitation
    mask = (
        data[speed_col].notna()
        & (data[speed_col] > 0)
        & data["prcp_amt"].notna()
        & data["air_temperature"].notna()
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
    result["totalvolume"] = data.get("Total Volume", pd.Series(dtype="float32")).astype("float32")
    result["link_name"] = data[link_col]
    result["datetime"] = data["datetime"]

    # Calendar controls
    result["schoolterm_t"] = is_school_term(data["datetime"])
    result["universityterm_t"] = is_uni_term(data["datetime"])
    result["bankholiday_t"] = data["datetime"].dt.date.isin(holiday_set).astype("float32")

    # Disruption controls
    result["event_t"] = (
        (data.get("AnimalPresenceObstruction", pd.Series(0)).fillna(0) > 0)
        | (data.get("AbnormalTraffic", pd.Series(0)).fillna(0) > 0)
        | (data.get("GeneralObstruction", pd.Series(0)).fillna(0) > 0)
        | (data.get("EnvironmentalObstruction", pd.Series(0)).fillna(0) > 0)
        | (data.get("VehicleObstruction", pd.Series(0)).fillna(0) > 0)
    ).astype("float32")
    result["roadworks_t"] = (
        (data.get("MaintenanceWorks", pd.Series(0)).fillna(0) > 0)
        | (data.get("RoadOrCarriagewayOrLaneManagement", pd.Series(0)).fillna(0) > 0)
    ).astype("float32")
    result["accident_t"] = data.get("Accident", pd.Series(0)).fillna(0).astype("float32")

    # Weather
    result["temperature_t"] = data["air_temperature"].astype("float32")
    result["precipitation_t"] = data["prcp_amt"].astype("float32")

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
    parser.add_argument("--sample", type=float, default=None, help="Sample fraction (e.g., 0.2)")
    args = parser.parse_args()

    prepare_data(args.input, args.output, args.speed_col, args.link_col, args.sample)
