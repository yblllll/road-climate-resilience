#!/usr/bin/env python3
"""
Auto-extract key sentences from all 21 literature review PDFs.
Uses pattern-based sentence scoring to find Method/Conclusion/Innovation/Limitation
from the CORRECT sections (not abstracts).

Output: auto_annotations.json — verified annotation data for the LR platform.
"""
import fitz
import json
import re
import os
import sys

PDF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Literature_Review")

# Category-specific patterns for sentence scoring
PATTERNS = {
    'method': [
        r'(?:this study|we|this paper|the paper)\s+(?:adopt|use|employ|apply|implement|develop|propose|present|build)',
        r'(?:model|regression|GLM|OLS|GWR|simulation|framework|algorithm|equation)\b',
        r'(?:Breusch.Pagan|heteroscedasticity|overdispersion|deviance|likelihood|ANOVA|chi.square)',
        r'(?:variable|covariate|predictor|control|dummy|interaction|dependent|independent)',
        r'(?:data|dataset|sample|observation|detector|camera|ANPR|sensor|survey|census)',
        r'(?:implemented|software|package|version|Python|Stata|MATLAB|MATSim)',
        r'(?:log.link|log.transformed|exponential|Poisson|binomial|Gamma)',
        r'(?:calibrat|validat|cross.validat|train|test split)',
    ],
    'conclusion': [
        r'\d+\.?\d*\s*%',  # Percentages
        r'(?:statistically?\s+)?(?:significant|insignificant)',
        r'(?:increase|decrease|decline|rise|fall|drop|reduction|growth)',
        r'(?:finding|result|evidence|suggest|indicate|demonstrate|show\s+that|reveal)',
        r'(?:paradox|contrary|despite|although|however|surprisingly|unexpected)',
        r'(?:R.squared|R2|RMSE|MAPE|AIC|BIC|p.value|coefficient)',
        r'(?:outperform|superior|better than|compared to|improvement)',
    ],
    'innovation': [
        r'(?:first|novel|new|unique|original|contribut)',
        r'(?:to the best of|no previous|unlike prior|gap|underexplored|overlooked)',
        r'(?:this paper|this study|our work)\s+(?:is|provides|offers|presents|proposes)',
        r'(?:advance|extend|bridge|fill)',
    ],
    'limitation': [
        r'(?:limitation|caveat|shortcoming|weakness|constraint|drawback)',
        r'(?:cannot|could not|unable|lack|absence|missing|omit)',
        r'(?:future research|future stud|further work|to be explored|remain)',
        r'(?:generalisab|transferab|specific to|only\s+\w+\s+cit)',
        r'(?:does not|do not|is not|are not)\s+(?:provide|account|consider|include|capture)',
        r'(?:assumption|simplif|approximat)',
    ],
}

# Section heading patterns
SECTION_HEADINGS = [
    (r'(?:^|\n)\s*\d+\.?\s*(Introduction|Background)\b', 'introduction'),
    (r'(?:^|\n)\s*\d+\.?\s*(Literature|Related|Previous)\b', 'literature'),
    (r'(?:^|\n)\s*\d+\.?\s*(Method|Data|Study\s+area|Approach|Model|Framework|Experiment)\b', 'methodology'),
    (r'(?:^|\n)\s*\d+\.?\s*(Result|Finding|Analysis|Discussion|Case\s+study)\b', 'results'),
    (r'(?:^|\n)\s*\d+\.?\s*(Conclusion|Summary|Limitation|Policy|Implication|Recommendation)\b', 'conclusions'),
]


def detect_sections(pages):
    """Detect section boundaries from page text."""
    sections = {}
    current_section = 'preamble'
    section_starts = []

    for pg, text in sorted(pages.items()):
        for pattern, sec_type in SECTION_HEADINGS:
            if re.search(pattern, text, re.IGNORECASE):
                section_starts.append((pg, sec_type))

    # Build section ranges
    for i, (pg, sec_type) in enumerate(section_starts):
        end_pg = section_starts[i+1][0] if i+1 < len(section_starts) else max(pages.keys())
        if sec_type not in sections:
            sections[sec_type] = (pg, end_pg)
        else:
            # Extend existing section
            existing_start, existing_end = sections[sec_type]
            sections[sec_type] = (min(existing_start, pg), max(existing_end, end_pg))

    return sections


def get_sentences(pages, start_pg, end_pg):
    """Extract sentences from a page range."""
    sents = []
    for pg in range(start_pg, min(end_pg + 1, max(pages.keys()) + 1)):
        if pg not in pages:
            continue
        text = pages[pg].replace('\n', ' ')
        # Split on sentence boundaries
        for m in re.finditer(r'(?<=[.!?])\s+([A-Z][^.!?]{25,400}[.!?])', text):
            sents.append((pg, m.group(1).strip()))
        # Also try without lookbehind for first sentence
        m = re.match(r'([A-Z][^.!?]{25,400}[.!?])', text)
        if m:
            sents.append((pg, m.group(1).strip()))
    return sents


def score_sentence(sent, category):
    """Score a sentence for relevance to a category."""
    return sum(1 for p in PATTERNS[category] if re.search(p, sent, re.IGNORECASE))


