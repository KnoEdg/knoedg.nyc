#!/usr/bin/env python3
"""Generate fixture-derived NYC Boundaries public surfaces from one artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT / "data" / "fixtures" / "nyc-boundary-public-view.json"
HTML_PATH = ROOT / "nyc-boundaries" / "index.html"
JSONLD_PATH = ROOT / "nyc-boundaries" / "index.jsonld"
COUNTS_PATH = ROOT / "nyc-boundaries" / "record-counts.json"
BEGIN = "<!-- BEGIN GENERATED: measurement-disposition -->"
END = "<!-- END GENERATED: measurement-disposition -->"

CLAIM_IDS = {
    "dcp": "https://knoedg.nyc/nyc-boundaries/#dcp-water-excluded",
    "census-gazetteer": "https://knoedg.nyc/nyc-boundaries/#census-county",
    "openstreetmap": "https://knoedg.nyc/nyc-boundaries/#osm-administrative",
    "geoboundaries": "https://knoedg.nyc/nyc-boundaries/#geoboundaries-adm2",
    "overture": "https://knoedg.nyc/nyc-boundaries/#overture-divisions",
    "whos-on-first": "https://knoedg.nyc/nyc-boundaries/#whos-on-first-counties",
}

def replace_region(text: str, rendered: str) -> str:
    start = text.find(BEGIN)
    finish = text.find(END)
    if start < 0 or finish < 0 or finish < start:
        raise SystemExit("generated measurement-disposition markers are missing")
    finish += len(END)
    return text[:start] + BEGIN + "\n" + rendered + "\n        " + END + text[finish:]

def render_measurement_section(data: dict) -> str:
    comparison = data["independentLandAreaComparison"]
    rows = "\n".join(
        f'                <tr><td>{row["place"]}</td><td>{row["dcpSquareMiles"]:.3f}</td>'
        f'<td>{row["censusSquareMiles"]:.3f}</td><td>{row["differencePercent"]:.2f}%</td></tr>'
        for row in comparison["rows"]
    )
    dispositions = []
    for group in data["sourceGroups"]:
        measurement = group["measurement"]
        availability = (
            f'Available · {measurement["status"]}'
            if measurement["numericAreaAvailable"]
            else "No numeric area in reviewed source record"
        )
        metric = measurement["metric"] or "—"
        disposition = (
            "Included"
            if measurement["comparisonDisposition"] == "included"
            else "Excluded"
        )
        dispositions.append(
            f"                <tr><td>{group['label']}</td><td>{availability}</td>"
            f"<td>{metric}</td><td>{disposition}</td><td>{measurement['reason']}</td></tr>"
        )
    wof_rows = "\n".join(
        f'                <tr><td>{row["place"]}</td><td>{row["wofId"]}</td>'
        f'<td>{row["squareMeters"]:,.6f}</td></tr>'
        for row in data["whosOnFirstGeometricAreas"]
    )
    return f'''        <section aria-labelledby="agreement">
          <h2 id="agreement">{comparison["heading"]}</h2>
          <p>{comparison["assessment"]}</p>
          <div class="table-wrap">
            <table class="numeric">
              <thead>
                <tr><th>Borough / county</th><th>DCP land shape<br><span>sq mi</span></th><th>Census land<br><span>sq mi</span></th><th>Difference</th></tr>
              </thead>
              <tbody>
{rows}
              </tbody>
            </table>
          </div>
          <h3>Measurement availability and comparison disposition</h3>
          <div class="table-wrap">
            <table>
              <thead><tr><th>Source group</th><th>Numeric area availability</th><th>Metric</th><th>Land-area table</th><th>Governed reason</th></tr></thead>
              <tbody>
{chr(10).join(dispositions)}
              </tbody>
            </table>
          </div>
          <p class="annotation">Measurement availability and source independence are separate. A numeric field can be available yet excluded because its metric or provenance is not comparable; geometry without a numeric area requires a separate governed calculation before comparison.</p>
          <h3>Who's On First geometric-area fields</h3>
          <p>All five WOF records supply <code>geom:area_square_m</code>. WOF documents these as Shapely-derived geometric areas. Because the underlying geometry is Census-sourced Quattroshapes and the metric is not land-only, these values are governed and shown here but excluded from the independent land-area table.</p>
          <div class="table-wrap">
            <table class="numeric">
              <thead><tr><th>Borough / county</th><th>WOF ID</th><th><code>geom:area_square_m</code></th></tr></thead>
              <tbody>
{wof_rows}
              </tbody>
            </table>
          </div>
        </section>'''

def build_counts(data: dict) -> dict:
    return {
        "schemaVersion": data["schemaVersion"],
        "resource": data["resource"],
        "activeRecordCount": data["activeRecordCount"],
        "representations": [
            {
                "id": group["id"],
                "label": group["label"],
                "count": group["count"],
                "provenanceCluster": group["provenanceCluster"],
            }
            for group in data["sourceGroups"]
        ],
    }

def build_jsonld(data: dict, current: dict) -> dict:
    nodes = {node.get("@id"): node for node in current.get("@graph", [])}
    for group in data["sourceGroups"]:
        node = nodes.get(CLAIM_IDS[group["id"]])
        if node is None:
            raise SystemExit(f"JSON-LD claim missing for {group['id']}")
        measurement = group["measurement"]
        properties = [
            prop for prop in node.get("schema:additionalProperty", [])
            if prop.get("schema:name") not in {
                "Numeric area availability",
                "Measurement semantics",
                "Independent land-area comparison disposition",
                "Source-supplied geometric areas",
            }
        ]
        properties.extend([
            {
                "@type": "schema:PropertyValue",
                "schema:name": "Numeric area availability",
                "schema:value": measurement["status"],
            },
            {
                "@type": "schema:PropertyValue",
                "schema:name": "Measurement semantics",
                "schema:value": measurement["reason"],
            },
            {
                "@type": "schema:PropertyValue",
                "schema:name": "Independent land-area comparison disposition",
                "schema:value": measurement["comparisonDisposition"],
            },
        ])
        if group["id"] == "whos-on-first":
            properties.append({
                "@type": "schema:PropertyValue",
                "schema:name": "Source-supplied geometric areas",
                "schema:value": "; ".join(
                    f'{row["wofId"]}: {row["squareMeters"]:.6f} m²'
                    for row in data["whosOnFirstGeometricAreas"]
                ),
            })
        node["schema:additionalProperty"] = properties
    return current

def generate() -> dict[Path, str]:
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    html = HTML_PATH.read_text(encoding="utf-8")
    jsonld = json.loads(JSONLD_PATH.read_text(encoding="utf-8"))
    return {
        HTML_PATH: replace_region(html, render_measurement_section(data)),
        JSONLD_PATH: json.dumps(build_jsonld(data, jsonld), indent=2, ensure_ascii=False) + "\n",
        COUNTS_PATH: json.dumps(build_counts(data), indent=2, ensure_ascii=False) + "\n",
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    failed = False
    for path, generated in generate().items():
        current = path.read_text(encoding="utf-8")
        if args.check:
            if current != generated:
                print(f"stale generated output: {path.relative_to(ROOT)}")
                failed = True
        else:
            path.write_text(generated, encoding="utf-8")
            print(f"generated {path.relative_to(ROOT)}")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
