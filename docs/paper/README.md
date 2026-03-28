# Paper: Precipitation Sensitivity of Road Speeds on the UK SRN

Target journal: **Transportation Research Part D** (IF 8.62, Q1)

## Current Status

- **Draft version**: v4 (revised after simulated peer review)
- **Stage**: Major Revision addressed, re-review passed (Accept conditional on Stata output)
- **Remaining**: Fill [STATA_OUTPUT_NEEDED] placeholders, generate 4 figures, compile final PDF

## Files

| File | Description |
|------|-------------|
| `main_v4_revised.tex` | Current working draft (LaTeX, Elsevier elsarticle class) |
| `references_v2.bib` | Bibliography (38 entries) |
| `main.tex` | Original draft (v1) |
| `references.bib` | Original bibliography (25 entries) |
| `main.pdf` | Last compiled PDF |

## Review Artifacts

| File | Description |
|------|-------------|
| `writing_style_guide_TRD_JTG.md` | TRD/JTG writing style analysis (from 5 LR papers) |
| `paper_audit_report.md` | Initial quality audit of v1 |
| `review_report_stage3.md` | Simulated 5-person peer review (EIC + R1/R2/R3 + Devil's Advocate) |
| `revision_log_v4.md` | Point-by-point revision response |
| `integrity_report_v4.md` | Final integrity verification |
| `ppt_figure_catalog.json` | Available figures from PPT presentations |

## Placeholders to Fill

Before submission, populate these in `main_v4_revised.tex`:

### Stata Output (run GLM and extract)
- Model fit: Deviance, AIC, BIC, Log pseudolikelihood
- Coefficient confidence intervals
- Specification test results (Gamma vs Gaussian vs Inverse Gaussian)
- Volume robustness check coefficients
- Betweenness centrality values (baseline, 90th, 95th, 99th percentile)
- Moran's I spatial autocorrelation test

### Figures (generate or extract from PPTs)
1. **Framework flowchart** — Estimate-Map-Explain methodology diagram
2. **Study area map** — Cambridgeshire SRN with 460 links and weather stations
3. **Spatial coefficient map** — Precipitation sensitivity across the network
4. **Centrality comparison map** — Betweenness centrality under normal vs extreme rainfall

## Compilation

```bash
pdflatex main_v4_revised
bibtex main_v4_revised
pdflatex main_v4_revised
pdflatex main_v4_revised
```

Requires: `elsarticle.cls`, `amsmath`, `booktabs`, `graphicx`, `hyperref`, `lineno`, `siunitx`
