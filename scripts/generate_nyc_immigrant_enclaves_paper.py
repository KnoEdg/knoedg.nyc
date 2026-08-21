#!/usr/bin/env python3
"""Generate the NYC Immigrant Enclaves data paper from its governed artifact.

No --manifest: a data paper cites a public view's claims and holds none of its
own, so it carries no record counts to publish. The renderer refuses one.
"""

from pathlib import Path
import base64
import sys

from generate_fixture_page import main, outputs

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/fixtures/nyc-immigrant-enclaves-data-paper.json"
TEMPLATE = ROOT / "templates/data-paper.html"
HTML = ROOT / "nyc-immigrant-enclaves-paper/index.html"
JSONLD = ROOT / "nyc-immigrant-enclaves-paper/index.jsonld"

if __name__ == "__main__":
    if "--check" in sys.argv:
        for path, rendered in outputs(ARTIFACT, TEMPLATE, HTML, JSONLD, None).items():
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != rendered:
                encoded = base64.b64encode(rendered.encode("utf-8")).decode("ascii")
                print(f"CANONICAL_BASE64 {path.name} {encoded}")
    defaults = [
        "--artifact", str(ARTIFACT),
        "--template", str(TEMPLATE),
        "--html", str(HTML),
        "--jsonld", str(JSONLD),
    ]
    sys.argv[1:1] = defaults
    raise SystemExit(main())
