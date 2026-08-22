#!/usr/bin/env python3
"""Validate public provenance references structurally.

Rules:
- public local assertion/source references must resolve to generated files;
- fixture-dependent public artifacts must not expose the old unpublished
  knoedg.org/nyc-knowledge-pack assertion-metadata namespace as public evidence;
- private pack/control-tower coordinates remain forbidden as defense in depth.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE_ORIGIN = "https://knoedg.nyc"
LOCAL_TECHNICAL = re.compile(r"^https://knoedg\.nyc/data/.+/(?:assertions|sources)/[^/#?]+\.json$")
OLD_ASSERTION_REFERENCE = "https://knoedg.org/nyc-knowledge-pack/assertion-metadata-"
PRIVATE_MARKERS = (
    "github.com/knoedg/pack-nyc",
    "github.com/knoedg/meta-knoedg-nyc",
    "knoedg/pack-nyc",
    "knoedg/meta-knoedg-nyc",
)

ARTIFACTS = (
    ROOT / "data/fixtures/30-immigrant-enclaves-map-technical-collection.json",
    ROOT / "data/fixtures/nyc-immigrant-enclaves-data-paper.json",
)
GENERATED_SURFACES = (
    ROOT / "data/30-immigrant-enclaves-map/index.html",
    ROOT / "data/30-immigrant-enclaves-map/index.jsonld",
)


def fail(message: str) -> None:
    raise SystemExit(f"public provenance validation failed: {message}")


def path_for_local_uri(uri: str) -> Path:
    parsed = urlparse(uri)
    if f"{parsed.scheme}://{parsed.netloc}" != SITE_ORIGIN:
        fail(f"expected KnoEdg.NYC-local URI: {uri}")
    if parsed.query or parsed.fragment:
        fail(f"technical record URI must be a concrete path, not query/fragment: {uri}")
    return ROOT / parsed.path.lstrip("/")


def walk_strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_strings(child)


def validate_text(text: str, origin: str) -> set[str]:
    lowered = text.lower()
    if OLD_ASSERTION_REFERENCE in lowered:
        fail(f"unpublished assertion-metadata URI exposed by {origin}")
    for marker in PRIVATE_MARKERS:
        if marker in lowered:
            fail(f"private repository coordinate exposed by {origin}: {marker}")
    return set(re.findall(r"https://knoedg\.nyc/data/[^\s\"'<>]+/(?:assertions|sources)/[^\s\"'<>]+\.json", text))


def validate_json(path: Path) -> set[str]:
    if not path.exists():
        fail(f"required artifact is missing: {path.relative_to(ROOT)}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")

    refs: set[str] = set()
    for value in walk_strings(data):
        refs |= validate_text(value, str(path.relative_to(ROOT)))
        if LOCAL_TECHNICAL.match(value):
            refs.add(value)
    return refs


def main() -> int:
    refs: set[str] = set()
    for artifact in ARTIFACTS:
        refs |= validate_json(artifact)

    for surface in GENERATED_SURFACES:
        if not surface.exists():
            fail(f"required generated surface is missing: {surface.relative_to(ROOT)}")
        refs |= validate_text(surface.read_text(encoding="utf-8"), str(surface.relative_to(ROOT)))

    if not refs:
        fail("no local assertion/source references found; provenance chain is not wired")

    for uri in sorted(refs):
        if not LOCAL_TECHNICAL.match(uri):
            fail(f"malformed local technical provenance URI: {uri}")
        target = path_for_local_uri(uri)
        if not target.is_file():
            fail(f"local provenance URI has no generated target: {uri} -> {target.relative_to(ROOT)}")
        validate_json(target)

    print(f"public provenance validates: {len(refs)} local assertion/source references resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
