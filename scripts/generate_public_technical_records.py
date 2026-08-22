#!/usr/bin/env python3
"""Materialize local technical records declared by a public-safe artifact.

The artifact remains semantic authority. This script only projects JSON-LD graph
nodes whose @id is already a stable KnoEdg.NYC `/data/.../assertions/*.json` or
`/data/.../sources/*.json` URI into matching files in the public tree.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

SITE_ORIGIN = "https://knoedg.nyc"
ALLOWED_RECORD_SEGMENTS = {"assertions", "sources"}


class TechnicalRecordError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TechnicalRecordError(message)


def record_path(root: Path, uri: str, collection_resource: str) -> Path:
    require(uri.startswith(collection_resource), f"record URI escapes collection: {uri}")
    parsed = urlparse(uri)
    require(f"{parsed.scheme}://{parsed.netloc}" == SITE_ORIGIN, f"record URI is not KnoEdg.NYC-local: {uri}")
    require(parsed.query == "" and parsed.fragment == "", f"record URI must be a concrete file URI: {uri}")
    require(parsed.path.endswith(".json"), f"technical record must end in .json: {uri}")
    relative = Path(parsed.path.lstrip("/"))
    parts = relative.parts
    require("data" in parts, f"technical record is outside /data/: {uri}")
    segment = parts[-2] if len(parts) >= 2 else ""
    require(segment in ALLOWED_RECORD_SEGMENTS, f"unsupported technical-record segment {segment!r}: {uri}")
    return root / relative


def generated_records(root: Path, artifact_path: Path) -> dict[Path, str]:
    data = json.loads(artifact_path.read_text(encoding="utf-8"))
    resource = data.get("resource")
    require(isinstance(resource, str) and resource.startswith(f"{SITE_ORIGIN}/data/"), "artifact resource must be a KnoEdg.NYC /data/ URI")
    semantic = data.get("semanticRepresentation")
    require(isinstance(semantic, dict), "semanticRepresentation must be an object")
    context = semantic.get("@context")
    graph = semantic.get("@graph")
    require(isinstance(context, dict), "semanticRepresentation.@context must be an object")
    require(isinstance(graph, list), "semanticRepresentation.@graph must be an array")

    by_id: dict[str, dict] = {}
    for node in graph:
        if not isinstance(node, dict):
            continue
        identifier = node.get("@id")
        if isinstance(identifier, str):
            require(identifier not in by_id, f"duplicate JSON-LD node identity: {identifier}")
            by_id[identifier] = node

    record_ids = sorted(
        identifier for identifier in by_id
        if identifier.startswith(resource)
        and any(f"/{segment}/" in identifier for segment in ALLOWED_RECORD_SEGMENTS)
    )
    require(record_ids, "technical collection declares no local assertion/source records")

    # Any local assertion/source reference is required to resolve to a graph
    # node, which will in turn be materialized to a concrete file below.
    def walk(value: object) -> None:
        if isinstance(value, dict):
            ref = value.get("@id")
            if isinstance(ref, str) and ref.startswith(resource) and any(
                f"/{segment}/" in ref for segment in ALLOWED_RECORD_SEGMENTS
            ):
                require(ref in by_id, f"unresolved local technical reference: {ref}")
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(semantic)

    produced: dict[Path, str] = {}
    for identifier in record_ids:
        path = record_path(root, identifier, resource)
        document = {"@context": context, **by_id[identifier]}
        serialized = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
        lowered = serialized.lower()
        require("knoedg/pack-nyc" not in lowered, f"private pack coordinate leaked into {identifier}")
        require("meta-knoedg-nyc" not in lowered, f"private control-tower coordinate leaked into {identifier}")
        produced[path] = serialized
    return produced


def materialize(root: Path, artifact_path: Path, *, check: bool = False) -> int:
    try:
        produced = generated_records(root, artifact_path)
    except (OSError, json.JSONDecodeError, TechnicalRecordError) as exc:
        raise SystemExit(f"technical-record generation failed: {exc}")

    failed = False
    for path, rendered in produced.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != rendered:
                print(f"stale generated technical record: {path}")
                failed = True
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8")
            print(f"generated {path}")
    return 1 if failed else 0
