#!/usr/bin/env python3
"""Validate the published geoBoundaries fixture and artifact parity."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "data" / "fixtures" / "nyc-geoboundaries-usa-adm2-counties.geojson"
SCHEMA_PATH = ROOT / "schemas" / "nyc-geoboundaries-usa-adm2-counties" / "v1"
VIEW_PATH = ROOT / "data" / "fixtures" / "nyc-boundary-public-view.json"
PUBLIC_URL = "https://knoedg.nyc/data/fixtures/nyc-geoboundaries-usa-adm2-counties.geojson"


def fail(message: str) -> None:
    raise SystemExit(f"NYC geoBoundaries fixture validation failed: {message}")


fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
view = json.loads(VIEW_PATH.read_text(encoding="utf-8"))
Draft202012Validator(schema, format_checker=FormatChecker()).validate(fixture)

features = fixture["features"]
if [feature["properties"]["boroughCode"] for feature in features] != [1, 2, 3, 4, 5]:
    fail("features are not in deterministic borough-code order")
if len({feature["properties"]["shapeID"] for feature in features}) != 5:
    fail("shape identifiers are not unique")
for feature in features:
    ring = feature["geometry"]["coordinates"][0]
    if ring[0] != ring[-1]:
        fail(f"polygon ring is not closed for {feature['properties']['shapeID']}")
    if feature["properties"]["governedAssertion"].startswith("https://knoedg.org/nyc-knowledge-pack/") is False:
        fail("governed assertion identity is not a stable public HTTPS IRI")

if fixture["selection"]["geometryIncluded"] is not True or fixture["selection"]["numericAreaIncluded"] is not False:
    fail("geometry/measurement disposition is inaccurate")
if fixture["comparisonDisposition"]["independentEvidenceFamily"] is not False:
    fail("Census-derived geometry is incorrectly treated as independent")

graph = view["semanticRepresentation"]["@graph"]
resource = next(node for node in graph if node.get("@id") == view["resource"])
if PUBLIC_URL not in {item["@id"] for item in resource["dcat:distribution"]}:
    fail("JSON-LD dataset does not declare the geoBoundaries distribution")
distribution = next((node for node in graph if node.get("@id") == PUBLIC_URL), None)
if not distribution or distribution.get("dcat:downloadURL", {}).get("@id") != PUBLIC_URL:
    fail("JSON-LD geoBoundaries distribution is missing or malformed")
if distribution.get("dcterms:license", {}).get("@id") != fixture["rights"]["licenseUrl"]:
    fail("JSON-LD license does not match fixture rights")

blocks = json.dumps(view["page"]["contentBlocks"], ensure_ascii=False)
if "/data/fixtures/nyc-geoboundaries-usa-adm2-counties.geojson" not in blocks:
    fail("human-visible download link is absent")
if "CC BY 4.0" not in blocks:
    fail("human-visible license attribution is absent")

serialized = json.dumps(fixture, ensure_ascii=False).lower()
for private_coordinate in ["knoedg/pack-nyc", "github.com/knoedg/pack-nyc", "meta-knoedg-nyc"]:
    if private_coordinate in serialized:
        fail(f"private repository coordinate leaked: {private_coordinate}")

print("NYC geoBoundaries public fixture validates: schema, five geometries, rights, artifact parity, stable identities, and public safety.")
