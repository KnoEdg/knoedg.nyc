#!/usr/bin/env python3
"""Generate the NYC geoBoundaries source page from its governed artifact."""

from pathlib import Path
import sys

from generate_fixture_page import main

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    defaults = [
        "--artifact", str(ROOT / "data/fixtures/nyc-geoboundaries-source-public-view.json"),
        "--template", str(ROOT / "templates/fixture-page.html"),
        "--html", str(ROOT / "nyc-geoboundaries/index.html"),
        "--jsonld", str(ROOT / "nyc-geoboundaries/index.jsonld"),
        "--manifest", str(ROOT / "nyc-geoboundaries/record-counts.json"),
    ]
    sys.argv[1:1] = defaults
    raise SystemExit(main())
