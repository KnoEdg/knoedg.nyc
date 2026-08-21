#!/usr/bin/env python3
"""Generate the NYC Immigrant Enclaves data paper from its governed artifact.

No --manifest: a data paper cites a public view's claims and holds none of its
own, so it carries no record counts to publish. The renderer refuses one.
"""

from pathlib import Path
import hashlib
import sys

from generate_fixture_page import main

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    defaults = [
        "--artifact", str(ROOT / "data/fixtures/nyc-immigrant-enclaves-data-paper.json"),
        "--template", str(ROOT / "templates/data-paper.html"),
        "--html", str(ROOT / "nyc-immigrant-enclaves-paper/index.html"),
        "--jsonld", str(ROOT / "nyc-immigrant-enclaves-paper/index.jsonld"),
    ]
    sys.argv[1:1] = defaults
    code = main()
    if code == 0 and "--check" in sys.argv:
        for relative in [
            "data/fixtures/nyc-immigrant-enclaves-public-view.json",
            "data/fixtures/nyc-immigrant-enclaves-data-paper.json",
            "scripts/generate_nyc_immigrant_enclaves_view.py",
            "scripts/generate_nyc_immigrant_enclaves_paper.py",
            "inside-the-map-of-30-immigrant-enclaves/index.html",
            "inside-the-map-of-30-immigrant-enclaves/index.jsonld",
            "inside-the-map-of-30-immigrant-enclaves/record-counts.json",
            "nyc-immigrant-enclaves-paper/index.html",
            "nyc-immigrant-enclaves-paper/index.jsonld",
        ]:
            path = ROOT / relative
            print(f"PUBLISH_SHA256 {hashlib.sha256(path.read_bytes()).hexdigest()}  {relative}")
    raise SystemExit(code)
