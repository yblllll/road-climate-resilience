"""
Step 3: Feature Analysis — What Road Characteristics Explain Climate Sensitivity?
===================================================================================
Regresses link-level precipitation sensitivity coefficients on road features
to identify which physical characteristics make roads more/less resilient.

Model: precipitation_coefficient ~ lanes + speed_limit + avg_delay + daily_flow + length + rural

Input:  link_coefficients_with_features.csv (from Step 02 + road features merge)
Output: - feature_regression_results.csv
        - regression_diagnostics.png

Usage:
    python 03_feature_analysis.py --input <link_coefficients_with_features.csv> --output-dir <output_dir>
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
import argparse
import os


def run_feature_analysis(input_path, output_dir):
    """
    Run OLS regression of precipitation coefficients on road features.

    Parameters
    ----------
    input_path : str
        Path to CSV with columns: coefficient, Number of lanes, Speed limit (mph),
        Average delay (spvpm), Average daily flow, Length (m), Road class
    output_dir : str
        Directory for output files.
    """
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(input_path)

    # Derive rural indicator
    if "Road class" in df.columns:
        df["is_rural"] = df["Road class"].str.contains("Rural all-purpose", na=False).astype(int)
    elif "is_rural" not in df.columns:
        df["is_rural"] = 0

    # Determine coefficient column
    coef_col = "coefficient"
    if coef_col not in df.columns:
        for candidate in ["precipitation_interaction_coefficient", "precipitat"]:
            if candidate in df.columns:
                coef_col = candidate
                break

    feature_vars = ["Number of lanes", "Speed limit (mph)", "Average delay (spvpm)",
                    "Average daily flow", "Length (m)", "is_rural"]

    # Filter to available columns
    available = [v for v in feature_vars if v in df.columns]
    if not available:
        print("ERROR: No road feature columns found. Expected columns:")
        print("  ", feature_vars)
        print("Available columns:", list(df.columns))
        return

    rd = df[[coef_col] + available].dropna()
    print(f"Observations with complete data: {len(rd)}")

    X = sm.add_constant(rd[available])
    y = rd[coef_col]

    # Robust SE model (primary)
    model_robust = sm.OLS(y, X).fit(cov_type="HC1")
    # Standard OLS (for diagnostics)
    model_ols = sm.OLS(y, X).fit()

    print("=" * 70)
    print(f"MODEL: {coef_col} ~ {' + '.join(available)}")
    print("=" * 70)
    print(model_robust.summary())

    # Save results
    results_df = pd.DataFrame({
        "feature": model_robust.params.index,
        "coefficient": model_robust.params.values,
        "std_err": model_robust.bse.values,
        "t_value": model_robust.tvalues.values,
        "p_value": model_robust.pvalues.values,
        "conf_int_lower": model_robust.conf_int()[0].values,
        "conf_int_upper": model_robust.conf_int()[1].values,
    })
    results_path = os.path.join(output_dir, "feature_regression_results.csv")
    results_df.to_csv(results_path, index=False)
    print(f"\nResults saved to {results_path}")

    # Diagnostics
    print("\n--- Diagnostics ---")
    jb, jp, sk, ku = sm.stats.jarque_bera(model_ols.resid)
    print(f"Jarque-Bera: stat={jb:.4f}, p={jp:.6f}")
    print(f"Skewness={sk:.4f}, Kurtosis={ku:.4f}")

    if len(model_ols.resid) >= 3:
        sw, sp = stats.shapiro(model_ols.resid)
        print(f"Shapiro-Wilk: stat={sw:.4f}, p={sp:.6f}")

    bp, bpp, _, _ = het_breuschpagan(model_ols.resid, model_ols.model.exog)
    print(f"Breusch-Pagan: stat={bp:.4f}, p={bpp:.6f}")

    dw = durbin_watson(model_ols.resid)
    print(f"Durbin-Watson: {dw:.4f}")

    print("\nVIF:")
    for i, c in enumerate(X.columns):
        if c == "const":
            continue
        v = variance_inflation_factor(X.values, i)
        flag = " (high)" if v > 5 else ""
        print(f"  {c}: {v:.2f}{flag}")

    # Generate diagnostic plots
    _plot_diagnostics(model_ols, model_robust, rd, available, coef_col, output_dir)

    return model_robust


def _plot_diagnostics(model_ols, model_robust, rd, feature_vars, coef_col, output_dir):
    """Generate diagnostic plots for the feature regression."""
    inf = model_ols.get_influence()
    fitted = model_ols.fittedvalues
    resid = model_ols.resid
    std_resid = inf.resid_studentized_internal
    leverage = inf.hat_matrix_diag
    cd = inf.cooks_distance[0]

    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(2, 3, hspace=0.35, wspace=0.3)

    # 1. Residuals vs Fitted
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.scatter(fitted, resid, alpha=0.5, s=20, c="steelblue", edgecolors="none")
    ax1.axhline(y=0, color="red", linestyle="--", linewidth=1)
    ax1.set_xlabel("Fitted Values")
    ax1.set_ylabel("Residuals")
    ax1.set_title("(a) Residuals vs Fitted", fontweight="bold")

    # 2. Q-Q Plot
    ax2 = fig.add_subplot(gs[0, 1])
    sm.qqplot(resid, line="45", ax=ax2, markersize=4, color="steelblue")
    ax2.set_title("(b) Normal Q-Q Plot", fontweight="bold")

    # 3. Cook's Distance
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.stem(range(len(cd)), cd, linefmt="steelblue", markerfmt=",", basefmt="grey")
    ax3.axhline(y=4 / len(rd), color="red", linestyle="--", label=f"4/n={4/len(rd):.4f}")
    ax3.set_xlabel("Observation Index")
    ax3.set_ylabel("Cook's Distance")
    ax3.set_title("(c) Cook's Distance", fontweight="bold")
    ax3.legend()

    # 4. Coefficient Plot
    ax4 = fig.add_subplot(gs[1, :2])
    params = model_robust.params.drop("const")
    conf = model_robust.conf_int().drop("const")
    pvals = model_robust.pvalues.drop("const")
    coefs = params.values
    ci_low = conf[0].values
    ci_high = conf[1].values
    colors = ["green" if p < 0.01 else "blue" if p < 0.05 else "orange" if p < 0.1 else "grey"
              for p in pvals]
    y_pos = range(len(params))
    ax4.barh(y_pos, coefs, xerr=[coefs - ci_low, ci_high - coefs],
             color=colors, alpha=0.7, capsize=3)
    ax4.axvline(x=0, color="black", linestyle="-", linewidth=0.8)
    ax4.set_yticks(list(y_pos))
    ax4.set_yticklabels(params.index)
    ax4.set_xlabel("Coefficient")
    ax4.set_title("(d) Coefficient Plot with 95% CI (Robust SE)", fontweight="bold")
    legend_elements = [
        Patch(facecolor="green", alpha=0.7, label="p<0.01"),
        Patch(facecolor="blue", alpha=0.7, label="p<0.05"),
        Patch(facecolor="orange", alpha=0.7, label="p<0.1"),
        Patch(facecolor="grey", alpha=0.7, label="p>=0.1"),
    ]
    ax4.legend(handles=legend_elements, loc="lower right")

    # 5. Correlation Heatmap
    ax5 = fig.add_subplot(gs[1, 2])
    corr = rd[feature_vars].corr()
    im = ax5.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    short_names = [v.split("(")[0].strip()[:12] for v in feature_vars]
    ax5.set_xticks(range(len(feature_vars)))
    ax5.set_yticks(range(len(feature_vars)))
    ax5.set_xticklabels(short_names, rotation=45, ha="right", fontsize=8)
    ax5.set_yticklabels(short_names, fontsize=8)
    for i in range(len(feature_vars)):
        for j in range(len(feature_vars)):
            ax5.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7,
                     color="white" if abs(corr.iloc[i, j]) > 0.5 else "black")
    plt.colorbar(im, ax=ax5, shrink=0.8)
    ax5.set_title("(e) Correlation Heatmap", fontweight="bold")

    plt.suptitle("Road Climate Resilience: Feature Regression Diagnostics",
                 fontsize=14, fontweight="bold", y=1.01)

    plot_path = os.path.join(output_dir, "regression_diagnostics.png")
    plt.savefig(plot_path, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"\nDiagnostics plot saved to {plot_path}")
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feature analysis for road climate resilience")
    parser.add_argument("--input", required=True, help="Path to link_coefficients_with_features.csv")
    parser.add_argument("--output-dir", required=True, help="Directory for output files")
    args = parser.parse_args()

    run_feature_analysis(args.input, args.output_dir)
