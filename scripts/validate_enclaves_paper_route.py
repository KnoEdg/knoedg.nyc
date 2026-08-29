#!/usr/bin/env python3
"""Validate the ADR-0011 migration of the first Enclaves data paper."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/fixtures/nyc-immigrant-enclaves-data-paper.json"
LEGACY = ROOT / "nyc-immigrant-enclaves-paper"
CANON_DIR = ROOT / "data/papers/the-map-of-30-immigrant-enclaves-provenance-evidence-and-limits"
OLD = "https://knoedg.nyc/nyc-immigrant-enclaves-paper/"
NEW = "https://knoedg.nyc/data/papers/the-map-of-30-immigrant-enclaves-provenance-evidence-and-limits/"


def fail(message: str) -> None:
    raise SystemExit(f"Enclaves paper migration validation failed: {message}")


def main() -> int:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if data.get("resource") != NEW or data.get("page", {}).get("canonical") != NEW:
        fail("artifact resource/canonical is not the title-derived paper URI")
    if data.get("page", {}).get("alternate", {}).get("href") != NEW + "index.jsonld":
        fail("artifact alternate JSON-LD URI is not under the canonical paper route")
    if OLD in json.dumps(data, ensure_ascii=False):
        fail("legacy paper URI remains inside the public-safe artifact copy")

    html_path = CANON_DIR / "index.html"
    jsonld_path = CANON_DIR / "index.jsonld"
    if not html_path.is_file() or not jsonld_path.is_file():
        fail("canonical rendered HTML/JSON-LD pair is missing")
    html = html_path.read_text(encoding="utf-8")
    if f'<link rel="canonical" href="{NEW}">' not in html:
        fail("canonical HTML does not declare the canonical paper URI")
    graph = json.loads(jsonld_path.read_text(encoding="utf-8"))
    if OLD in json.dumps(graph, ensure_ascii=False):
        fail("canonical JSON-LD still contains the legacy paper URI")

    redirect = (LEGACY / "index.html").read_text(encoding="utf-8")
    if NEW not in redirect or 'http-equiv="refresh"' not in redirect or 'rel="canonical"' not in redirect:
        fail("legacy HTML is not a redirect-only canonicalization surface")
    if (LEGACY / "index.jsonld").exists():
        fail("legacy JSON-LD representation still exists as a second semantic identity")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    if NEW not in sitemap or OLD in sitemap:
        fail("sitemap does not list only the canonical paper route")

    print("Enclaves paper canonical route and legacy redirect valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
