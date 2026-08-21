#!/usr/bin/env python3
"""Expand every published JSON-LD document and fail on invalid or empty output.

Widened 2026-08-21. This script previously expanded ONE hardcoded page, so
every page added after it -- six source views and, at the time of widening, two
more -- was never checked. A gate that covers one of nine files reports success
in the same words as a gate that covers all nine, which is the failure mode
worth more than the bug: it reads as coverage.

Discovery is by glob rather than by list, so a page added later cannot escape
by nobody remembering to register it.
"""

import json
from pathlib import Path

from pyld import jsonld

ROOT = Path(__file__).resolve().parents[1]
SOURCES = sorted(ROOT.glob("*/index.jsonld"))

if not SOURCES:
    raise SystemExit("no published JSON-LD documents found -- discovery is broken, not the corpus")

total = 0
for source in SOURCES:
    rel = source.relative_to(ROOT)
    document = json.loads(source.read_text(encoding="utf-8"))
    expanded = jsonld.expand(document)
    if not isinstance(expanded, list) or not expanded:
        raise SystemExit(f"{rel}: JSON-LD expansion produced no nodes")
    for node in expanded:
        identifier = node.get("@id")
        if identifier is not None and not identifier.startswith("https://"):
            raise SystemExit(f"{rel}: expanded graph contains a non-HTTPS node identity: {identifier}")
    print(f"  {rel}: {len(expanded)} nodes")
    total += len(expanded)

print(f"JSON-LD expansion validates across {len(SOURCES)} documents: {total} nodes.")
