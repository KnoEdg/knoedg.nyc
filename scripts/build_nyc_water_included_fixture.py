#!/usr/bin/env python3
"""Build the governed water-included boundary fixture from a retained DCP response."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "data/sources/nyc-boroughs-water-included-2026-08-09.geojson"
DEFAULT_OUTPUT = ROOT / "data/fixtures/nyc-boroughs-water-included.json"
EXPECTED_SOURCE_SHA256 = "5c34b9279415538081e5f1e4b6e5c8d3df5e10a2f35f6f7d94fb5c693ddb1bb2"
EXPECTED_BOROUGHS = {
    "1": "Manhattan",
    "2": "Bronx",
    "3": "Brooklyn",
    "4": "Queens",
    "5": "Staten Island",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build(source_path: Path) -> dict:
    source_sha256 = sha256(source_path)
    if source_sha256 != EXPECTED_SOURCE_SHA256:
        raise ValueError(
            f"source checksum mismatch: expected {EXPECTED_SOURCE_SHA256}, got {source_sha256}"
        )

    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source.get("type") != "FeatureCollection" or len(source.get("features", [])) != 5:
        raise ValueError("source must be a five-feature GeoJSON FeatureCollection")

    boroughs = []
    for feature in source["features"]:
        properties = feature.get("properties", {})
        code = properties.get("borocode")
        name = properties.get("boroname")
        if EXPECTED_BOROUGHS.get(code) != name:
            raise ValueError(f"unexpected borough identity: {code!r} / {name!r}")
        geometry = feature.get("geometry", {})
        if geometry.get("type") != "MultiPolygon" or not geometry.get("coordinates"):
            raise ValueError(f"{name} must contain non-empty MultiPolygon geometry")
        boroughs.append(
            {
                "order": int(code),
                "borocode": code,
                "name": name,
                "shapeAreaSquareFeet": properties.get("shape_area"),
                "shapeLengthFeet": properties.get("shape_leng"),
                "geometry": geometry,
            }
        )

    return {
        "schemaVersion": 1,
        "id": "nyc-boroughs-water-included",
        "title": "New York City borough boundaries, water included",
        "geometryRepresentation": "GeoJSON MultiPolygon coordinates",
        "sourceCrs": "EPSG:4326",
        "viewBox": "0 0 720 620",
        "source": {
            "publisher": "NYC Department of City Planning",
            "datasetTitle": "Borough Boundaries",
            "datasetId": "wh2p-dxnf",
            "variant": "water areas included",
            "datasetUrl": "https://data.cityofnewyork.us/City-Government/Borough-Boundaries/wh2p-dxnf",
            "apiRequestUrl": "https://data.cityofnewyork.us/resource/wh2p-dxnf.geojson?$limit=5000",
            "capturedAt": "2026-08-09T11:55:58Z",
            "snapshotUrl": "https://knoedg.nyc/data/sources/nyc-boroughs-water-included-2026-08-09.geojson",
            "snapshotSha256": source_sha256,
            "rightsNote": "Source attribution is retained in the public page. Review current NYC Open Data terms before redistributing beyond this repository.",
        },
        "governance": {
            "publisher": "KnoEdg.NYC",
            "publicResource": "https://knoedg.nyc/nyc-boundaries/",
            "fixtureUrl": "https://knoedg.nyc/data/fixtures/nyc-boroughs-water-included.json",
            "lifecycleState": "Active",
            "confidenceStatus": "HighConfidence",
            "confidenceValue": 0.95,
            "reviewedAt": "2026-08-09T11:55:58Z",
            "transformationNote": "The retained upstream GeoJSON response is normalized into this fixture without changing coordinates. The comparison SVG applies the fixed affine projection recorded below.",
        },
        "projection": {
            "method": "fixed affine equirectangular alignment",
            "xOffset": 18.0,
            "yOffset": 51.83053350172412,
            "minimumLongitude": -74.25559136315213,
            "maximumLatitude": 40.91553277650281,
            "scale": 1231.1407344835504,
            "decimalPlaces": 1,
            "formula": {
                "x": "xOffset + (longitude - minimumLongitude) * scale",
                "y": "yOffset + (maximumLatitude - latitude) * scale",
            },
            "alignmentNote": "The fixed values reproduce the coordinate frame of the previously published water-excluded SVG-path fixture. They were recovered from its retained 720 by 620 viewBox alignment and the current DCP water-excluded extent; they do not repair the missing historical source response or initial projection script.",
        },
        "presentation": {
            "fill": "#d8e7e8",
            "stroke": "#3f7785",
            "strokeWidth": 1.4,
            "strokeDasharray": "4 3",
            "fillRule": "evenodd",
            "strokeLinejoin": "round",
        },
        "boroughs": sorted(boroughs, key=lambda item: item["order"]),
    }


def render(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render(build(args.source))
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"{args.output} is not reproducible from {args.source}")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
