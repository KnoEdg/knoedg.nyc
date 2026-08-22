#!/usr/bin/env python3
from pathlib import Path
import sys

from generate_fixture_page import main as render_main
from generate_public_technical_records import materialize

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/fixtures/30-immigrant-enclaves-map-technical-collection.json"

if __name__ == "__main__":
    check = "--check" in sys.argv[1:]
    sys.argv[1:1] = [
        "--artifact", str(ARTIFACT),
        "--template", str(ROOT / "templates/fixture-page.html"),
        "--html", str(ROOT / "data/30-immigrant-enclaves-map/index.html"),
        "--jsonld", str(ROOT / "data/30-immigrant-enclaves-map/index.jsonld"),
        "--manifest", str(ROOT / "data/30-immigrant-enclaves-map/record-counts.json"),
    ]
    result = render_main()
    if result:
        raise SystemExit(result)
    raise SystemExit(materialize(ROOT, ARTIFACT, check=check))
