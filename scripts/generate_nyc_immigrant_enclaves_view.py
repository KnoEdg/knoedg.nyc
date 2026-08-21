#!/usr/bin/env python3
"""Generate the NYC Immigrant Enclaves public view page from its governed artifact."""

from pathlib import Path
import sys

from generate_fixture_page import main

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    defaults = [
        "--artifact", str(ROOT / "data/fixtures/nyc-immigrant-enclaves-public-view.json"),
        "--template", str(ROOT / "templates/fixture-page.html"),
        "--html", str(ROOT / "inside-the-map-of-30-immigrant-enclaves/index.html"),
        "--jsonld", str(ROOT / "inside-the-map-of-30-immigrant-enclaves/index.jsonld"),
        "--manifest", str(ROOT / "inside-the-map-of-30-immigrant-enclaves/record-counts.json"),
    ]
    sys.argv[1:1] = defaults
    raise SystemExit(main())
