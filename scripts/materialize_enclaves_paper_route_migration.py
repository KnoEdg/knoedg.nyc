#!/usr/bin/env python3
"""Materialize the approved Enclaves data-paper route migration.

One-shot publication helper. It updates the already-published public fixture copy
to the exact ADR-0011 identity change, writes a redirect-only legacy HTML stub,
removes the legacy JSON-LD representation, and updates the sitemap. Rendering of
the canonical page is performed separately by the shared renderer.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/fixtures/nyc-immigrant-enclaves-data-paper.json"
SITEMAP = ROOT / "sitemap.xml"
LEGACY_DIR = ROOT / "nyc-immigrant-enclaves-paper"
OLD = "https://knoedg.nyc/nyc-immigrant-enclaves-paper/"
NEW = "https://knoedg.nyc/data/papers/the-map-of-30-immigrant-enclaves-provenance-evidence-and-limits/"
NEW_VERSION = "2026-08-29.1"


def migrate_artifact() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    data["resource"] = NEW
    data["artifactVersion"] = NEW_VERSION
    data["page"]["canonical"] = NEW
    data["page"]["alternate"]["href"] = NEW + "index.jsonld"

    scholarly = [
        node for node in data.get("semanticRepresentation", {}).get("@graph", [])
        if isinstance(node, dict) and node.get("@type") == "schema:ScholarlyArticle"
    ]
    if len(scholarly) != 1:
        raise SystemExit(f"expected one schema:ScholarlyArticle, got {len(scholarly)}")
    if scholarly[0].get("@id") not in {OLD, NEW}:
        raise SystemExit("unexpected ScholarlyArticle identity")
    scholarly[0]["@id"] = NEW

    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if OLD in text:
        raise SystemExit("legacy paper URI remains inside public fixture after migration")
    ARTIFACT.write_text(text, encoding="utf-8")


def write_redirect_stub() -> None:
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)
    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="0; url={NEW}">
  <link rel="canonical" href="{NEW}">
  <title>Data paper moved — KnoEdg.NYC</title>
  <script>location.replace({json.dumps(NEW)});</script>
</head>
<body>
  <main>
    <p>This data paper has moved to its canonical title-derived address.</p>
    <p><a href="{NEW}">Continue to The Map of 30 Immigrant Enclaves — provenance, evidence and limits</a>.</p>
  </main>
</body>
</html>
'''
    (LEGACY_DIR / "index.html").write_text(html, encoding="utf-8")
    (LEGACY_DIR / "index.jsonld").unlink(missing_ok=True)


def update_sitemap() -> None:
    text = SITEMAP.read_text(encoding="utf-8")
    old_loc = f"    <loc>{OLD}</loc>"
    new_loc = f"    <loc>{NEW}</loc>"
    if old_loc in text:
        text = text.replace(old_loc, new_loc, 1)
    elif new_loc not in text:
        raise SystemExit("sitemap has neither legacy nor canonical paper location")
    SITEMAP.write_text(text, encoding="utf-8")


def main() -> int:
    migrate_artifact()
    write_redirect_stub()
    update_sitemap()
    print(f"materialized public paper migration: {OLD} -> {NEW}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
