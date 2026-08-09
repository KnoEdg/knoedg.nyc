#!/usr/bin/env python3
"""Validate v2 ownership, parity, accessibility and deterministic output."""

import html
import json
import re
from pathlib import Path

from generate_fixture_page import load_artifact, render_article

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/fixtures/nyc-boundary-public-view.json"
TEMPLATE = ROOT / "templates/fixture-page.html"
HTML = ROOT / "nyc-boundaries/index.html"
JSONLD = ROOT / "nyc-boundaries/index.jsonld"
MANIFEST = ROOT / "nyc-boundaries/record-counts.json"


def fail(message: str) -> None:
    raise SystemExit(f"fixture-page ownership validation failed: {message}")


data = load_artifact(ARTIFACT)
template = TEMPLATE.read_text(encoding="utf-8")
rendered = HTML.read_text(encoding="utf-8")
jsonld = json.loads(JSONLD.read_text(encoding="utf-8"))
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
article = render_article(data)

if data.get("schemaVersion") != 1 or data.get("rendererContract") != "fixture-page/v2":
    fail("artifact does not declare fixture-page/v2 schema version 1")
if data.get("contentModel") != "fixture-content-blocks/v1":
    fail("artifact does not declare fixture-content-blocks/v1")
if "articleHtml" in data["page"]:
    fail("v2 source must not carry an independently authored articleHtml")
if rendered.count("<article>") != 1 or article not in rendered:
    fail("normative content-block rendering is not present exactly once")
if jsonld != data["semanticRepresentation"]:
    fail("JSON-LD is not the artifact-owned semantic representation")
groups = data["sourceGroups"]
if sum(group["count"] for group in groups) != data["activeRecordCount"]:
    fail("source-group counts do not reconcile")
if manifest["activeRecordCount"] != data["activeRecordCount"]:
    fail("manifest total disagrees with artifact")
if manifest["schema"] != data["schema"] or manifest["rendererContract"] != data["rendererContract"]:
    fail("manifest omits the exact v2 contract identity")
visible_article = html.unescape(article)
for group in groups:
    if group["label"] not in visible_article:
        fail(f"article does not expose source group {group['id']}")
for forbidden in [data["page"]["title"], str(data["activeRecordCount"]), *[g["label"] for g in groups]]:
    if forbidden in template:
        fail(f"template independently contains fixture content: {forbidden}")
if "BEGIN GENERATED" in rendered or "END GENERATED" in rendered:
    fail("partial-generation markers remain in the complete generated page")
if "<h1 " not in article or article.count("<h1 ") != 1:
    fail("v2 article must expose exactly one h1")
if not re.search(r"<table>\s*<caption>.+?</caption>\s*<thead><tr><th scope=\"col\">", article, re.S):
    fail("v2 tables must expose captions and scoped column headers")
if 'target="_blank"' in article and 'rel="noopener noreferrer"' not in article:
    fail("new-window links are missing safe relationship attributes")
if 'target="_blank"' in article and 'class="visually-hidden"> opens in a new tab' not in article:
    fail("new-window links are missing assistive announcements")

graph = data["semanticRepresentation"].get("@graph")
if not isinstance(graph, list) or not graph:
    fail("semanticRepresentation has no @graph")
ids = [node.get("@id") for node in graph if isinstance(node, dict)]
if any(not isinstance(identifier, str) or not identifier.startswith("https://") for identifier in ids):
    fail("JSON-LD graph nodes require stable HTTPS identifiers")
if data["resource"] not in ids:
    fail("public resource identity is absent from the JSON-LD graph")
resource_node = next(node for node in graph if node.get("@id") == data["resource"])
if resource_node.get("dcat:landingPage", {}).get("@id") != data["page"]["canonical"]:
    fail("HTML canonical and JSON-LD landing-page identity disagree")

serialized = json.dumps(data, ensure_ascii=False).lower()
for private_coordinate in ["knoedg/pack-nyc", "github.com/knoedg/pack-nyc", "meta-knoedg-nyc", "docs/publications/"]:
    if private_coordinate in serialized:
        fail(f"private repository coordinate leaked: {private_coordinate}")

print(f"Fixture page v2 is artifact-generated: {data['activeRecordCount']} records, {len(groups)} groups, blocks + HTML + expanded JSON-LD gate + manifest.")
