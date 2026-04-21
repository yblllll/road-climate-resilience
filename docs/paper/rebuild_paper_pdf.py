#!/usr/bin/env python3
"""
rebuild_paper_pdf.py — Apply paper_edits.json to docs/paper_v2/main.tex and
rebuild main.pdf via tectonic.

Inputs
------
  docs/paper/paper_edits.json  — edits keyed by block index, with origHtml/origText
  docs/paper/paper_content.json — canonical block list from build_paper_view.py
  docs/paper_v2/main.tex        — source LaTeX

Outputs
-------
  docs/paper_v2/main.pdf       — freshly compiled PDF (tectonic)
  docs/paper_v2/main.tex.bak   — automatic backup of the previous main.tex

Safety
------
  * main.tex is always backed up before modification.
  * Edits whose orig text cannot be located are logged + skipped (the block
    in main.tex is left untouched) rather than corrupting the file.
  * If tectonic fails, main.tex is restored from the backup.
  * Run in --dry-run to preview without writing anything.

Usage
-----
  uv run python docs/paper/rebuild_paper_pdf.py                 # default paths
  uv run python docs/paper/rebuild_paper_pdf.py --dry-run       # preview only
  uv run python docs/paper/rebuild_paper_pdf.py --no-compile    # write tex, skip tectonic
"""
from __future__ import annotations

import argparse
import html as htmllib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


# Match the <a class="cite-link" data-key="KEY" ...>KEY</a> anchors emitted
# by build_paper_view.py.
CITE_ANCHOR_RE = re.compile(
    r'<a\s[^>]*class="cite-link"[^>]*data-key="([^"]+)"[^>]*>[^<]*</a>'
)
# Match the bracketed comma-separated list of cite anchors
# e.g. [<a data-key="a">a</a>, <a data-key="b">b</a>]
CITE_BRACKET_RE = re.compile(
    r'\[\s*((?:<a[^>]*class="cite-link"[^>]*>[^<]*</a>(?:\s*,\s*)?)+)\s*\]'
)
TAG_RE = re.compile(r'<[^>]+>')


# ────────────────────────────────────────────────────────────────────────────
# HTML ↔ LaTeX conversion
# ────────────────────────────────────────────────────────────────────────────

def html_to_latex(s: str) -> str:
    """
    Reverse build_paper_view.py's LaTeX→HTML conversion.
    Handles cite anchors, basic formatting, typographic quotes and dashes.
    """
    def cite_bracket(m: re.Match) -> str:
        keys = CITE_ANCHOR_RE.findall(m.group(1))
        return '\\citep{' + ','.join(keys) + '}' if keys else m.group(0)

    s = CITE_BRACKET_RE.sub(cite_bracket, s)
    s = CITE_ANCHOR_RE.sub(lambda m: '\\citep{' + m.group(1) + '}', s)

    # Preserve inline formatting
    s = re.sub(r'<strong[^>]*>([^<]*)</strong>', r'\\textbf{\1}', s)
    s = re.sub(r'<b[^>]*>([^<]*)</b>',           r'\\textbf{\1}', s)
    s = re.sub(r'<em[^>]*>([^<]*)</em>',         r'\\emph{\1}',   s)
    s = re.sub(r'<i[^>]*>([^<]*)</i>',           r'\\emph{\1}',   s)
    s = re.sub(r'<code[^>]*>([^<]*)</code>',     r'\\texttt{\1}', s)
    s = re.sub(r'<u[^>]*>([^<]*)</u>',           r'\\underline{\1}', s)

    # Strip remaining tags
    s = TAG_RE.sub('', s)

    # Decode HTML entities
    s = htmllib.unescape(s)

    # Typography back to LaTeX conventions
    s = s.replace('\u201c', '``').replace('\u201d', "''")
    s = s.replace('\u2018', '`').replace('\u2019', "'")
    s = s.replace('\u2014', '---').replace('\u2013', '--')
    return s.strip()


def strip_to_plain(html_text: str) -> str:
    """Convert our HTML to plain readable text for anchor matching."""
    s = CITE_BRACKET_RE.sub('', html_text)
    s = CITE_ANCHOR_RE.sub(lambda m: '', s)
    s = TAG_RE.sub('', s)
    s = htmllib.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


# ────────────────────────────────────────────────────────────────────────────
# Finding the paragraph span in main.tex that corresponds to an edit
# ────────────────────────────────────────────────────────────────────────────

STOP_WORDS = {
    'the', 'and', 'that', 'with', 'from', 'this', 'have', 'been', 'such',
    'also', 'more', 'when', 'than', 'into', 'which', 'only', 'most', 'some',
    'they', 'were', 'these', 'those', 'their', 'upon', 'both', 'does', 'each',
    'very', 'over', 'what', 'make', 'made', 'many', 'other', 'while',
}


