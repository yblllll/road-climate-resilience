# LR PDF Annotation Platform

Interactive Literature Review platform with 4-color coded PDF annotations, auto-extraction, and 18-agent QA pipeline.

## Quick Start

```bash
git clone https://github.com/yblllll/lr-pdf-annotation-platform.git
cd lr-pdf-annotation-platform
pip install pymupdf
mkdir -p Literature_Review
# Add your PDFs to Literature_Review/
python run.py --extract    # Auto-extract + open platform
```

## Features

- **4-color annotation**: Method (blue), Conclusion (green), Innovation (orange), Limitation (red)
- **Auto-extraction**: Section-by-section reading with ligature handling
- **Interactive PDF Reader**: Continuous scroll, retina DPI, clickable annotation sidebar
- **Literature Dashboard**: Matrix table, citation graph, paper cards, knowledge gaps (7 tabs)
- **QA Pipeline**: 5 agents verify annotation quality (classification, coverage, precision)

## Part of a bigger suite

This is one component of [Academic Research Skills](https://github.com/yblllll/academic-research-skills) — a 12-skill, 18-agent academic research pipeline for Claude Code.

## License

MIT
