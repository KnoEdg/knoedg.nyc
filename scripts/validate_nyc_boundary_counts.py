#!/usr/bin/env python3
"""Validate full artifact ownership for the NYC Boundaries fixture page."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/fixtures/nyc-boundary-public-view.json"
TEMPLATE = ROOT / "templates/fixture-page.html"
HTML = ROOT / "nyc-boundaries/index.html"
JSONLD = ROOT / "nyc-boundaries/index.jsonld"
MANIFEST = ROOT / "nyc-boundaries/record-counts.json"


def fail(message: str) -> None:
    raise SystemExit(f"fixture-page ownership validation failed: {message}")


data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
template = TEMPLATE.read_text(encoding="utf-8")
rendered = HTML.read_text(encoding="utf-8")
jsonld = json.loads(JSONLD.read_text(encoding="utf-8"))
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

if data.get("schemaVersion") != 2 or data.get("rendererContract") != "fixture-page/v1":
    fail("artifact does not declare fixture-page/v1 schema version 2")
if rendered.count("<article>") != 1 or data["page"]["articleHtml"] not in rendered:
    fail("complete artifact-owned article is not present exactly once")
if jsonld != data["semanticRepresentation"]:
    fail("JSON-LD is not the artifact-owned semantic representation")
groups = data["sourceGroups"]
if sum(group["count"] for group in groups) != data["activeRecordCount"]:
    fail("source-group counts do not reconcile")
if manifest["activeRecordCount"] != data["activeRecordCount"]:
    fail("manifest total disagrees with artifact")
for group in groups:
    if group["label"] not in data["page"]["articleHtml"]:
        fail(f"article does not expose source group {group['id']}")
for forbidden in [data["page"]["title"], str(data["activeRecordCount"]), *[g["label"] for g in groups]]:
    if forbidden in template:
        fail(f"template independently contains fixture content: {forbidden}")
if "BEGIN GENERATED" in rendered or "END GENERATED" in rendered:
    fail("partial-generation markers remain in the complete generated page")
print(f"Fixture page is fully artifact-generated: {data['activeRecordCount']} records, {len(groups)} groups, HTML + JSON-LD + manifest.")
