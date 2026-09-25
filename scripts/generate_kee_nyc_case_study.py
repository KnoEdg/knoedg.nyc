#!/usr/bin/env python3
"""Generate the KEE NYC flagship case-study page from its approved public-view artifact."""

from pathlib import Path
import sys

from generate_fixture_page import main

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    defaults = [
        "--artifact", str(ROOT / "data/fixtures/nyc-kee-case-study-public-view.json"),
        "--template", str(ROOT / "templates/fixture-page.html"),
        "--html", str(ROOT / "kee-nyc-case-study/index.html"),
        "--jsonld", str(ROOT / "kee-nyc-case-study/index.jsonld"),
        "--manifest", str(ROOT / "kee-nyc-case-study/record-counts.json"),
    ]
    sys.argv[1:1] = defaults
    raise SystemExit(main())
