---
name: lr-pdf-annotation-platform
description: |
  Generate an interactive Literature Review PDF annotation platform with 4-color coded
  highlights (Method=blue, Conclusion=green, Innovation=orange, Limitation=red) embedded
  in both the PDF files and an HTML reader with right-sidebar navigation. Use when:
  (1) completing a literature review and needing a persistent, visual summary platform,
  (2) user asks to annotate/highlight academic papers by category,
  (3) user wants a PDF reader with clickable annotation sidebar,
  (4) building an LR platform as part of the academic research pipeline.
  This skill is part of the literature-analyzer → lr-pdf-annotation-platform pipeline.
  Each research project gets its own saved platform instance.
author: Claude Code (extracted from DARe project session)
version: 1.0.0
date: 2026-03-26
tags: [literature-review, pdf-annotation, academic, research-platform]
---

# Literature Review PDF Annotation Platform

## Problem
After reading 10-30+ academic papers for a literature review, researchers need a way to:
- Visually see which parts of each paper contain method/conclusion/innovation/limitation
- Navigate directly to relevant passages from a summary sidebar
- Have persistent, color-coded highlights in the actual PDF files
- Access everything from a single integrated platform (not separate files)

## Context / Trigger Conditions
- User has completed reading papers for a literature review
- User wants to generate an LR annotation platform
- User says "annotate papers", "highlight papers", "LR platform", "literature reader"
- After `literature-analyzer` skill has been used to build the matrix/dashboard
- As the final step of a `deep-research` lit-review mode

## Critical Rules (Learned from User Feedback)

### Rule 1: Annotations Must Come from FULL TEXT, Not Just Abstract
**NEVER** use short generic keywords as search phrases. They match in the abstract and
create misleading highlights all on page 1.

**BAD** (matches abstract):
```json
{"text": "rainfall", "page": 1}
{"text": "percolation theory", "page": 1}
{"text": "resilience", "page": 1}
```

**GOOD** (matches specific sections):
```json
{"text": "this study adopts a generalised linear model using Gamma", "page": 13}
{"text": "ratio between the residual deviance (2,545,314) and the degrees of freedom", "page": 13}
{"text": "reallocation of road space for public and active modes", "page": 26}
```

**Each category MUST have original_texts from DIFFERENT sections:**
- Method → from Methodology/Data section (typically pages 5-15)
- Conclusion → from Results/Discussion section (typically pages 15-25)
- Innovation → from Introduction or Discussion (where novelty is claimed)
- Limitation → from Limitations/Discussion section (near the end)

### Rule 2: Use Long, Unique Sentence Fragments (15-40 words)
Search phrases must be long enough to match ONLY in the intended location:
- Minimum 15 words for any search phrase
- Include specific numbers, variable names, or technical terms
- Verify with `page.search_for()` that it matches exactly 1 location

### Rule 3: Verify Every Phrase with PyMuPDF search_for()
Before saving annotation data, verify every phrase:
```python
rects = doc[page_num].search_for(phrase)
if not rects:
    # Try shorter version, or extract actual text from PDF
    actual_text = doc[page_num].get_text()
    # Find the correct passage in actual_text
```

### Rule 4: Handle PDF Text Encoding Issues
PDFs often have encoding quirks:
- `fi` ligature renders as single character (so "traffic" may be "traFic")
- Line breaks within sentences (Gamma\ndistribution)
- Different quote characters (' vs ')
- Em-dash vs hyphen

Always extract actual text from PDF first, then use that as the search phrase.

### Rule 5: PDF Rendering Must Use devicePixelRatio
For retina/HiDPI displays:
```javascript
const dpr = window.devicePixelRatio || 1;
canvas.width = viewport.width * dpr;
canvas.height = viewport.height * dpr;
canvas.style.width = viewport.width + 'px';
canvas.style.height = viewport.height + 'px';
ctx.scale(dpr, dpr);
```

### Rule 6: PyMuPDF save() Needs Proper Parameters
```python
doc.save(output_path, garbage=4, deflate=True)  # NOT just doc.save(output_path)
```
Without `garbage=4, deflate=True`, highlights may not persist.

### Rule 7: Platform Must Be Integrated, Not Standalone
The PDF reader is a TAB within the main LR platform (literature_viewer.html),
NOT a separate HTML file. The platform has these tabs:
1. Overview (stats)
2. Matrix Table
3. Citation Graph
4. Citation Chain
5. Paper Cards
6. Knowledge Gaps
7. **PDF Reader** (with annotation sidebar)

### Rule 8: Each Project Gets Its Own Persistent Platform
Save the platform data per research project:
```
project_root/docs/paper/
├── literature_viewer.html      # Main platform (self-contained)
├── annotation_data_final.json  # Verified annotations
├── Literature_Review/          # Original PDFs
│   ├── Paper1.pdf
│   ├── Paper1_annotated.pdf    # With highlights
│   └── ...
```

## Data Format

### Annotation Data Structure
```json
{
  "Filename.pdf": {
    "method": [
      {
        "note": "Summary of what this method passage tells us and why it matters",
        "original_texts": [
          {"text": "exact sentence fragment from methodology section", "page": 8},
          {"text": "another relevant passage about the method", "page": 9}
        ]
      }
    ],
    "conclusion": [...],
    "innovation": [...],
    "limitation": [...]
  }
}
```

