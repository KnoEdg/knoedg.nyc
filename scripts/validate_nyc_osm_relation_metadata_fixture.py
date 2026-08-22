#!/usr/bin/env python3
"""Validate the published OSM relation metadata fixture and technical surfaces."""

import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "data" / "fixtures" / "nyc-openstreetmap-relation-metadata.json"
SCHEMA_PATH = ROOT / "schemas" / "nyc-openstreetmap-relation-metadata" / "v1"
VIEW_PATH = ROOT / "data" / "fixtures" / "nyc-boundaries-technical-collection.json"
HTML_PATH = ROOT / "data" / "nyc-boundaries" / "index.html"
JSONLD_PATH = ROOT / "data" / "nyc-boundaries" / "index.jsonld"
PUBLIC_URL = "https://knoedg.nyc/data/fixtures/nyc-openstreetmap-relation-metadata.json"


def fail(message: str) -> None:
    raise SystemExit(f"Published NYC OSM relation metadata fixture validation failed: {message}")


fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
view = json.loads(VIEW_PATH.read_text(encoding="utf-8"))
jsonld = json.loads(JSONLD_PATH.read_text(encoding="utf-8"))
html = HTML_PATH.read_text(encoding="utf-8")
Draft202012Validator(schema, format_checker=FormatChecker()).validate(fixture)

records = fixture["records"]
if [(row["boroughCode"], row["representation"]) for row in records] != [
    (1, "county"), (1, "borough"), (2, "county"), (2, "borough"),
    (3, "county"), (3, "borough"), (4, "county"), (4, "borough"),
    (5, "county"), (5, "borough"),
]:
    fail("records are not in deterministic borough/county-before-borough order")
if Counter(row["boroughCode"] for row in records) != Counter({1: 2, 2: 2, 3: 2, 4: 2, 5: 2}):
    fail("fixture does not contain exactly one county/borough pair per borough")
if len({row["relationId"] for row in records}) != 10 or len({row["versionUrl"] for row in records}) != 10:
    fail("relation and version identities are not unique")
for row in records:
    if row["relationUrl"] != f"https://www.openstreetmap.org/relation/{row['relationId']}":
        fail(f"relation URL mismatch for {row['relationId']}")
    if row["versionUrl"] != f"{row['relationUrl']}/history/{row['version']}":
        fail(f"version URL mismatch for {row['relationId']}")
    if row["representation"] != row["borderType"] or row["adminLevel"] != (6 if row["representation"] == "county" else 7):
        fail(f"administrative framing mismatch for {row['relationId']}")

fixture_keys = set()


def collect_keys(value: object) -> None:
    if isinstance(value, dict):
        fixture_keys.update(key.lower() for key in value)
        for child in value.values():
            collect_keys(child)
    elif isinstance(value, list):
        for child in value:
            collect_keys(child)


collect_keys(fixture)
for forbidden in {"geometry", "coordinates", "centroid", "boundingbox", "members", "lat", "lon"} & fixture_keys:
    fail(f"forbidden geometry-like field leaked: {forbidden}")
if fixture["selection"]["geometryIncluded"] is not False or fixture["selection"]["relationMembersIncluded"] is not False:
    fail("fixture does not explicitly state geometry/member absence")

if jsonld != view["semanticRepresentation"]:
    fail("generated technical JSON-LD differs from the technical artifact graph")
source_versions = {row["versionUrl"]: row["sourceModifiedAt"] for row in records}
view_versions = {
    node["@id"]: node["dcterms:modified"]["@value"]
    for node in jsonld["@graph"]
    if node.get("@id") in source_versions
}
if view_versions != source_versions:
    fail("relation versions or timestamps drift from the technical artifact")
if "/data/fixtures/nyc-openstreetmap-relation-metadata.json" not in html:
    fail("technical HTML does not link the fixture")
resource = next(node for node in jsonld["@graph"] if node.get("@id") == view["resource"])
if PUBLIC_URL not in {item["@id"] for item in resource["dcat:distribution"]}:
    fail("technical JSON-LD dataset omits the fixture distribution")
distribution = next((node for node in jsonld["@graph"] if node.get("@id") == PUBLIC_URL), None)
if not distribution or distribution.get("dcat:downloadURL", {}).get("@id") != PUBLIC_URL:
    fail("technical JSON-LD fixture distribution is missing or malformed")
if distribution.get("dcterms:license", {}).get("@id") != fixture["rights"]["licenseUrl"]:
    fail("technical JSON-LD license does not match fixture rights")

serialized = json.dumps(fixture, ensure_ascii=False).lower()
for private_coordinate in ["knoedg/pack-nyc", "github.com/knoedg/pack-nyc", "meta-knoedg-nyc"]:
    if private_coordinate in serialized:
        fail(f"private repository coordinate leaked: {private_coordinate}")

print("Published OSM metadata fixture validates: schema, 10 exact versions, no geometry, technical HTML/JSON-LD parity, rights, and public safety.")
