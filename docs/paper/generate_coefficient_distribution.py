"""
Generate publication-quality histogram of link-level precipitation sensitivity coefficients.

Usage:
    python generate_coefficient_distribution.py

Output:
    figures/coefficient_distribution.pdf
    figures/coefficient_distribution.png
"""

import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(SCRIPT_DIR)),
    'backup', 'original_data', 'gamma_glm_full_results.csv'
)
OUT_DIR = os.path.join(SCRIPT_DIR, 'figures')
os.makedirs(OUT_DIR, exist_ok=True)

# Read data
df = pd.read_csv(DATA_PATH)

# Extract link precipitation interaction terms
link_precip = df[df['feature'].str.match(r'link_\d+_precip', na=False)].copy()
interaction_coeffs = link_precip['coefficient'].values

# Baseline precipitation coefficient
BASELINE = -0.020943981885684877

# Total sensitivity = baseline + interaction
total_sensitivity = BASELINE + interaction_coeffs

print(f'Number of links: {len(total_sensitivity)}')
print(f'Range: [{total_sensitivity.min():.4f}, {total_sensitivity.max():.4f}]')
print(f'Mean total sensitivity: {total_sensitivity.mean():.4f}')
print(f'Median total sensitivity: {np.median(total_sensitivity):.4f}')
print(f'Links more sensitive than baseline (interaction < 0): '
      f'{(interaction_coeffs < 0).sum()}')
print(f'Links with positive total sensitivity (speed increases with rain): '
      f'{(total_sensitivity > 0).sum()}')

# ── APA 7.0 style configuration ──────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
})

fig, ax = plt.subplots(figsize=(8, 5))

# ── Histogram ─────────────────────────────────────────────────────────────────
NAVY = '#00295e'
n, bins, patches = ax.hist(
    total_sensitivity, bins=30,
    color=NAVY, edgecolor='white', linewidth=0.5, alpha=0.9, zorder=3
)

# ── Reference lines ──────────────────────────────────────────────────────────
ax.axvline(
    x=BASELINE, color='#c0392b', linestyle='--', linewidth=1.5, zorder=4,
    label=f'Network baseline ({BASELINE:.4f})'
)
ax.axvline(x=0, color='grey', linestyle=':', linewidth=1.0, alpha=0.6, zorder=2)

# ── Axis labels ───────────────────────────────────────────────────────────────
ax.set_xlabel('Total Precipitation Sensitivity Coefficient', fontsize=11, labelpad=8)
ax.set_ylabel('Number of Links', fontsize=11, labelpad=8)

# ── Resilience annotations with arrows ────────────────────────────────────────
y_max = n.max()
x_range = total_sensitivity.max() - total_sensitivity.min()

# "More resilient" on the right
ax.annotate(
    'More resilient',
    xy=(total_sensitivity.max() - 0.12 * x_range, y_max * 0.92),
    fontsize=10, fontstyle='italic', color='#2d6a4f', ha='center', fontweight='bold'
)
ax.annotate(
    '', xy=(total_sensitivity.max() - 0.02 * x_range, y_max * 0.85),
    xytext=(total_sensitivity.max() - 0.22 * x_range, y_max * 0.85),
    arrowprops=dict(arrowstyle='->', color='#2d6a4f', lw=1.5)
)

# "Less resilient" on the left
ax.annotate(
    'Less resilient',
    xy=(total_sensitivity.min() + 0.12 * x_range, y_max * 0.92),
    fontsize=10, fontstyle='italic', color='#c0392b', ha='center', fontweight='bold'
)
ax.annotate(
    '', xy=(total_sensitivity.min() + 0.02 * x_range, y_max * 0.85),
    xytext=(total_sensitivity.min() + 0.22 * x_range, y_max * 0.85),
    arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.5)
)

# ── Legend ────────────────────────────────────────────────────────────────────
ax.legend(loc='upper right', frameon=False, fontsize=10)

# ── APA style: remove top and right spines ────────────────────────────────────
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# ── Save ──────────────────────────────────────────────────────────────────────
fig.tight_layout(pad=1.5)

pdf_path = os.path.join(OUT_DIR, 'coefficient_distribution.pdf')
png_path = os.path.join(OUT_DIR, 'coefficient_distribution.png')

fig.savefig(pdf_path, dpi=300, bbox_inches='tight')
fig.savefig(png_path, dpi=300, bbox_inches='tight')
plt.close()

print(f'\nFigures saved:')
print(f'  PDF: {pdf_path}')
print(f'  PNG: {png_path}')