def find_searchable_phrase(doc, pg, sent):
    """Find the longest searchable substring in the PDF."""
    for length in [70, 55, 45, 35, 25, 18]:
        if length > len(sent):
            continue
        phrase = sent[:length]
        if pg - 1 < len(doc):
            rects = doc[pg - 1].search_for(phrase)
            if rects:
                return phrase, pg, rects
    # Try nearby pages
    for offset in [-1, 1, -2, 2]:
        alt_pg = pg + offset
        if 0 < alt_pg <= len(doc):
            for length in [50, 35, 25]:
                if length > len(sent):
                    continue
                phrase = sent[:length]
                rects = doc[alt_pg - 1].search_for(phrase)
                if rects:
                    return phrase, alt_pg, rects
    return None, pg, []


def process_pdf(filepath):
    """Auto-extract annotations from a single PDF."""
    doc = fitz.open(filepath)
    pages = {i + 1: doc[i].get_text() for i in range(len(doc))}

    # Detect sections
    sections = detect_sections(pages)

    # Map categories to sections with fallbacks
    cat_sections = {
        'method': ['methodology', 'literature'],
        'conclusion': ['results', 'conclusions'],
        'innovation': ['introduction', 'literature'],
        'limitation': ['conclusions'],
    }

    result = {}
    for cat in ['method', 'conclusion', 'innovation', 'limitation']:
        candidates = []

        for sec_name in cat_sections[cat]:
            if sec_name not in sections:
                continue
            start, end = sections[sec_name]
            for pg, sent in get_sentences(pages, start, end):
                score = score_sentence(sent, cat)
                if score >= 1:
                    phrase, real_pg, rects = find_searchable_phrase(doc, pg, sent)
                    if phrase:
                        candidates.append((real_pg, sent, score, phrase))

        # Fallback: if no candidates, search ALL pages
        if not candidates:
            for pg, text in pages.items():
                text_clean = text.replace('\n', ' ')
                for m in re.finditer(r'(?<=[.!?])\s+([A-Z][^.!?]{25,400}[.!?])', text_clean):
                    sent = m.group(1).strip()
                    score = score_sentence(sent, cat)
                    if score >= 2:  # Higher threshold for fallback
                        phrase, real_pg, rects = find_searchable_phrase(doc, pg, sent)
                        if phrase:
                            candidates.append((real_pg, sent, score, phrase))

        # Sort by score, deduplicate
        candidates.sort(key=lambda x: -x[2])
        selected = []
        for pg, sent, score, phrase in candidates:
            if len(selected) >= 6:
                break
            if any(phrase[:25] == p[3][:25] for p in selected):
                continue
            selected.append((pg, sent, score, phrase))

        # Build items
        items = []
        for pg, sent, score, phrase in selected:
            items.append({
                "note": sent[:300],
                "original_texts": [{"text": phrase, "page": pg}],
            })

        result[cat] = items

    doc.close()
    return result, sections


def annotate_pdf(filepath, annotations):
    """Write colored highlights to PDF using quads-based approach (PyMuPDF 1.27.2 fix)."""
    COLORS = {
        "method": (0.204, 0.596, 0.859),
        "conclusion": (0.298, 0.686, 0.314),
        "innovation": (0.953, 0.612, 0.071),
        "limitation": (0.906, 0.298, 0.235),
    }

    base = os.path.splitext(filepath)[0]
    out_path = base + "_annotated.pdf"

    doc = fitz.open(filepath)
    hl_count = 0

    for cat in ['method', 'conclusion', 'innovation', 'limitation']:
        color = COLORS[cat]
        for item in annotations.get(cat, []):
            for ot in item.get('original_texts', []):
                phrase = ot.get('text', '')
                if not phrase or len(phrase) < 3:
                    continue
                for pi in range(len(doc)):
                    # MUST use load_page() not doc[pi] — PyMuPDF 1.27.2 bug
                    page = doc.load_page(pi)
                    quads = page.search_for(phrase, quads=True)
                    if quads:
                        try:
                            a = page.add_highlight_annot(quads=quads[:3])
                            a.update()
                            a.set_colors(stroke=color)
                            a.update()
                            hl_count += 1
                        except Exception as e:
                            pass
                        ot['page'] = pi + 1
                        break

    doc.save(out_path, garbage=4, deflate=True)
    doc.close()
    return hl_count


def main():
    print(f"Auto-Extract Annotation Tool v1.0")
    print(f"PDF Directory: {PDF_DIR}")
    print(f"PyMuPDF: {fitz.__version__}")
    print("=" * 70)

    all_annotations = {}
    total_hl = 0

    # Process all PDFs
    pdfs = sorted([f for f in os.listdir(PDF_DIR)
                   if f.endswith('.pdf') and '_annotated' not in f and '_test' not in f])

    print(f"\nProcessing {len(pdfs)} PDFs...\n")

    for fn in pdfs:
        filepath = os.path.join(PDF_DIR, fn)

        # Auto-extract
        annotations, sections = process_pdf(filepath)

        # Count
        n_items = sum(len(annotations[c]) for c in ['method', 'conclusion', 'innovation', 'limitation'])
        n_texts = sum(len(item['original_texts']) for c in ['method', 'conclusion', 'innovation', 'limitation'] for item in annotations[c])
        sec_names = ', '.join(sorted(sections.keys()))

        # Annotate PDF
        hl = annotate_pdf(filepath, annotations)
        total_hl += hl

        mc = ' '.join(f"{c[0].upper()}:{len(annotations[c])}" for c in ['method', 'conclusion', 'innovation', 'limitation'])
        print(f"  {fn[:55]:55s} {mc:20s} {hl:3d} hl  [{sec_names}]")

        all_annotations[fn] = annotations

    # Save
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auto_annotations.json")
    with open(output_path, "w") as f:
        json.dump(all_annotations, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"Done: {len(all_annotations)} papers, {total_hl} total highlights")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
