#!/usr/bin/env python3
"""Validate the published Who's On First fixture and technical artifact parity."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "data" / "fixtures" / "nyc-whos-on-first-county-representations.geojson"
SCHEMA_PATH = ROOT / "schemas" / "nyc-whos-on-first-county-representations" / "v1"
VIEW_PATH = ROOT / "data" / "fixtures" / "nyc-boundaries-technical-collection.json"
PUBLIC_URL = "https://knoedg.nyc/data/fixtures/nyc-whos-on-first-county-representations.geojson"


def fail(message: str) -> None:
    raise SystemExit(f"NYC Who's On First fixture validation failed: {message}")


def rings_closed(geometry: dict) -> bool:
    if geometry["type"] == "Polygon":
        polygons = [geometry["coordinates"]]
    elif geometry["type"] == "MultiPolygon":
        polygons = geometry["coordinates"]
    else:
        return False
    for polygon in polygons:
        for ring in polygon:
            if ring[0] != ring[-1]:
                return False
    return True


fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
view = json.loads(VIEW_PATH.read_text(encoding="utf-8"))
Draft202012Validator(schema, format_checker=FormatChecker()).validate(fixture)

features = fixture["features"]
if [feature["properties"]["boroughCode"] for feature in features] != [1, 2, 3, 4, 5]:
    fail("features are not in deterministic borough-code order")
if len({feature["properties"]["wofId"] for feature in features}) != 5:
    fail("WOF identifiers are not unique")
for feature in features:
    if not rings_closed(feature["geometry"]):
        fail(f"polygon ring is not closed for WOF:{feature['properties']['wofId']}")
    if feature["properties"]["governedAssertion"].startswith("https://knoedg.org/nyc-knowledge-pack/") is False:
        fail("governed assertion identity is not a stable public HTTPS IRI")

if fixture["selection"]["geometryIncluded"] is not True:
    fail("geometry disposition is inaccurate")
if fixture["comparisonDisposition"]["independentEvidenceFamily"] is not False:
    fail("Quattroshapes-derived geometry is incorrectly treated as independent")

graph = view["semanticRepresentation"]["@graph"]
resource = next(node for node in graph if node.get("@id") == view["resource"])
if PUBLIC_URL not in {item["@id"] for item in resource["dcat:distribution"]}:
    fail("technical JSON-LD dataset does not declare the Who's On First distribution")
distribution = next((node for node in graph if node.get("@id") == PUBLIC_URL), None)
if not distribution or distribution.get("dcat:downloadURL", {}).get("@id") != PUBLIC_URL:
    fail("technical JSON-LD Who's On First distribution is missing or malformed")
if distribution.get("dcterms:license", {}).get("@id") != fixture["rights"]["licenseUrl"]:
    fail("technical JSON-LD license does not match fixture rights")

blocks = json.dumps(view["page"]["contentBlocks"], ensure_ascii=False)
if "/data/fixtures/nyc-whos-on-first-county-representations.geojson" not in blocks:
    fail("technical collection download link is absent")
if "Who's On First" not in blocks or "Quattroshapes" not in blocks:
    fail("technical collection attribution is absent")

serialized = json.dumps(fixture, ensure_ascii=False).lower()
for private_coordinate in ["knoedg/pack-nyc", "github.com/knoedg/pack-nyc", "meta-knoedg-nyc"]:
    if private_coordinate in serialized:
        fail(f"private repository coordinate leaked: {private_coordinate}")

print("NYC Who's On First public fixture validates: schema, five geometries, rights, technical artifact parity, stable identities, and public safety.")
