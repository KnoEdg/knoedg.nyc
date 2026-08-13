#!/usr/bin/env python3
"""Positive and negative fixture-page renderer conformance vectors."""

import copy
import json
from pathlib import Path

from generate_fixture_page import ConformanceError, format_value, load_artifact, render_article, render_inlines

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

# KnoEdg.NYC displays instant text in America/New_York local time; the
# <time datetime="..."> machine attribute must still carry the exact UTC
# instant unchanged. This UTC value crosses a calendar-day boundary in ET
# (03:55 UTC on the 10th is 23:55 EDT on the 9th) -- deliberately chosen so a
# regression to raw-UTC display would be caught by a wrong displayed date,
# not just a wrong hour.
if format_value("2026-08-10T03:55:38Z", "datetime") != "August 9, 2026, 11:55 PM EDT":
    raise SystemExit(f"datetime format did not localize to America/New_York ET: {format_value('2026-08-10T03:55:38Z', 'datetime')!r}")
time_artifact = {"foo": "2026-08-10T03:55:38Z"}
time_html = render_inlines([{"type": "time", "pointer": "/foo", "format": "datetime"}], time_artifact)
if time_html != '<time datetime="2026-08-10T03:55:38Z">August 9, 2026, 11:55 PM EDT</time>':
    raise SystemExit(f"time node did not preserve UTC datetime attribute while localizing display text: {time_html!r}")

# Per the governing ADR-0006: date-only values render human-readable text,
# not a raw ISO string, and never gain a fabricated time.
if format_value("2023-12-12", "date") != "December 12, 2023":
    raise SystemExit(f"date format did not render human-readable text: {format_value('2023-12-12', 'date')!r}")
date_artifact = {"foo": "2023-12-12"}
date_html = render_inlines([{"type": "time", "pointer": "/foo", "format": "date"}], date_artifact)
if date_html != '<time datetime="2023-12-12">December 12, 2023</time>':
    raise SystemExit(f"date-format time node did not preserve ISO date attribute while rendering human-readable text: {date_html!r}")

print("Renderer conformance passes: v1 compatibility, v2 blocks, unknown schema, pointer, raw HTML, projection drift, ET localization, date-only formatting.")
