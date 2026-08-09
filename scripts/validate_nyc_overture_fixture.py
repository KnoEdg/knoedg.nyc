#!/usr/bin/env python3
"""Validate the published Overture Maps division-area fixture and artifact parity."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "data" / "fixtures" / "nyc-overture-division-area-representations.geojson"
SCHEMA_PATH = ROOT / "schemas" / "nyc-overture-division-area-representations" / "v1"
VIEW_PATH = ROOT / "data" / "fixtures" / "nyc-boundary-public-view.json"
PUBLIC_URL = "https://knoedg.nyc/data/fixtures/nyc-overture-division-area-representations.geojson"


def fail(message: str) -> None:
    raise SystemExit(f"NYC Overture fixture validation failed: {message}")


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
if [feature["properties"]["boroughCode"] for feature in features] != [2, 2, 3, 3, 1, 1, 4, 4, 5, 5, 5]:
    fail("features are not in deterministic borough-code order")
if len({feature["properties"]["areaId"] for feature in features}) != 11:
    fail("area identifiers are not unique")
for feature in features:
    if not rings_closed(feature["geometry"]):
        fail(f"polygon ring is not closed for {feature['properties']['areaId']}")
    if feature["properties"]["governedAssertion"].startswith("https://knoedg.org/nyc-knowledge-pack/") is False:
        fail("governed assertion identity is not a stable public HTTPS IRI")

richmond = [f for f in features if f["properties"]["namePrimary"] == "Richmond County"]
if len(richmond) != 2:
    fail("Richmond County must have exactly two representations")
land = [f for f in richmond if f["properties"]["isLand"]]
maritime = [f for f in richmond if not f["properties"]["isLand"]]
if len(land) != 1 or len(maritime) != 1:
    fail("Richmond County must have exactly one land and one non-land representation")

if fixture["selection"]["geometryIncluded"] is not True:
    fail("geometry disposition is inaccurate")
if fixture["comparisonDisposition"]["independentEvidenceFamily"] is not False:
    fail("Overture-derived geometry is incorrectly treated as independent")

graph = view["semanticRepresentation"]["@graph"]
resource = next(node for node in graph if node.get("@id") == view["resource"])
if PUBLIC_URL not in {item["@id"] for item in resource["dcat:distribution"]}:
    fail("JSON-LD dataset does not declare the Overture distribution")
distribution = next((node for node in graph if node.get("@id") == PUBLIC_URL), None)
if not distribution or distribution.get("dcat:downloadURL", {}).get("@id") != PUBLIC_URL:
    fail("JSON-LD Overture distribution is missing or malformed")
if distribution.get("dcterms:license", {}).get("@id") != fixture["rights"]["licenseUrl"]:
    fail("JSON-LD license does not match fixture rights")

blocks = json.dumps(view["page"]["contentBlocks"], ensure_ascii=False)
if "/data/fixtures/nyc-overture-division-area-representations.geojson" not in blocks:
    fail("human-visible download link is absent")
if "Overture" not in blocks or "ODbL" not in blocks:
    fail("human-visible attribution is absent")

serialized = json.dumps(fixture, ensure_ascii=False).lower()
for private_coordinate in ["knoedg/pack-nyc", "github.com/knoedg/pack-nyc", "meta-knoedg-nyc"]:
    if private_coordinate in serialized:
        fail(f"private repository coordinate leaked: {private_coordinate}")

print("NYC Overture public fixture validates: schema, eleven geometries, Richmond land/maritime disposition, rights, artifact parity, and public safety.")
