#!/usr/bin/env python3
"""Positive and negative fixture-page renderer conformance vectors."""

import copy
import json
from pathlib import Path

from generate_fixture_page import ConformanceError, load_artifact, render_article

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "tests/fixture-page-v1.json"
V2 = ROOT / "data/fixtures/nyc-boundary-public-view.json"

v1 = load_artifact(V1)
if v1["page"]["articleHtml"] != "<article><h1>Example</h1><p>One governed record.</p></article>":
    raise SystemExit("v1 trusted article compatibility failed")

v2 = load_artifact(V2)
projected = render_article(v2)
if not projected.startswith("<article>\n<section") or projected.count("<h1 ") != 1:
    raise SystemExit("v2 block rendering failed")


def must_fail(candidate: dict, expected: str) -> None:
    path = ROOT / "tests/.fixture-page-negative.tmp.json"
    try:
        path.write_text(json.dumps(candidate), encoding="utf-8")
        try:
            load_artifact(path)
        except ConformanceError as exc:
            if expected not in str(exc):
                raise SystemExit(f"expected {expected!r}, got {str(exc)!r}")
        else:
            raise SystemExit(f"negative vector did not fail: {expected}")
    finally:
        path.unlink(missing_ok=True)


broken = copy.deepcopy(v2)
broken["schema"] = "https://knoedg.nyc/schemas/fixture-dependent-public-view/v99"
must_fail(broken, "unsupported fixture-view schema")

broken = copy.deepcopy(v2)
broken["page"]["contentBlocks"][0]["children"][0]["content"] = [{"type": "value", "pointer": "/missing"}]
must_fail(broken, "unresolved JSON Pointer")

broken = copy.deepcopy(v2)
broken["page"]["contentBlocks"][0]["children"].append({"type": "rawHtml", "html": "<script>alert(1)</script>"})
must_fail(broken, "unsupported block type")

broken = copy.deepcopy(v2)
broken["page"]["articleHtml"] = projected + "<!-- drift -->"
must_fail(broken, "compatibility projection differs")

print("Renderer conformance passes: v1 compatibility, v2 blocks, unknown schema, pointer, raw HTML, projection drift.")
