#!/usr/bin/env python3
"""Generate the NYC Immigrant Enclaves public view page from its governed artifact."""

from pathlib import Path
import difflib
import sys

from generate_fixture_page import main, outputs

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/fixtures/nyc-immigrant-enclaves-public-view.json"
TEMPLATE = ROOT / "templates/fixture-page.html"
HTML = ROOT / "inside-the-map-of-30-immigrant-enclaves/index.html"
JSONLD = ROOT / "inside-the-map-of-30-immigrant-enclaves/index.jsonld"
MANIFEST = ROOT / "inside-the-map-of-30-immigrant-enclaves/record-counts.json"

if __name__ == "__main__":
    if "--check" in sys.argv:
        for path, rendered in outputs(ARTIFACT, TEMPLATE, HTML, JSONLD, MANIFEST).items():
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != rendered:
                print(f"--- DIFF {path}")
                print("".join(difflib.unified_diff(
                    current.splitlines(keepends=True),
                    rendered.splitlines(keepends=True),
                    fromfile="committed",
                    tofile="generated",
                    n=3,
                )))
    defaults = [
        "--artifact", str(ARTIFACT),
        "--template", str(TEMPLATE),
        "--html", str(HTML),
        "--jsonld", str(JSONLD),
        "--manifest", str(MANIFEST),
    ]
    sys.argv[1:1] = defaults
    raise SystemExit(main())
