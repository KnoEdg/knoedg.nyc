#!/usr/bin/env python3
"""Generate the NYC Immigrant Enclaves data paper from its governed artifact.

No --manifest: a data paper cites a public view's claims and holds none of its
own, so it carries no record counts to publish. The renderer refuses one.
"""

from pathlib import Path
import sys

from generate_fixture_page import main

ROOT = Path(__file__).resolve().parents[1]
PAPER_ROUTE = ROOT / "data" / "papers" / "the-map-of-30-immigrant-enclaves-provenance-evidence-and-limits"

if __name__ == "__main__":
    defaults = [
        "--artifact", str(ROOT / "data/fixtures/nyc-immigrant-enclaves-data-paper.json"),
        "--template", str(ROOT / "templates/data-paper.html"),
        "--html", str(PAPER_ROUTE / "index.html"),
        "--jsonld", str(PAPER_ROUTE / "index.jsonld"),
    ]
    sys.argv[1:1] = defaults
    raise SystemExit(main())
