#!/usr/bin/env python3
"""Generate the NYC Immigrant Enclaves public view page from its governed artifact."""

from pathlib import Path
import base64
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
                encoded = base64.b64encode(rendered.encode("utf-8")).decode("ascii")
                print(f"CANONICAL_BASE64 {path.name} {encoded}")
    defaults = [
        "--artifact", str(ARTIFACT),
        "--template", str(TEMPLATE),
        "--html", str(HTML),
        "--jsonld", str(JSONLD),
        "--manifest", str(MANIFEST),
    ]
    sys.argv[1:1] = defaults
    raise SystemExit(main())
