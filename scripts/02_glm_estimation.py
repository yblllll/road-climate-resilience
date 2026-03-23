"""
Step 2: Gamma GLM Estimation with Link x Precipitation Interactions
====================================================================
Estimates road-link-level climate sensitivity using a Gamma GLM
with log link on travel speed.

Uses sparse matrices for link fixed effects and interaction terms
to handle large datasets (5-6GB, 7M+ rows) without exceeding memory.

Model replicates the Stata specification:
  glm avgmph ... ib146.linkname_num##c.precipitation_t
      if avgmph != . & day_sat == 0 & day_sun == 0,
      family(gamma) link(log) vce(cluster linkname_num)

Input:  Prepared CSV from Step 01 (with weekday-only data).
Output: - gamma_glm_full_results.csv (all coefficients with clustered SEs)
        - precipitation_interaction_results.csv (link-level resilience scores)
        - gamma_glm_summary.txt (model summary)

Usage:
    python 02_glm_estimation.py --input <prepared_data.csv> --output-dir <output_dir>
"""

import pandas as pd
import numpy as np
from scipy import sparse
import argparse
import time
import os
import sys
import gc
from datetime import timedelta


def log_time(msg, start_time):
    elapsed = time.time() - start_time
    print(f"[{timedelta(seconds=int(elapsed))}] {msg}")
    sys.stdout.flush()


def progress(pct, msg=""):
    """Output standardised progress for the Streamlit UI to parse."""
    print(f"PROGRESS:{pct}:{msg}")
    sys.stdout.flush()


def compute_clustered_se(X, y, mu, coef, cluster_ids, family="gamma"):
    """
    Compute cluster-robust (sandwich) standard errors for a GLM.

    Replicates Stata's vce(cluster linkname_num).

    Parameters
    ----------
    X : sparse matrix (n, p)
        Design matrix (including intercept column).
    y : array (n,)
        Response variable.
    mu : array (n,)
        Fitted values (predicted means).
    coef : array (p,)
        Estimated coefficients (including intercept).
    cluster_ids : array (n,)
        Cluster membership (link IDs as integer codes).
    family : str
        GLM family ("gamma").

    Returns
    -------
    se : array (p,)
        Cluster-robust standard errors.
    vcov : array (p, p)
        Cluster-robust variance-covariance matrix.
    """
    n, p = X.shape
    unique_clusters = np.unique(cluster_ids)
    G = len(unique_clusters)

    # For Gamma with log link:
    # Working weight: w_i = mu_i^2 / V(mu_i) = mu_i^2 / mu_i^2 = 1
    # But with log link, d_mu/d_eta = mu_i
    # Score contribution: s_i = (y_i - mu_i) / mu_i * x_i  (for log link Gamma)
    resid_working = (y - mu) / mu  # Pearson residual for Gamma

    # Compute the "bread": (X' W X)^-1
    # For Gamma log-link, W_ii = mu_i^2 / V(mu_i) * (d_mu/d_eta)^-2
    # Simplifies: W_ii = 1 for Gamma log-link (weight = 1)
    # So bread = (X' X)^-1
    # But we need to account for the GLM weights properly:
    # w_i = mu_i^2 / var(y_i) where var(y_i) = phi * mu_i^2 for Gamma
    # So w_i = 1/phi, but phi cancels in sandwich estimator
    # The IRLS weight for Gamma log-link is w_i = 1 (constant)

    # Bread: (X' X)^-1 — since X is sparse, use dense for the p×p result
    XtX = (X.T @ X).toarray()
    try:
        bread = np.linalg.inv(XtX)
    except np.linalg.LinAlgError:
        # Add small ridge for numerical stability
        bread = np.linalg.inv(XtX + 1e-8 * np.eye(p))

    # Compute meat: sum of S_g S_g' over clusters
    # S_g = sum of score contributions within cluster g
    meat = np.zeros((p, p), dtype=np.float64)

    for g in unique_clusters:
        mask = cluster_ids == g
        # Score for observations in this cluster
        X_g = X[mask]  # sparse slice
        r_g = resid_working[mask]
        # S_g = X_g' @ r_g (sum of x_i * resid_i within cluster)
        S_g = X_g.T @ r_g  # (p,) array
        if sparse.issparse(S_g):
            S_g = S_g.toarray().ravel()
        meat += np.outer(S_g, S_g)

    # Finite-sample correction (Stata default): G/(G-1) * (N-1)/(N-p)
    correction = (G / (G - 1)) * ((n - 1) / (n - p))

    # Sandwich: V = bread @ meat @ bread * correction
    vcov = bread @ meat @ bread * correction
    # Clip tiny negative values from numerical imprecision before sqrt
    se = np.sqrt(np.maximum(np.diag(vcov), 0.0))

    return se, vcov