### Color Scheme (PyMuPDF RGB tuples)
```python
COLORS = {
    "method":     (0.204, 0.596, 0.859),  # Blue
    "conclusion": (0.298, 0.686, 0.314),   # Green
    "innovation": (0.953, 0.612, 0.071),   # Orange
    "limitation": (0.906, 0.298, 0.235),   # Red
}
```

## Workflow

### Step 1: Deep Read Each Paper
For each PDF, extract ALL text from ALL pages using PyMuPDF:
```python
doc = fitz.open(path)
for i in range(len(doc)):
    text = doc[i].get_text()
    # Read methodology, results, discussion, limitations sections
```

### Step 2: Identify Key Passages Per Category
For each paper, find 2-4 passages per category from DIFFERENT sections:
- Method: exact model specification, data sources, sample size
- Conclusion: key quantitative findings with numbers
- Innovation: explicit novelty claims ("first to...", "novel approach...")
- Limitation: acknowledged weaknesses, geographic/temporal constraints

### Step 3: Verify All Phrases
```python
for phrase in all_phrases:
    found = False
    for page_num in range(len(doc)):
        if doc[page_num].search_for(phrase):
            found = True
            verified_page = page_num + 1
            break
    if not found:
        # Extract actual text and find a better phrase
```

### Step 4: Generate Annotated PDFs
```python
for rect in page.search_for(phrase):
    hl = page.add_highlight_annot(rect)
    hl.set_colors(stroke=color)
    hl.set_info(title=label, content=note)
    hl.update()
doc.save(output_path, garbage=4, deflate=True)
```

### Step 5: Build/Update Platform HTML
Embed annotation data as JSON in the HTML. The reader sidebar shows:
- Category headers (collapsible)
- Summary note (clickable → jumps to first page)
- "ORIGINAL TEXT:" label
- Numbered list of original passages (each clickable → jumps to its page)

### Step 6: QA Audit with oh-my-claudecode Agents

After generating annotations, run quality audit using oh-my-claudecode's agents.
These are GENERAL-PURPOSE agents that work well for academic annotation review
because their framework (evidence-based verification, multi-perspective analysis,
gap detection) naturally applies to literature review quality.

**Agent 1: `critic` (Opus model)**
- Spawn as Agent with subagent_type from oh-my-claudecode
- Task: "Review the annotation quality for [paper]. Read the full PDF and compare
  against annotation_data_final.json. Check: (1) Are all key method/result/limitation
  sentences from the paper captured? (2) Is each annotation in the correct category?
  (3) What important content is MISSING from the annotations?"
- Critic's multi-perspective protocol naturally checks from statistician/domain-expert/
  methodologist angles
- Critic's gap analysis ("What's Missing") catches under-annotated sections
- Output: VERDICT (REJECT/REVISE/ACCEPT) with specific findings

**Agent 2: `verifier`**
- Task: "Verify all annotation phrases for [paper] exist in the PDF using
  fitz search_for(). Check page numbers. Flag duplicates and too-short phrases."
- Verifier's evidence-based approach ensures every phrase is actually findable
- Output: verification report with PASS/FAIL per paper

**QA Pipeline:**
```
Step 5 output (annotations)
  → critic reviews each paper for content quality
  → verifier checks phrase existence + page accuracy
  → Fix any REJECT/FAIL issues
  → Re-run until all ACCEPT/PASS
```

**When to use QA:**
- ALWAYS run on the first 2-3 papers as a calibration check
- Run on any paper with fewer than 3 annotations in any category
- Run on any paper where annotations are concentrated on pages 1-2 (abstract-only)

## Verification Checklist
- [ ] Each paper has annotations in ALL 4 categories
- [ ] Method annotations come from methodology section (not abstract)
- [ ] Conclusion annotations come from results/discussion (not abstract)
- [ ] Innovation annotations come from introduction or discussion
- [ ] Limitation annotations come from limitations section (not policy recommendations)
- [ ] All phrases verified with search_for()
- [ ] No policy implications misclassified as limitations
- [ ] Annotations span at least 3 different pages per paper
- [ ] PDF renders at high DPI on retina displays
- [ ] Clicking sidebar items scrolls to correct page
- [ ] Platform is integrated as a tab, not standalone
- [ ] critic agent verdict: ACCEPT for all papers
- [ ] verifier agent: PASS for all papers

## Notes
- This skill works in conjunction with `literature-analyzer` (matrix/dashboard)
  and `academic-literature` (paper download)
- The full pipeline is: download → read → annotate → QA audit → platform
- Batch processing with parallel agents (3-4 papers per agent) is efficient
- Total annotation count of 150-400 across 20 papers is typical
- oh-my-claudecode's `critic` and `verifier` agents are used AS-IS (not modified)
  because their general-purpose frameworks naturally apply to academic content review

## See Also
- `literature-analyzer`: Generates the overall dashboard and matrix
- `academic-literature`: Downloads papers with institutional login
- `deep-research`: 18-agent pipeline for systematic literature review
- `academic-paper`: Uses the LR platform output to write the literature review section
- oh-my-claudecode `critic`: Multi-perspective quality gate (Opus model)
- oh-my-claudecode `verifier`: Evidence-based verification