def find_paragraph_span(
    tex_lines: list[str],
    probe_text: str,
    used_ranges: list[tuple[int, int]],
) -> tuple[int, int] | None:
    """
    Locate the paragraph in tex_lines whose plain-text form contains a
    distinctive 6-7 word phrase from probe_text. Paragraph = contiguous
    non-blank lines delimited by blank lines / sectioning commands /
    environment markers.
    """
    words = [w for w in probe_text.split() if len(w) >= 3]
    words = [w for w in words if w.lower() not in STOP_WORDS]
    if not words:
        return None

    # Try multiple anchor phrases so we survive phrasing quirks
    candidates: list[str] = []
    step = max(1, len(words) // 6)
    for start in range(0, max(1, len(words) - 6), step):
        phrase = ' '.join(words[start:start + 7])
        if len(phrase) >= 24:
            candidates.append(phrase)
    # Fallback: the whole probe if it's short enough
    if not candidates:
        candidates.append(' '.join(words))

    joined = '\n'.join(tex_lines)
    for phrase in candidates:
        parts = [re.escape(w) for w in phrase.split()]
        # allow any whitespace (including newlines) + tolerate LaTeX commands
        # intervening between words (e.g. \citep{})
        pat = re.compile(
            r'(?:[\s]|\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{[^{}]*\})+'.join(parts),
            re.IGNORECASE | re.DOTALL,
        )
        m = pat.search(joined)
        if not m:
            continue
        line_idx = joined[:m.start()].count('\n')

        start = line_idx
        while start > 0:
            prev = tex_lines[start - 1].strip()
            if (
                not prev
                or prev.startswith('%')
                or prev.startswith('\\section')
                or prev.startswith('\\subsection')
                or prev.startswith('\\subsubsection')
                or prev.startswith('\\begin{')
                or prev.startswith('\\end{')
            ):
                break
            start -= 1

        end = line_idx
        while end < len(tex_lines) - 1:
            nxt = tex_lines[end + 1].strip()
            if (
                not nxt
                or nxt.startswith('%')
                or nxt.startswith('\\section')
                or nxt.startswith('\\subsection')
                or nxt.startswith('\\subsubsection')
                or nxt.startswith('\\begin{')
                or nxt.startswith('\\end{')
            ):
                break
            end += 1

        span = (start, end)
        if any(span[0] <= u[1] and span[1] >= u[0] for u in used_ranges):
            continue  # overlaps an already-replaced span
        return span
    return None


# ────────────────────────────────────────────────────────────────────────────
# Apply edits
# ────────────────────────────────────────────────────────────────────────────

def apply_edits(
    tex_path: Path,
    edits: dict,
    content_path: Path | None = None,
    dry_run: bool = False,
) -> tuple[str, list, list]:
    tex = tex_path.read_text()
    tex_lines = tex.splitlines()
    used_ranges: list[tuple[int, int]] = []
    applied: list[tuple] = []
    skipped: list[tuple] = []

    pc = None
    if content_path and content_path.exists():
        pc = json.loads(content_path.read_text())

    # Iterate high→low block index so line-number replacements don't shift
    # earlier searches.
    for idx_str, edit in sorted(
        edits.items(), key=lambda x: int(x[0]), reverse=True
    ):
        idx = int(idx_str)
        t = edit.get('type')

        if t in ('h2', 'h3', 'h4'):
            orig = (
                edit.get('origText')
                or (pc and idx < len(pc['blocks']) and pc['blocks'][idx].get('text'))
                or ''
            ).strip()
            new = (edit.get('text') or '').strip()
            if not orig or orig == new:
                continue
            cmd = {'h2': 'section', 'h3': 'subsection', 'h4': 'subsubsection'}[t]
            pat = re.compile(
                r'\\' + cmd + r'\*?\{\s*' + re.escape(orig) + r'\s*\}'
            )
            joined = '\n'.join(tex_lines)
            m = pat.search(joined)
            if not m:
                skipped.append((idx, t, f'heading not found: {orig[:50]!r}'))
                continue
            line_idx = joined[:m.start()].count('\n')
            tex_lines[line_idx] = tex_lines[line_idx].replace(
                m.group(0), '\\' + cmd + '{' + new + '}'
            )
            applied.append((idx, t, f'{orig[:40]!r} → {new[:40]!r}'))
            used_ranges.append((line_idx, line_idx))

        elif t == 'p':
            orig_html = (
                edit.get('origHtml')
                or (pc and idx < len(pc['blocks']) and pc['blocks'][idx].get('html'))
                or ''
            )
            new_html = edit.get('html') or ''
            if not orig_html or orig_html == new_html:
                continue
            probe = strip_to_plain(orig_html)
            if len(probe) < 20:
                skipped.append((idx, t, 'probe too short'))
                continue
            span = find_paragraph_span(tex_lines, probe, used_ranges)
            if not span:
                skipped.append((idx, t, f'paragraph not found for probe: {probe[:60]!r}'))
                continue
            new_latex = html_to_latex(new_html).strip()
            if not new_latex:
                skipped.append((idx, t, 'new latex empty'))
                continue
            old_block_preview = ' '.join(
                tex_lines[span[0]:span[1] + 1]
            )[:80].replace('\n', ' ')
            tex_lines[span[0]:span[1] + 1] = [new_latex]
            applied.append((idx, t, f'[L{span[0]+1}-L{span[1]+1}] {old_block_preview} …'))
            used_ranges.append(span)
        else:
            skipped.append((idx, t, 'unsupported block type'))

    new_tex = '\n'.join(tex_lines)
    if tex.endswith('\n') and not new_tex.endswith('\n'):
        new_tex += '\n'

    if not dry_run:
        tex_path.write_text(new_tex)

    return new_tex, applied, skipped


# ────────────────────────────────────────────────────────────────────────────
# Tectonic compilation
# ────────────────────────────────────────────────────────────────────────────

def run_tectonic(tex_path: Path, tectonic_bin: str, timeout_s: int = 240) -> tuple[int, str, str]:
    try:
        r = subprocess.run(
            [
                tectonic_bin,
                '--keep-intermediates',
                '--chatter', 'minimal',
                '--keep-logs',
                str(tex_path.name),
            ],
            capture_output=True, text=True, cwd=str(tex_path.parent),
            timeout=timeout_s,
        )
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        return 124, (e.stdout or '').decode() if isinstance(e.stdout, bytes) else (e.stdout or ''), 'timeout'


# ────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────

def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--edits',    default=str(repo_root / 'docs/paper/paper_edits.json'))
    ap.add_argument('--tex',      default=str(repo_root / 'docs/paper_v2/main.tex'))
    ap.add_argument('--content',  default=str(repo_root / 'docs/paper/paper_content.json'))
    ap.add_argument('--tectonic', default=None, help='tectonic binary (auto-detected if not given)')
    ap.add_argument('--no-compile', action='store_true', help='write tex but skip tectonic')
    ap.add_argument('--dry-run',    action='store_true', help='preview only, write nothing')
    ap.add_argument('--quiet',      action='store_true')
    args = ap.parse_args()

    tex_path = Path(args.tex)
    edits_path = Path(args.edits)
    content_path = Path(args.content) if args.content else None

    if not tex_path.exists():
        print(f'[rebuild] ERROR: tex file missing → {tex_path}', file=sys.stderr)
        return 2
    if not edits_path.exists():
        if not args.quiet:
            print(f'[rebuild] no paper_edits.json at {edits_path}; nothing to do.')
        return 0

    edits_obj = json.loads(edits_path.read_text())
    edits = edits_obj.get('edits', edits_obj) if isinstance(edits_obj, dict) else {}
    if not edits:
        if not args.quiet:
            print('[rebuild] paper_edits.json is empty — nothing to apply.')
        return 0

    print(f'[rebuild] loaded {len(edits)} edit(s) from {edits_path}')

    backup = tex_path.with_suffix('.tex.bak')
    if not args.dry_run:
        shutil.copy2(tex_path, backup)
        print(f'[rebuild] backup  → {backup}')

    _, applied, skipped = apply_edits(tex_path, edits, content_path, dry_run=args.dry_run)
    print(f'[rebuild] applied {len(applied)} / skipped {len(skipped)}')
    for a in applied:
        print(f'  \u2713 [idx {a[0]} {a[1]}] {a[2]}')
    for s in skipped:
        print(f'  \u2717 [idx {s[0]} {s[1]}] {s[2]}')

    if args.dry_run:
        print('[rebuild] --dry-run: tex not written, tectonic skipped')
        return 0
    if args.no_compile:
        print('[rebuild] --no-compile: skipping tectonic')
        return 0

    tectonic_bin = args.tectonic or shutil.which('tectonic') or '/opt/homebrew/bin/tectonic'
    if not Path(tectonic_bin).exists():
        print(f'[rebuild] ERROR: tectonic not found at {tectonic_bin}', file=sys.stderr)
        print('[rebuild] tex was written but NOT compiled. Run tectonic manually.')
        return 2

    print(f'[rebuild] compiling via {tectonic_bin} …')
    t0 = time.time()
    rc, so, se = run_tectonic(tex_path, tectonic_bin)
    print(f'[rebuild] tectonic exit={rc} in {time.time()-t0:.1f}s')
    if rc != 0:
        print('[rebuild] tectonic FAILED — restoring backup.')
        if so: print((so or '')[-2000:])
        if se: print((se or '')[-2000:], file=sys.stderr)
        shutil.copy2(backup, tex_path)
        return rc
    pdf = tex_path.with_suffix('.pdf')
    if pdf.exists():
        print(f'[rebuild] OK → {pdf}')
    else:
        print('[rebuild] tectonic returned 0 but PDF not found at expected path.')
        return 3
    return 0


if __name__ == '__main__':
    sys.exit(main())
