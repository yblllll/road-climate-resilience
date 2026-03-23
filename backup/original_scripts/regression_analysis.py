import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch

df = pd.read_csv('link_coefficients_with_features.csv')
df['is_rural'] = df['Road class'].str.contains('Rural all-purpose', na=False).astype(int)

rv = ['Number of lanes','Speed limit (mph)','Average delay (spvpm)','Average daily flow','Length (m)','is_rural']
rd = df[['coefficient']+rv].dropna()

X = sm.add_constant(rd[rv])
y = rd['coefficient']

model_robust = sm.OLS(y, X).fit(cov_type='HC1')
model_ols = sm.OLS(y, X).fit()

print("="*70)
print("MODEL: coefficient ~ lanes + speed_limit + avg_delay + daily_flow + length + rural")
print("(Dropped: Average speed due to multicollinearity with Average delay)")
print("="*70)
print(model_robust.summary())

# Diagnostics
print("\n--- Diagnostics ---")
jb,jp,sk,ku = sm.stats.jarque_bera(model_ols.resid)
print(f"Jarque-Bera: stat={jb:.4f}, p={jp:.6f}")
print(f"Skewness={sk:.4f}, Kurtosis={ku:.4f}")
sw,sp = stats.shapiro(model_ols.resid)
print(f"Shapiro-Wilk: stat={sw:.4f}, p={sp:.6f}")
bp,bpp,_,_ = het_breuschpagan(model_ols.resid, model_ols.model.exog)
print(f"Breusch-Pagan: stat={bp:.4f}, p={bpp:.6f}")
dw = durbin_watson(model_ols.resid)
print(f"Durbin-Watson: {dw:.4f}")

print("\nVIF:")
for i,c in enumerate(X.columns):
    if c=='const': continue
    v = variance_inflation_factor(X.values, i)
    f = ' ⚠️' if v>5 else ''
    print(f"  {c}: {v:.2f}{f}")

inf = model_ols.get_influence()
cd = inf.cooks_distance[0]
print(f"\nOutliers (Cook D>4/n): {(cd>4/len(rd)).sum()}, max={cd.max():.4f}")

# ========== VISUALIZATIONS ==========
fitted = model_ols.fittedvalues
resid = model_ols.resid
std_resid = inf.resid_studentized_internal
leverage = inf.hat_matrix_diag

fig = plt.figure(figsize=(20, 24))
gs = gridspec.GridSpec(4, 3, hspace=0.35, wspace=0.3)

# 1. Residuals vs Fitted
ax1 = fig.add_subplot(gs[0, 0])
ax1.scatter(fitted, resid, alpha=0.5, s=20, c='steelblue', edgecolors='none')
ax1.axhline(y=0, color='red', linestyle='--', linewidth=1)
lowess = sm.nonparametric.lowess(resid, fitted, frac=0.6)
ax1.plot(lowess[:,0], lowess[:,1], 'orange', linewidth=2)
ax1.set_xlabel('Fitted Values')
ax1.set_ylabel('Residuals')
ax1.set_title('(a) Residuals vs Fitted', fontweight='bold')

# 2. Q-Q Plot
ax2 = fig.add_subplot(gs[0, 1])
sm.qqplot(resid, line='45', ax=ax2, markersize=4, color='steelblue')
ax2.set_title('(b) Normal Q-Q Plot', fontweight='bold')

# 3. Scale-Location
ax3 = fig.add_subplot(gs[0, 2])
ax3.scatter(fitted, np.sqrt(np.abs(std_resid)), alpha=0.5, s=20, c='steelblue', edgecolors='none')
lowess2 = sm.nonparametric.lowess(np.sqrt(np.abs(std_resid)), fitted, frac=0.6)
ax3.plot(lowess2[:,0], lowess2[:,1], 'orange', linewidth=2)
ax3.set_xlabel('Fitted Values')
ax3.set_ylabel('√|Standardized Residuals|')
ax3.set_title('(c) Scale-Location', fontweight='bold')

# 4. Cook's Distance
ax4 = fig.add_subplot(gs[1, 0])
ax4.stem(range(len(cd)), cd, linefmt='steelblue', markerfmt=',', basefmt='grey')
ax4.axhline(y=4/len(rd), color='red', linestyle='--', label=f'4/n={4/len(rd):.4f}')
ax4.set_xlabel('Observation Index')
ax4.set_ylabel("Cook's Distance")
ax4.set_title("(d) Cook's Distance", fontweight='bold')
ax4.legend()

