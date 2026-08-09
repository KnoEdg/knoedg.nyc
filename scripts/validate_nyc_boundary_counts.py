#!/usr/bin/env python3
"""Validate NYC Boundaries record-count reconciliation across public surfaces."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_DIR = ROOT / "nyc-boundaries"
MANIFEST_PATH = RESOURCE_DIR / "record-counts.json"
HTML_PATH = RESOURCE_DIR / "index.html"
JSONLD_PATH = RESOURCE_DIR / "index.jsonld"


def fail(message: str) -> None:
    raise SystemExit(f"NYC boundary count validation failed: {message}")


manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
html = HTML_PATH.read_text(encoding="utf-8")
jsonld = json.loads(JSONLD_PATH.read_text(encoding="utf-8"))

expected_total = manifest["activeRecordCount"]
groups = manifest["representations"]
computed_total = sum(group["count"] for group in groups)

if computed_total != expected_total:
    fail(
        f"manifest total is {expected_total}, but representation counts sum to "
        f"{computed_total}"
    )

html_totals = {
    int(value)
    for value in re.findall(r"(\d+) active (?:governed )?records", html)
}
if html_totals != {expected_total}:
    fail(
        f"HTML active-record totals are {sorted(html_totals)}; expected only "
        f"{expected_total}"
    )

for group in groups:
    token = f'{group["count"]} {group["label"]}'
    if token not in html:
        fail(f"HTML is missing reconciled representation token: {token!r}")

dataset = next(
    (
        node
        for node in jsonld.get("@graph", [])
        if node.get("@id") == manifest["resource"]
    ),
    None,
)
if dataset is None:
    fail(f"JSON-LD has no dataset node for {manifest['resource']}")

description = dataset.get("dcterms:description", "")
match = re.search(r"(\d+) representations", description)
if match is None or int(match.group(1)) != expected_total:
    fail(
        "JSON-LD dataset description does not contain the reconciled total "
        f"{expected_total}"
    )

print(
    f"NYC boundary counts reconcile: {expected_total} active records across "
    f"{len(groups)} representation groups."
)
