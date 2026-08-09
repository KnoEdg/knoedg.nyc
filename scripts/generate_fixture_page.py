#!/usr/bin/env python3
"""Render a complete fixture-dependent page from one public-safe artifact."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

PLACEHOLDERS = {
    "language",
    "description",
    "title",
    "canonical",
    "alternate_media_type",
    "alternate_href",
    "alternate_title",
    "stylesheet",
    "article_html",
}


def load_artifact(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 2:
        raise SystemExit("unsupported fixture-view schemaVersion")
    if data.get("artifactType") != "fixture-dependent-public-view":
        raise SystemExit("unsupported fixture-view artifactType")
    if data.get("rendererContract") != "fixture-page/v1":
        raise SystemExit("unsupported rendererContract")
    if not isinstance(data.get("semanticRepresentation"), dict):
        raise SystemExit("semanticRepresentation must be an object")
    return data


def render_template(template: str, data: dict) -> str:
    page = data["page"]
    alternate = page["alternate"]
    values = {
        "language": html.escape(page["language"], quote=True),
        "description": html.escape(page["description"], quote=True),
        "title": html.escape(page["title"]),
        "canonical": html.escape(page["canonical"], quote=True),
        "alternate_media_type": html.escape(alternate["mediaType"], quote=True),
        "alternate_href": html.escape(alternate["href"], quote=True),
        "alternate_title": html.escape(alternate["title"], quote=True),
        "stylesheet": html.escape(page["stylesheet"], quote=True),
        "article_html": page["articleHtml"],
    }
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    unresolved = {name for name in PLACEHOLDERS if "{{" + name + "}}" in template}
    if unresolved or "{{" in template or "}}" in template:
        raise SystemExit(f"unresolved template placeholders: {sorted(unresolved)}")
    return template


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


def outputs(artifact: Path, template: Path, html_path: Path, jsonld_path: Path, manifest_path: Path) -> dict[Path, str]:
    data = load_artifact(artifact)
    source = template.read_text(encoding="utf-8")
    return {
        html_path: render_template(source, data),
        jsonld_path: json.dumps(data["semanticRepresentation"], indent=2, ensure_ascii=False) + "\n",
        manifest_path: json.dumps(build_counts(data), indent=2, ensure_ascii=False) + "\n",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True, type=Path)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--jsonld", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    failed = False
    for path, rendered in outputs(args.artifact, args.template, args.html, args.jsonld, args.manifest).items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != rendered:
                print(f"stale generated output: {path}")
                failed = True
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8")
            print(f"generated {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
