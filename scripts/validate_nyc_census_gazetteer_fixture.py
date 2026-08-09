#!/usr/bin/env python3
"""Validate the published Census Gazetteer fixture and its public-view links."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "data" / "fixtures" / "nyc-census-gazetteer-county-measurements.json"
SCHEMA_PATH = ROOT / "schemas" / "nyc-census-gazetteer-counties" / "v1"
VIEW_PATH = ROOT / "data" / "fixtures" / "nyc-boundary-public-view.json"
HTML_PATH = ROOT / "nyc-boundaries" / "index.html"
JSONLD_PATH = ROOT / "nyc-boundaries" / "index.jsonld"
PUBLIC_URL = "https://knoedg.nyc/data/fixtures/nyc-census-gazetteer-county-measurements.json"


def fail(message: str) -> None:
    raise SystemExit(f"Published NYC Census Gazetteer fixture validation failed: {message}")


fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
view = json.loads(VIEW_PATH.read_text(encoding="utf-8"))
jsonld = json.loads(JSONLD_PATH.read_text(encoding="utf-8"))
html = HTML_PATH.read_text(encoding="utf-8")
Draft202012Validator(schema, format_checker=FormatChecker()).validate(fixture)

records = fixture["records"]
if [row["boroughCode"] for row in records] != [1, 2, 3, 4, 5]:
    fail("expected five uniquely ordered borough-county records")
if len({row["geoid"] for row in records}) != 5:
    fail("GEOIDs are not unique")

expected_pairs = {
    f"{row['boroughName']} / {row['countyName']}": row["alandSquareMiles"]
    for row in records
}
observed_pairs = {
    row["place"]: row["censusSquareMiles"]
    for row in view["independentLandAreaComparison"]["rows"]
}
if observed_pairs != expected_pairs:
    fail("raw fixture and canonical comparison values differ")

relative_url = "/data/fixtures/nyc-census-gazetteer-county-measurements.json"
if relative_url not in html:
    fail("generated HTML does not link the fixture")
if jsonld != view["semanticRepresentation"]:
    fail("generated JSON-LD differs from the canonical artifact graph")

graph = jsonld["@graph"]
resource = next(node for node in graph if node.get("@id") == view["resource"])
if PUBLIC_URL not in {item["@id"] for item in resource["dcat:distribution"]}:
    fail("JSON-LD dataset omits the fixture distribution")
distribution = next((node for node in graph if node.get("@id") == PUBLIC_URL), None)
if not distribution or distribution.get("dcat:downloadURL", {}).get("@id") != PUBLIC_URL:
    fail("JSON-LD fixture distribution is missing or malformed")

serialized = json.dumps(fixture, ensure_ascii=False).lower()
for private_coordinate in ["knoedg/pack-nyc", "github.com/knoedg/pack-nyc", "meta-knoedg-nyc"]:
    if private_coordinate in serialized:
        fail(f"private repository coordinate leaked: {private_coordinate}")

print("Published Census Gazetteer fixture validates: schema, 5 records, HTML/JSON-LD links, comparison parity, and public safety.")
