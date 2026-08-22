#!/usr/bin/env python3
"""Validate the target-side NYC Boundaries identity/surface split.

This validator checks publication structure and artifact/render parity. It does not
author or independently recalculate governed boundary facts.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_RESOURCE = "https://knoedg.nyc/nyc-boundaries/"
TECH_RESOURCE = "https://knoedg.nyc/data/nyc-boundaries/"
OLD_FRAGMENT_PREFIX = PUBLIC_RESOURCE + "#"
NEW_FRAGMENT_PREFIX = TECH_RESOURCE + "#"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    public = load("data/fixtures/nyc-boundaries-public-page.json")
    tech = load("data/fixtures/nyc-boundaries-technical-collection.json")
    public_jsonld = load("nyc-boundaries/index.jsonld")
    tech_jsonld = load("data/nyc-boundaries/index.jsonld")
    public_manifest = load("nyc-boundaries/record-counts.json")
    tech_manifest = load("data/nyc-boundaries/record-counts.json")
    public_html = (ROOT / "nyc-boundaries/index.html").read_text(encoding="utf-8")
    tech_html = (ROOT / "data/nyc-boundaries/index.html").read_text(encoding="utf-8")

    if public["resource"] != PUBLIC_RESOURCE or tech["resource"] != TECH_RESOURCE:
        raise SystemExit("boundary surface resource identity mismatch")
    if public["activeRecordCount"] != tech["activeRecordCount"]:
        raise SystemExit("public/technical active record count mismatch")
    if public["countingGranularity"] != tech["countingGranularity"]:
        raise SystemExit("public/technical counting granularity mismatch")

    for forbidden in ("independentLandAreaComparison", "whosOnFirstGeometricAreas"):
        if forbidden in public:
            raise SystemExit(f"general-public artifact leaked technical payload: {forbidden}")
        if forbidden not in tech:
            raise SystemExit(f"technical artifact lost governed payload: {forbidden}")

    public_markers = (
        "Compared views",
        "Measurement availability and comparison disposition",
        "geom:area_square_m",
    )
    for marker in public_markers:
        if marker in public_html:
            raise SystemExit(f"general-public HTML leaked technical section: {marker}")
    if TECH_RESOURCE not in public_html:
        raise SystemExit("general-public HTML does not link to technical collection")
    for marker in public_markers:
        if marker not in tech_html:
            raise SystemExit(f"technical HTML missing governed section: {marker}")

    if public_jsonld != public["semanticRepresentation"]:
        raise SystemExit("general-public JSON-LD is not the artifact representation")
    if tech_jsonld != tech["semanticRepresentation"]:
        raise SystemExit("technical JSON-LD is not the artifact representation")

    graph = tech["semanticRepresentation"]["@graph"]
    graph_text = json.dumps(tech["semanticRepresentation"], ensure_ascii=False)
    if OLD_FRAGMENT_PREFIX in graph_text:
        raise SystemExit("technical JSON-LD retains old public-page fragment namespace")
    if NEW_FRAGMENT_PREFIX not in graph_text:
        raise SystemExit("technical JSON-LD has no technical fragment namespace")

    datasets = [
        node for node in graph
        if isinstance(node, dict)
        and node.get("@id") == TECH_RESOURCE
        and (
            node.get("@type") == "dcat:Dataset"
            or isinstance(node.get("@type"), list) and "dcat:Dataset" in node.get("@type", [])
        )
    ]
    if len(datasets) != 1:
        raise SystemExit("technical collection must have exactly one root Dataset identity")
    if datasets[0].get("dcat:landingPage", {}).get("@id") != PUBLIC_RESOURCE:
        raise SystemExit("technical Dataset landing page must remain the general-public page")

    page_nodes = [node for node in graph if isinstance(node, dict) and node.get("@id") == TECH_RESOURCE + "#page"]
    if len(page_nodes) != 1:
        raise SystemExit("technical collection must have exactly one technical WebPage node")
    if page_nodes[0].get("schema:url") != TECH_RESOURCE:
        raise SystemExit("technical WebPage URL mismatch")
    if page_nodes[0].get("schema:mainEntity", {}).get("@id") != TECH_RESOURCE:
        raise SystemExit("technical WebPage mainEntity mismatch")

    for manifest, resource in ((public_manifest, PUBLIC_RESOURCE), (tech_manifest, TECH_RESOURCE)):
        if manifest.get("resource") != resource:
            raise SystemExit(f"manifest resource mismatch: {resource}")
        if manifest.get("activeRecordCount") != public["activeRecordCount"]:
            raise SystemExit(f"manifest count mismatch: {resource}")

    print("NYC Boundaries public/technical target split validates")


if __name__ == "__main__":
    main()
