#!/usr/bin/env python3
"""Generate the NYC Boundaries public technical collection from its approved artifact."""

from pathlib import Path
import sys

from generate_fixture_page import main

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/fixtures/nyc-boundaries-technical-collection.json"

if __name__ == "__main__":
    sys.argv[1:1] = [
        "--artifact", str(ARTIFACT),
        "--template", str(ROOT / "templates/fixture-page.html"),
        "--html", str(ROOT / "data/nyc-boundaries/index.html"),
        "--jsonld", str(ROOT / "data/nyc-boundaries/index.jsonld"),
        "--manifest", str(ROOT / "data/nyc-boundaries/record-counts.json"),
    ]
    raise SystemExit(main())
