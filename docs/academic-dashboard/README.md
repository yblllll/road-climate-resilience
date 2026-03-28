# Academic Dashboard

Interactive research management platform with 10 tabs for literature review, journal analysis, research pipeline tracking, and paper editing.

## Quick Start

```bash
cd docs/academic-dashboard
python3 run.py
```

Opens at `http://localhost:8765/literature_viewer.html`

## 10 Tabs

| Tab | Function |
|-----|----------|
| **Overview** | Paper counts, year distribution, theme breakdown, method distribution |
| **Matrix Table** | Sortable/filterable table — authors, year, journal, method, IF, citations |
| **Citation Graph** | D3 force-directed network — nodes sized by citations, colored by theme |
| **Citation Chain** | Chronological knowledge flow from foundational works to your contribution |
| **Paper Cards** | Expandable cards with 4-color aspect badges (Method/Conclusion/Innovation/Limitation) |
| **Knowledge Gaps** | Theme coverage heatmap and identified research gaps |
| **PDF Reader** | Full-text reader with 4-color annotation sidebar — click annotation to jump to page |
| **Research Pipeline** | 9-stage workflow tracker with status (completed/in-progress/pending) |
| **Journal Rankings** | 32 transport journals — IF, tier, ABS/ABDC rating, relevance, target marking |
| **Paper** | LaTeX editor + live preview + margin notes + AI writing assistant |

## PDF Annotation Color Code

| Color | Category |
|-------|----------|
| Blue | **Method** — how the study was conducted |
| Green | **Conclusion** — key findings and results |
| Orange | **Innovation** — novel contributions |
| Red | **Limitation** — acknowledged weaknesses |

## Files

- `literature_viewer.html` — Main dashboard (all 10 tabs, single-file)
- `literature_reader.html` — PDF reader (embedded via iframe in PDF Reader tab)
- `annotation_data_final.json` — Annotation data for 21+ papers
- `d3.v7.min.js` — D3.js library for citation graph
- `run.py` — One-command launcher

## Notes

- PDFs should be in `../paper/Literature_Review/` relative to this directory
- The platform runs entirely client-side (no server-side processing)
- All annotation data is embedded in the HTML for portability
