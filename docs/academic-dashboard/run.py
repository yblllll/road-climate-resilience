#!/usr/bin/env python3
"""
LR PDF Annotation Platform — One-command launcher

Usage:
    python run.py                    # Start with default settings
    python run.py --port 9000        # Custom port
    python run.py --pdf-dir ./pdfs   # Custom PDF directory
    python run.py --extract          # Re-run auto-extraction before starting

Requirements:
    pip install pymupdf              # For PDF annotation (PyMuPDF/fitz)
"""

import argparse
import http.server
import json
import os
import socketserver
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path

# ============================================================
# Configuration
# ============================================================
DEFAULT_PORT = 8765
DEFAULT_PDF_DIR = "Literature_Review"
ANNO_FILE = "annotation_data_final.json"
READER_HTML = "literature_reader.html"
VIEWER_HTML = "literature_viewer.html"
MAIN_HTML = "literature_viewer.html"  # Main entry point (has all tabs including PDF Reader)
EXTRACT_SCRIPT = "auto_extract_all.py"
ANNOTATE_SCRIPT = "annotate_pdfs.py"


def check_dependencies():
    """Check that required packages are installed."""
    try:
        import fitz
        print(f"  PyMuPDF version: {fitz.__version__}")
    except ImportError:
        print("  WARNING: PyMuPDF not installed. Install with: pip install pymupdf")
        print("  PDF annotation features will not work without it.")
        return False
    return True


def check_files(base_dir, pdf_dir):
    """Check that required files exist."""
    issues = []

    reader = os.path.join(base_dir, READER_HTML)
    viewer = os.path.join(base_dir, VIEWER_HTML)
    anno = os.path.join(base_dir, ANNO_FILE)
    pdf_path = os.path.join(base_dir, pdf_dir)

    if not os.path.exists(reader):
        issues.append(f"Missing: {READER_HTML}")
    if not os.path.exists(viewer):
        issues.append(f"Missing: {VIEWER_HTML}")

    if os.path.exists(pdf_path):
        pdfs = [f for f in os.listdir(pdf_path) if f.endswith('.pdf') and '_annotated' not in f]
        annotated = [f for f in os.listdir(pdf_path) if f.endswith('_annotated.pdf')]
        print(f"  PDFs found: {len(pdfs)} original, {len(annotated)} annotated")
    else:
        print(f"  PDF directory not found: {pdf_path}")
        print(f"  Create it and add your PDFs, then run: python run.py --extract")
        os.makedirs(pdf_path, exist_ok=True)

    if not os.path.exists(anno):
        print(f"  No annotation data found. Run with --extract to generate.")
    else:
        with open(anno) as f:
            data = json.load(f)
        print(f"  Annotation data: {len(data)} papers")

    return issues


def run_extraction(base_dir):
    """Run the auto-extraction script."""
    script = os.path.join(base_dir, EXTRACT_SCRIPT)
    if os.path.exists(script):
        print("\n  Running auto-extraction...")
        result = subprocess.run([sys.executable, script], cwd=base_dir, capture_output=True, text=True)
        if result.returncode == 0:
            print("  Auto-extraction complete!")
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        else:
            print(f"  Extraction failed: {result.stderr[-300:]}")
    else:
        print(f"  Extraction script not found: {script}")


def run_annotation(base_dir):
    """Run the PDF annotation script."""
    script = os.path.join(base_dir, ANNOTATE_SCRIPT)
    if os.path.exists(script):
        print("\n  Generating annotated PDFs...")
        result = subprocess.run([sys.executable, script], cwd=base_dir, capture_output=True, text=True)
        if result.returncode == 0:
            print("  Annotation complete!")
        else:
            print(f"  Annotation failed: {result.stderr[-300:]}")
    else:
        print(f"  Annotation script not found: {script}")


def start_server(base_dir, port):
    """Start HTTP server and open browser."""
    os.chdir(base_dir)

    handler = http.server.SimpleHTTPRequestHandler
    handler.extensions_map.update({
        '.js': 'application/javascript',
        '.json': 'application/json',
    })

    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}/{MAIN_HTML}"
        print(f"\n  Server running at http://localhost:{port}/")
        print(f"  PDF Reader:  {url}")
        print(f"  Dashboard:   http://localhost:{port}/{VIEWER_HTML}")
        print(f"\n  Press Ctrl+C to stop\n")

        # Open browser after short delay
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Server stopped.")


def main():
    parser = argparse.ArgumentParser(description="LR PDF Annotation Platform")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Server port (default: {DEFAULT_PORT})")
    parser.add_argument("--pdf-dir", default=DEFAULT_PDF_DIR, help=f"PDF directory (default: {DEFAULT_PDF_DIR})")
    parser.add_argument("--extract", action="store_true", help="Re-run auto-extraction before starting")
    parser.add_argument("--annotate", action="store_true", help="Re-generate annotated PDFs before starting")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 50)
    print("  LR PDF Annotation Platform")
    print("=" * 50)
    print()

    # Check dependencies
    print("[1/4] Checking dependencies...")
    has_fitz = check_dependencies()

    # Check files
    print("\n[2/4] Checking files...")
    issues = check_files(base_dir, args.pdf_dir)
    if issues:
        for i in issues:
            print(f"  ERROR: {i}")
        sys.exit(1)

    # Extract if requested
    if args.extract and has_fitz:
        print("\n[3/4] Extracting annotations...")
        run_extraction(base_dir)
        if args.annotate:
            run_annotation(base_dir)
    else:
        print("\n[3/4] Skipping extraction (use --extract to run)")

    # Start server
    print(f"\n[4/4] Starting server on port {args.port}...")
    start_server(base_dir, args.port)


if __name__ == "__main__":
    main()
