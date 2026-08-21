#!/usr/bin/env python3
"""Generate the NYC Immigrant Enclaves data paper from its governed artifact."""

from pathlib import Path
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
                print(f"DRIFT {path.name} current_len={len(current)} rendered_len={len(rendered)}")
                limit = min(len(current), len(rendered))
                diffs = [i for i in range(limit) if current[i] != rendered[i]]
                for i in diffs[:20]:
                    lo, hi = max(0, i-30), min(limit, i+31)
                    print(f"DIFF_AT {i} current={ord(current[i])}:{current[i]!r} rendered={ord(rendered[i])}:{rendered[i]!r}")
                    print(f"CURRENT_CTX {current[lo:hi]!r}")
                    print(f"RENDERED_CTX {rendered[lo:hi]!r}")
                if len(current) != len(rendered):
                    i = limit
                    print(f"TAIL_AT {i} current={current[i:i+80]!r} rendered={rendered[i:i+80]!r}")
    defaults = [
        "--artifact", str(ARTIFACT),
        "--template", str(TEMPLATE),
        "--html", str(HTML),
        "--jsonld", str(JSONLD),
    ]
    sys.argv[1:1] = defaults
    raise SystemExit(main())
