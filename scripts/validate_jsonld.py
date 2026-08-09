#!/usr/bin/env python3
"""Expand the published JSON-LD and fail on invalid or empty RDF output."""

import json
from pathlib import Path

from pyld import jsonld

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "nyc-boundaries/index.jsonld"

document = json.loads(SOURCE.read_text(encoding="utf-8"))
expanded = jsonld.expand(document)
if not isinstance(expanded, list) or not expanded:
    raise SystemExit("JSON-LD expansion produced no nodes")
for node in expanded:
    identifier = node.get("@id")
    if identifier is not None and not identifier.startswith("https://"):
        raise SystemExit(f"expanded graph contains a non-HTTPS node identity: {identifier}")
print(f"JSON-LD expansion validates: {len(expanded)} nodes.")