def run_gamma_glm(input_path, output_dir):
    """
    Run Gamma GLM with sparse link x precipitation interactions
    and cluster-robust standard errors.
    """
    os.makedirs(output_dir, exist_ok=True)
    total_start = time.time()

    # ---- Step 1: Load data ----
    progress(5, "Loading data...")
    data = pd.read_csv(input_path, low_memory=False)
    n_rows = len(data)
    n_links = data["link_name"].nunique()
    log_time(f"Loaded {n_rows:,} rows, {n_links} unique links", total_start)

    y = data["speed"].values.astype("float64")

    # Verify weekday-only (should be handled by Step 01, but double-check)
    if "dow" in data.columns:
        weekend_count = (data["dow"] >= 5).sum()
        if weekend_count > 0:
            print(f"  WARNING: {weekend_count:,} weekend rows found — filtering out")
            weekday_mask = data["dow"] < 5
            data = data[weekday_mask].reset_index(drop=True)
            y = data["speed"].values.astype("float64")

    # ---- Step 2: Build dense feature matrix (small: ~40 columns) ----
    progress(15, "Building control variables...")

    # Base controls (matching Stata spec)
    base_cols = ["totalvolume", "schoolterm_t", "universityterm_t", "bankholiday_t",
                 "event_t", "roadworks_t", "accident_t", "temperature_t", "precipitation_t"]
    # Add temp_below0_past6h if available
    if "temp_below0_past6h" in data.columns:
        base_cols.append("temp_below0_past6h")

    base_features = data[base_cols].fillna(0).astype("float64")

    # Day-of-week dummies (Wed = reference, drop Sat/Sun since weekday-only)
    dow_map = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri"}
    dow = data["dow"].map(dow_map)
    dow_dummies = pd.get_dummies(dow, prefix="dow", dtype="float64")
    for col in ["dow_Wed"]:  # Wednesday = reference
        if col in dow_dummies.columns:
            dow_dummies = dow_dummies.drop(col, axis=1)

    # Hour dummies (hour 12 = reference, matching Stata ib12.hour)
    hour_dummies = pd.get_dummies(data["hour"], prefix="hour", dtype="float64")
    if "hour_12" in hour_dummies.columns:
        hour_dummies = hour_dummies.drop("hour_12", axis=1)

    # Month dummies (drop_first)
    month_dummies = pd.get_dummies(data["month"], prefix="month", drop_first=True, dtype="float64")

    # Year dummies (drop_first)
    year_dummies = pd.get_dummies(data["year"], prefix="year", drop_first=True, dtype="float64")

    # Highway dummies (if highway column available)
    highway_dummies = pd.DataFrame()
    if "highway" in data.columns:
        highway_dummies = pd.get_dummies(data["highway"], prefix="highway", drop_first=True, dtype="float64")

    # Combine all dense controls
    X_dense = pd.concat([base_features, dow_dummies, hour_dummies,
                         month_dummies, year_dummies, highway_dummies], axis=1)
    dense_names = list(X_dense.columns)
    log_time(f"Dense controls: {len(dense_names)} features", total_start)

    # ---- Step 3: Build sparse link FEs ----
    progress(30, "Building sparse link fixed effects...")

    link_cat = data["link_name"].astype("category")
    link_codes = link_cat.cat.codes.values
    link_categories = link_cat.cat.categories
    n_samples = len(data)
    n_link_cats = len(link_categories)

    # Sparse link dummy matrix: each row has exactly one 1
    link_sparse = sparse.csr_matrix(
        (np.ones(n_samples, dtype="float64"),
         (np.arange(n_samples), link_codes)),
        shape=(n_samples, n_link_cats)
    )
    link_sparse = link_sparse[:, 1:]  # drop_first (first link = reference)
    link_names = [f"link_{cat}" for cat in link_categories[1:]]

    sparse_mb = (link_sparse.data.nbytes + link_sparse.indices.nbytes + link_sparse.indptr.nbytes) / 1024**2
    log_time(f"Link FEs: {n_link_cats - 1} dummies ({sparse_mb:.1f} MB sparse)", total_start)

    # ---- Step 4: Build sparse interaction terms ----
    progress(45, "Building sparse link x precipitation interactions...")

    precip = data["precipitation_t"].fillna(0).values.astype("float64")
    link_precip_sparse = link_sparse.multiply(precip.reshape(-1, 1))
    link_precip_names = [f"{name}_x_precip" for name in link_names]

    log_time(f"Interaction terms: {len(link_precip_names)} features", total_start)

    # ---- Step 5: Combine into final sparse design matrix ----
    progress(55, "Assembling design matrix...")

    # Add intercept column
    intercept = np.ones((n_samples, 1), dtype="float64")
    X_intercept = sparse.csr_matrix(intercept)

    # Convert dense to sparse and hstack everything
    X_dense_sparse = sparse.csr_matrix(X_dense.values.astype("float64"))
    X_all = sparse.hstack([X_intercept, X_dense_sparse, link_sparse, link_precip_sparse],
                          format="csr")

    feature_names = ["const"] + dense_names + link_names + link_precip_names

    total_mb = (X_all.data.nbytes + X_all.indices.nbytes + X_all.indptr.nbytes) / 1024**2
    log_time(f"Design matrix: {X_all.shape[0]:,} x {X_all.shape[1]:,} ({total_mb:.1f} MB sparse)", total_start)

    # Store cluster IDs before freeing data
    cluster_ids = link_codes.copy()

    # Free memory
    del data, base_features, dow_dummies, hour_dummies, month_dummies, year_dummies
    del highway_dummies, X_dense, X_dense_sparse, link_sparse, link_precip_sparse
    del intercept, X_intercept
    gc.collect()

    # ---- Step 6: Fit Gamma GLM ----
    progress(60, "Fitting Gamma GLM (this may take a while)...")

    try:
        from glum import GeneralizedLinearRegressor
    except ImportError:
        print("ERROR: glum library not installed. Run: pip install glum")
        sys.exit(1)

    model_start = time.time()
    print(f"\n  Fitting: {n_samples:,} observations, {X_all.shape[1]:,} features")
    print(f"  Family: Gamma, Link: log")
    print(f"  Solver: L-BFGS (via glum)")

    model = GeneralizedLinearRegressor(
        family="gamma",
        link="log",
        fit_intercept=False,  # We added intercept manually for easier coefficient extraction
        max_iter=200,
        gradient_tol=1e-8,
        alpha=1e-10,  # Near-zero regularisation → effectively unregularised MLE (like Stata)
        verbose=1,
    )

    model.fit(X_all, y)
    coef = model.coef_.copy()

    model_time = time.time() - model_start
    log_time(f"GLM fitted in {timedelta(seconds=int(model_time))}", total_start)

    # ---- Step 7: Compute fitted values and clustered SEs ----
    progress(80, "Computing cluster-robust standard errors...")

    # Fitted values: mu = exp(X @ beta) for log link
    eta = X_all @ coef
    mu = np.exp(eta)

    print(f"  Computing sandwich estimator with {len(np.unique(cluster_ids))} clusters...")
    se_start = time.time()
    clustered_se, vcov = compute_clustered_se(X_all, y, mu, coef, cluster_ids)
    log_time(f"Clustered SEs computed in {timedelta(seconds=int(time.time() - se_start))}", total_start)

    # z-values and p-values (protect against SE=0)
    from scipy import stats
    with np.errstate(divide="ignore", invalid="ignore"):
        z_values = np.where(clustered_se > 0, coef / clustered_se, 0.0)
        p_values = np.where(clustered_se > 0,
                            2 * (1 - stats.norm.cdf(np.abs(z_values))),
                            1.0)

    # Confidence intervals (95%)
    ci_lower = coef - 1.96 * clustered_se
    ci_upper = coef + 1.96 * clustered_se

    # ---- Step 8: Save results ----
    progress(90, "Saving results...")

    # Full results table
    summary_df = pd.DataFrame({
        "feature": feature_names,
        "coefficient": coef,
        "std_err": clustered_se,
        "z_value": z_values,
        "p_value": p_values,
        "conf_int_lower": ci_lower,
        "conf_int_upper": ci_upper,
    })
    full_path = os.path.join(output_dir, "gamma_glm_full_results.csv")
    summary_df.to_csv(full_path, index=False)
    print(f"  Full results: {full_path}")

    # Extract precipitation interaction terms
    baseline_precip = summary_df.loc[
        summary_df["feature"] == "precipitation_t", "coefficient"
    ].values
    baseline_precip = baseline_precip[0] if len(baseline_precip) > 0 else np.nan

    precip_mask = summary_df["feature"].str.endswith("_x_precip")
    precip_interactions = summary_df[precip_mask]

    interaction_records = []
    for _, row in precip_interactions.iterrows():
        link_name = row["feature"].replace("link_", "").replace("_x_precip", "")
        interaction_records.append({
            "link_name": link_name,
            "precipitation_interaction_coefficient": row["coefficient"],
            "total_precipitation_effect": baseline_precip + row["coefficient"],
            "p_value": row["p_value"],
            "std_err": row["std_err"],
            "significance": (
                "***" if row["p_value"] < 0.001 else
                "**" if row["p_value"] < 0.01 else
                "*" if row["p_value"] < 0.05 else
                "+" if row["p_value"] < 0.1 else ""
            ),
        })

    interaction_df = pd.DataFrame(interaction_records)
    inter_path = os.path.join(output_dir, "precipitation_interaction_results.csv")
    interaction_df.to_csv(inter_path, index=False)
    print(f"  Interaction terms: {inter_path} ({len(interaction_df)} links)")

    # Model summary text
    n_sig = (interaction_df["p_value"] < 0.05).sum()
    summary_text = f"""Road Climate Resilience — Gamma GLM Results
{'='*60}
Observations:        {n_samples:,}
Features:            {X_all.shape[1]:,}
Family:              Gamma (log link)
Standard errors:     Clustered at link level ({len(np.unique(cluster_ids))} clusters)
Estimation time:     {timedelta(seconds=int(model_time))}

Baseline precipitation effect: {baseline_precip:.6f}
Links with significant interaction (p<0.05): {n_sig}/{len(interaction_df)}

Key control variables:
"""
    # Add key non-link coefficients
    for _, row in summary_df.iterrows():
        if not row["feature"].startswith("link_") and row["feature"] != "const":
            sig = "***" if row["p_value"] < 0.001 else "**" if row["p_value"] < 0.01 else "*" if row["p_value"] < 0.05 else ""
            summary_text += f"  {row['feature']:<30} {row['coefficient']:>12.6f}  (SE: {row['std_err']:.6f}) {sig}\n"

    summary_path = os.path.join(output_dir, "gamma_glm_summary.txt")
    with open(summary_path, "w") as f:
        f.write(summary_text)
    print(f"  Summary: {summary_path}")

    # Save model statistics as JSON (for dashboard display)
    import json as _json
    # Compute model fit statistics
    # Deviance for Gamma: 2 * sum( (y - mu)/mu - log(y/mu) )
    deviance = 2 * np.sum((y - mu) / mu - np.log(y / mu))
    pearson_chi2 = np.sum(((y - mu) / mu) ** 2)
    n_params = X_all.shape[1]
    df_resid = n_samples - n_params
    # AIC = -2*ll + 2*k (approximate via deviance)
    ll_approx = -0.5 * n_samples * (1 + np.log(2 * np.pi * deviance / n_samples))
    aic_approx = -2 * ll_approx + 2 * n_params
    bic_approx = -2 * ll_approx + np.log(n_samples) * n_params

    model_stats = {
        "family": "Gamma",
        "link": "Log",
        "standard_errors": f"Clustered ({len(np.unique(cluster_ids))} clusters)",
        "sample_restriction": "Weekdays only (Mon-Fri)",
        "n_obs": int(n_samples),
        "n_clusters": int(len(np.unique(cluster_ids))),
        "n_parameters": int(n_params),
        "deviance": round(float(deviance), 4),
        "pearson_chi2": round(float(pearson_chi2), 4),
        "aic": round(float(aic_approx), 4),
        "bic": round(float(bic_approx), 4),
        "log_likelihood": round(float(ll_approx), 4),
        "df_model": int(n_params - 1),
        "df_residual": int(df_resid),
        "deviance_per_df": round(float(deviance / df_resid), 6),
        "pearson_per_df": round(float(pearson_chi2 / df_resid), 6),
    }
    stats_path = os.path.join(output_dir, "model_summary.json")
    with open(stats_path, "w") as f:
        _json.dump(model_stats, f, indent=2)
    print(f"  Model stats: {stats_path}")

    progress(100, "Complete!")
    log_time("All done!", total_start)

    return summary_df, interaction_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Gamma GLM for road climate resilience")
    parser.add_argument("--input", required=True, help="Path to prepared data CSV")
    parser.add_argument("--output-dir", required=True, help="Directory for results")
    args = parser.parse_args()

    run_gamma_glm(args.input, args.output_dir)
