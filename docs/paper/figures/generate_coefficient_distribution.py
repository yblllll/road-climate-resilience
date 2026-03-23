"""
Generate publication-quality figure: distribution of link-level
precipitation sensitivity coefficients from Gamma GLM results.

Total precipitation sensitivity for each link = baseline coefficient
(precipitation_t) + link-specific interaction coefficient (link_*_precip).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import os

# --- Load data (read-only) ---
data_path = (
    "/Users/ybl/Desktop/Postdoc research/DARe's flex fund project/"
    "road-climate-resilience/backup/original_data/gamma_glm_full_results.csv"
)
df = pd.read_csv(data_path)

# --- Extract coefficients ---
baseline_row = df.loc[df["feature"] == "precipitation_t", "coefficient"]
baseline = float(baseline_row.values[0])

interaction_df = df[
    df["feature"].str.startswith("link_") & df["feature"].str.endswith("_precip")
].copy()

total_sensitivity = baseline + interaction_df["coefficient"].values

print(f"Baseline precipitation coefficient: {baseline:.6f}")
print(f"Number of link interaction terms: {len(interaction_df)}")
print(f"Total sensitivity: min={total_sensitivity.min():.4f}, "
      f"max={total_sensitivity.max():.4f}, mean={total_sensitivity.mean():.4f}")

# --- Figure ---
fig, ax = plt.subplots(figsize=(8, 5))

# Histogram
n_bins = 35
counts, bin_edges, patches = ax.hist(
    total_sensitivity,
    bins=n_bins,
    color="#00295e",
    edgecolor="white",
    linewidth=0.5,
    alpha=0.85,
    zorder=2,
    label="Road links",
)

# KDE overlay
kde = gaussian_kde(total_sensitivity, bw_method="scott")
x_kde = np.linspace(total_sensitivity.min() - 0.005, total_sensitivity.max() + 0.005, 300)
y_kde = kde(x_kde)
# Scale KDE to match histogram height
bin_width = bin_edges[1] - bin_edges[0]
y_kde_scaled = y_kde * len(total_sensitivity) * bin_width
ax.plot(x_kde, y_kde_scaled, color="#c1272d", linewidth=1.8, zorder=3, label="KDE")

# Baseline vertical line
ax.axvline(
    baseline,
    color="#c1272d",
    linestyle="--",
    linewidth=1.5,
    zorder=4,
)
# Label the baseline line — place text just above the top of the plot
y_top = ax.get_ylim()[1]
ax.text(
    baseline,
    y_top * 0.95,
    f"  Baseline\n  ({baseline:.4f})",
    color="#c1272d",
    fontsize=8.5,
    fontweight="bold",
    va="top",
    ha="left",
    zorder=5,
)

# Axes labels
ax.set_xlabel("Total precipitation sensitivity coefficient", fontsize=11, labelpad=8)
ax.set_ylabel("Number of road links", fontsize=11, labelpad=8)

# Publication style
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.8)
ax.spines["bottom"].set_linewidth(0.8)
ax.tick_params(axis="both", which="both", direction="out", length=4, width=0.8,
               labelsize=9.5)
ax.set_axisbelow(True)
# No grid

# Clip x-axis to show main distribution clearly (exclude extreme outliers)
q01 = np.percentile(total_sensitivity, 1)
q99 = np.percentile(total_sensitivity, 99)
margin = (q99 - q01) * 0.15
ax.set_xlim(q01 - margin, q99 + margin)

# Add note about outliers
n_outliers = np.sum((total_sensitivity < q01 - margin) | (total_sensitivity > q99 + margin))
if n_outliers > 0:
    ax.text(0.97, 0.85, f"Note: {n_outliers} outlier(s)\nnot shown",
            transform=ax.transAxes, fontsize=7.5, ha="right", va="top",
            color="gray", fontstyle="italic")

# Legend
ax.legend(frameon=False, fontsize=9, loc="upper right")

plt.tight_layout()

# --- Save ---
out_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(out_dir, exist_ok=True)

pdf_path = os.path.join(out_dir, "coefficient_distribution.pdf")
png_path = os.path.join(out_dir, "coefficient_distribution.png")

fig.savefig(pdf_path, dpi=300, bbox_inches="tight", format="pdf")
fig.savefig(png_path, dpi=300, bbox_inches="tight", format="png")
plt.close(fig)

print(f"\nSaved PDF: {pdf_path}")
print(f"Saved PNG: {png_path}")
