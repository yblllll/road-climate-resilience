#!/usr/bin/env python3
"""
watch_paper_edits.py — Poll docs/paper/paper_edits.json for mtime changes;
invoke rebuild_paper_pdf.py automatically whenever the file is updated.

Run this once in a terminal:

    uv run python docs/paper/watch_paper_edits.py

Then in the browser, every time you click "Export JSON → rebuild PDF" and
drop the downloaded paper_edits.json into docs/paper/, the watcher will
rebuild docs/paper_v2/main.pdf within ~2s. The Manuscript PDF tab in
literature_viewer.html auto-reloads it (HTTP HEAD polling, 5s interval).

Flags:
    --interval FLOAT   polling interval (default 2.0s)
    --no-initial       skip rebuild on startup even if paper_edits.json exists
    --once             rebuild once if edits file exists, then exit
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    default_edits = root / 'docs/paper/paper_edits.json'
    default_rebuild = root / 'docs/paper/rebuild_paper_pdf.py'

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--edits',    default=str(default_edits))
    ap.add_argument('--rebuild',  default=str(default_rebuild))
    ap.add_argument('--interval', type=float, default=2.0)
    ap.add_argument('--no-initial', action='store_true',
                    help='skip rebuild on startup even if paper_edits.json already exists')
    ap.add_argument('--once',       action='store_true',
                    help='rebuild once if edits file exists, then exit')
    args = ap.parse_args()

    edits_path = Path(args.edits)
    rebuild_path = Path(args.rebuild)

    if not rebuild_path.exists():
        print(f'[watch] ERROR: rebuild script not found → {rebuild_path}', file=sys.stderr)
        return 2

    def rebuild(tag: str) -> int:
        print(f'[watch] {tag} — running rebuild_paper_pdf.py')
        t0 = time.time()
        r = subprocess.run([sys.executable, str(rebuild_path)])
        print(f'[watch] rebuild exited {r.returncode} in {time.time()-t0:.1f}s')
        return r.returncode

    if args.once:
        if edits_path.exists():
            return rebuild('one-shot')
        print(f'[watch] {edits_path} not present; nothing to do.')
        return 0

    print(f'[watch] polling {edits_path}')
    print(f'[watch] interval = {args.interval}s ; Ctrl-C to stop.')

    last_mtime: float | None = None
    if edits_path.exists():
        last_mtime = edits_path.stat().st_mtime
        if not args.no_initial:
            rebuild('startup rebuild')

    while True:
        try:
            time.sleep(args.interval)
            if not edits_path.exists():
                continue
            m = edits_path.stat().st_mtime
            if last_mtime is None:
                last_mtime = m
                rebuild('edits appeared')
                continue
            if m != last_mtime:
                last_mtime = m
                rebuild(f'{time.strftime("%H:%M:%S", time.localtime(m))} — edits changed')
        except KeyboardInterrupt:
            print('\n[watch] stopped by user')
            return 0
        except Exception as e:
            # Don't die on transient filesystem hiccups
            print(f'[watch] warning: {e}')


if __name__ == '__main__':
    sys.exit(main())