# 5. Residuals vs Leverage
ax5 = fig.add_subplot(gs[1, 1])
ax5.scatter(leverage, std_resid, alpha=0.5, s=20, c='steelblue', edgecolors='none')
ax5.axhline(y=0, color='grey', linestyle='--', linewidth=0.8)
ax5.set_xlabel('Leverage')
ax5.set_ylabel('Standardized Residuals')
ax5.set_title('(e) Residuals vs Leverage', fontweight='bold')

# 6. Histogram of Residuals
ax6 = fig.add_subplot(gs[1, 2])
ax6.hist(resid, bins=30, color='steelblue', edgecolor='white', density=True, alpha=0.7)
xmin, xmax = ax6.get_xlim()
x = np.linspace(xmin, xmax, 100)
p = stats.norm.pdf(x, resid.mean(), resid.std())
ax6.plot(x, p, 'red', linewidth=2, label='Normal fit')
ax6.set_xlabel('Residuals')
ax6.set_ylabel('Density')
ax6.set_title('(f) Distribution of Residuals', fontweight='bold')
ax6.legend()

# 7. Coefficient Plot
ax7 = fig.add_subplot(gs[2, :2])
params = model_robust.params.drop('const')
conf = model_robust.conf_int().drop('const')
pvals = model_robust.pvalues.drop('const')

param_names = params.index.tolist()
coefs = params.values
ci_low = conf[0].values
ci_high = conf[1].values
colors = ['green' if p < 0.01 else 'blue' if p < 0.05 else 'orange' if p < 0.1 else 'grey' for p in pvals]

y_pos = range(len(param_names))
ax7.barh(y_pos, coefs, xerr=[coefs-ci_low, ci_high-coefs], color=colors, alpha=0.7, capsize=3)
ax7.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
ax7.set_yticks(list(y_pos))
ax7.set_yticklabels(param_names)
ax7.set_xlabel('Coefficient')
ax7.set_title('(g) Coefficient Plot with 95% CI (Robust SE)', fontweight='bold')
legend_elements = [Patch(facecolor='green', alpha=0.7, label='p<0.01'),
                   Patch(facecolor='blue', alpha=0.7, label='p<0.05'),
                   Patch(facecolor='orange', alpha=0.7, label='p<0.1'),
                   Patch(facecolor='grey', alpha=0.7, label='p≥0.1')]
ax7.legend(handles=legend_elements, loc='lower right')

# 8. Correlation Heatmap
ax8 = fig.add_subplot(gs[2, 2])
corr = rd[rv].corr()
im = ax8.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
ax8.set_xticks(range(len(rv)))
ax8.set_yticks(range(len(rv)))
short_names = ['Lanes','Speed Lim','Avg Delay','Daily Flow','Length','Rural']
ax8.set_xticklabels(short_names, rotation=45, ha='right', fontsize=8)
ax8.set_yticklabels(short_names, fontsize=8)
for i in range(len(rv)):
    for j in range(len(rv)):
        ax8.text(j, i, f'{corr.iloc[i,j]:.2f}', ha='center', va='center', fontsize=7,
                 color='white' if abs(corr.iloc[i,j]) > 0.5 else 'black')
plt.colorbar(im, ax=ax8, shrink=0.8)
ax8.set_title('(h) Correlation Heatmap', fontweight='bold')

# 9-11. Partial Regression Plots (manual implementation to avoid patsy column name issues)
for idx, (var, label) in enumerate([('Number of lanes','i'), ('Average delay (spvpm)','j'), ('Average daily flow','k')]):
    ax = fig.add_subplot(gs[3, idx])
    others = [v for v in rv if v != var]
    # Regress y on others
    X_others = sm.add_constant(rd[others])
    resid_y = sm.OLS(y, X_others).fit().resid
    # Regress var on others
    resid_x = sm.OLS(rd[var], X_others).fit().resid
    ax.scatter(resid_x, resid_y, alpha=0.5, s=20, c='steelblue', edgecolors='none')
    # Fit line
    b = np.polyfit(resid_x, resid_y, 1)
    ax.plot(np.sort(resid_x), np.polyval(b, np.sort(resid_x)), 'red', linewidth=1.5)
    ax.axhline(y=0, color='grey', linestyle='--', linewidth=0.5)
    ax.axvline(x=0, color='grey', linestyle='--', linewidth=0.5)
    ax.set_xlabel(f'e({var} | others)')
    ax.set_ylabel('e(coefficient | others)')
    ax.set_title(f'({label}) Partial Regression: {var}', fontweight='bold')

plt.suptitle('Econometric Diagnostics: Road Climate Resilience Coefficient\n(Model without Average Speed)', 
             fontsize=16, fontweight='bold', y=1.01)
plt.savefig('regression_diagnostics.png', dpi=150, bbox_inches='tight', facecolor='white')
print('\nSaved: regression_diagnostics.png')
