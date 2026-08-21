#!/usr/bin/env python3
"""Generate the NYC Immigrant Enclaves data paper from its governed artifact.

No --manifest: a data paper cites a public view's claims and holds none of its
own, so it carries no record counts to publish. The renderer refuses one.
"""

from pathlib import Path
import difflib
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
    ]
    sys.argv[1:1] = defaults
    raise SystemExit(main())
