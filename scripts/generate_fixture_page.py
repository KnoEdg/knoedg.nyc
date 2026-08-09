#!/usr/bin/env python3
"""Render fixture-page/v1 and fixture-page/v2 artifacts without network access."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

V1_SCHEMA = "https://knoedg.nyc/schemas/fixture-dependent-public-view/v1"
V2_SCHEMA = "https://knoedg.nyc/schemas/fixture-dependent-public-view/v2"
PLACEHOLDERS = {
    "language", "description", "title", "canonical", "alternate_media_type",
    "alternate_href", "alternate_title", "stylesheet", "article_html",
}


class ConformanceError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ConformanceError(message)


def resolve_pointer(document: object, pointer: str) -> object:
    require(pointer == "" or pointer.startswith("/"), f"invalid JSON Pointer: {pointer!r}")
    value = document
    if pointer == "":
        return value
    for encoded in pointer[1:].split("/"):
        require(re.sub(r"~[01]", "", encoded).find("~") == -1, f"invalid JSON Pointer escape: {pointer!r}")
        token = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict):
            require(token in value, f"unresolved JSON Pointer: {pointer!r}")
            value = value[token]
        elif isinstance(value, list):
            require(token.isdigit() and int(token) < len(value), f"unresolved JSON Pointer: {pointer!r}")
            value = value[int(token)]
        else:
            raise ConformanceError(f"JSON Pointer traverses a scalar: {pointer!r}")
    return value


def format_value(value: object, format_name: str = "text") -> str:
    if format_name == "text":
        require(isinstance(value, (str, int, float)) and not isinstance(value, bool), "text format requires a scalar")
        return str(value)
    if format_name == "integer":
        require(isinstance(value, int) and not isinstance(value, bool), "integer format requires an integer")
        return str(value)
    if format_name == "decimal":
        require(isinstance(value, (int, float)) and not isinstance(value, bool), "decimal format requires a number")
        return format(value, ".15g")
    if format_name == "percent":
        require(isinstance(value, (int, float)) and not isinstance(value, bool), "percent format requires a number")
        return f"{format(value * 100, '.15g')}%"
    if format_name == "date":
        require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value), "date format requires YYYY-MM-DD")
        return value
    if format_name == "datetime":
        require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value), "datetime format requires UTC ISO 8601 seconds")
        return value
    raise ConformanceError(f"unsupported value format: {format_name!r}")


def render_inlines(nodes: list[dict], artifact: dict) -> str:
    require(isinstance(nodes, list), "inline content must be an array")
    rendered = []
    for node in nodes:
        require(isinstance(node, dict), "inline node must be an object")
        kind = node.get("type")
        if kind == "text":
            require(set(node) == {"type", "text"} and isinstance(node["text"], str), "invalid text node")
            rendered.append(html.escape(node["text"]))
        elif kind == "value":
            require(set(node) <= {"type", "pointer", "format"} and isinstance(node.get("pointer"), str), "invalid value node")
            rendered.append(html.escape(format_value(resolve_pointer(artifact, node["pointer"]), node.get("format", "text"))))
        elif kind in {"emphasis", "strong"}:
            require(set(node) == {"type", "content"}, f"invalid {kind} node")
            tag = "em" if kind == "emphasis" else "strong"
            rendered.append(f"<{tag}>{render_inlines(node['content'], artifact)}</{tag}>")
        elif kind == "code":
            require(set(node) == {"type", "text"} and isinstance(node["text"], str), "invalid code node")
            rendered.append(f"<code>{html.escape(node['text'])}</code>")
        elif kind == "time":
            require(set(node) == {"type", "pointer", "format"}, "invalid time node")
            value = resolve_pointer(artifact, node["pointer"])
            rendered.append(f'<time datetime="{html.escape(str(value), quote=True)}">{html.escape(format_value(value, node["format"]))}</time>')
        elif kind == "link":
            require(set(node) <= {"type", "href", "content", "newWindow", "accessibleNewWindowText"}, "invalid link node")
            href = node.get("href")
            require(isinstance(href, str) and href, "link href must be non-empty")
            parsed = urlparse(href)
            require(not parsed.scheme or parsed.scheme in {"http", "https"}, "unsupported or unsafe link scheme")
            body = render_inlines(node.get("content"), artifact)
            attrs = f'href="{html.escape(href, quote=True)}"'
            if node.get("newWindow"):
                announcement = node.get("accessibleNewWindowText")
                require(isinstance(announcement, str) and announcement.strip(), "new-window link requires accessibleNewWindowText")
                accessible_name = html.unescape(re.sub(r"<[^>]+>", "", body))
                attrs += (
                    ' target="_blank" rel="noopener noreferrer"'
                    f' aria-label="{html.escape(f"{accessible_name} ({announcement})", quote=True)}"'
                )
                body += '<span aria-hidden="true"> ↗</span>'
            else:
                require("accessibleNewWindowText" not in node, "new-window text requires newWindow=true")
            rendered.append(f"<a {attrs}>{body}</a>")
        else:
            raise ConformanceError(f"unsupported inline type: {kind!r}")
    return "".join(rendered)


def render_blocks(blocks: list[dict], artifact: dict, level: int = 1, ids: set[str] | None = None) -> str:
    require(isinstance(blocks, list), "contentBlocks must be an array")
    ids = ids if ids is not None else set()
    lines = []
    for block in blocks:
        require(isinstance(block, dict), "block must be an object")
        kind = block.get("type")
        if kind == "section":
            require(set(block) == {"type", "id", "heading", "children"}, "invalid section block")
            section_id = block["id"]
            require(isinstance(section_id, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", section_id), "invalid section id")
            require(section_id not in ids, f"duplicate section id: {section_id}")
            require(level <= 6, "section nesting exceeds HTML heading levels")
            ids.add(section_id)
            heading = render_inlines(block["heading"], artifact)
            require(bool(re.sub("<[^>]+>", "", heading).strip()), "section heading must not be empty")
            children = render_blocks(block["children"], artifact, level + 1, ids)
            lines.append(f'<section aria-labelledby="{section_id}">\n<h{level} id="{section_id}">{heading}</h{level}>\n{children}\n</section>')
        elif kind == "paragraph":
            require(set(block) == {"type", "content"}, "invalid paragraph block")
            lines.append(f"<p>{render_inlines(block['content'], artifact)}</p>")
        elif kind == "definitionList":
            require(set(block) <= {"type", "label", "items"} and set(block) >= {"type", "items"}, "invalid definitionList block")
            label = f' aria-label="{html.escape(block["label"], quote=True)}"' if "label" in block else ""
            items = []
            for item in block["items"]:
                require(isinstance(item, dict) and set(item) == {"term", "description"}, "invalid definition-list item")
                items.append(f"<div><dt>{render_inlines(item['term'], artifact)}</dt><dd>{render_inlines(item['description'], artifact)}</dd></div>")
            lines.append(f"<dl{label}>\n" + "\n".join(items) + "\n</dl>")
        elif kind == "table":
            require(set(block) == {"type", "caption", "columns", "rows"}, "invalid table block")
            caption = render_inlines(block["caption"], artifact)
            require(bool(re.sub("<[^>]+>", "", caption).strip()), "table caption must not be empty")
            columns = block["columns"]
            require(isinstance(columns, list) and columns, "table requires columns")
            headers = []
            for column in columns:
                require(isinstance(column, dict) and set(column) == {"header"}, "invalid table column")
                header = render_inlines(column["header"], artifact)
                require(bool(re.sub("<[^>]+>", "", header).strip()), "table header must not be empty")
                headers.append(f'<th scope="col">{header}</th>')
            rows = []
            for row in block["rows"]:
                require(isinstance(row, list) and len(row) == len(columns), "table row width does not match columns")
                rows.append("<tr>" + "".join(f"<td>{render_inlines(cell, artifact)}</td>" for cell in row) + "</tr>")
            lines.append('<div class="table-wrap"><table>\n<caption>' + caption + "</caption>\n<thead><tr>" + "".join(headers) + "</tr></thead>\n<tbody>" + "".join(rows) + "</tbody>\n</table></div>")
        elif kind == "figure":
            require(set(block) <= {"type", "src", "alt", "decorative", "caption"} and set(block) >= {"type", "src", "caption"}, "invalid figure block")
            alt = block.get("alt", "")
            decorative = block.get("decorative", False)
            require(isinstance(alt, str) and isinstance(decorative, bool), "invalid figure accessibility fields")
            require((decorative and alt == "") or (not decorative and bool(alt.strip())), "figure requires alt text or explicit decorative=true, but not both")
            caption = render_inlines(block["caption"], artifact)
            lines.append(f'<figure><img src="{html.escape(block["src"], quote=True)}" alt="{html.escape(alt, quote=True)}"><figcaption>{caption}</figcaption></figure>')
        elif kind == "list":
            require(set(block) == {"type", "ordered", "items"} and isinstance(block["ordered"], bool), "invalid list block")
            require(isinstance(block["items"], list) and block["items"], "list must contain items")
            tag = "ol" if block["ordered"] else "ul"
            lines.append(f"<{tag}>" + "".join(f"<li>{render_inlines(item, artifact)}</li>" for item in block["items"]) + f"</{tag}>")
        else:
            raise ConformanceError(f"unsupported block type: {kind!r}")
    return "\n".join(lines)


def render_article(data: dict) -> str:
    return "<article>\n" + render_blocks(data["page"]["contentBlocks"], data) + "\n</article>"


def load_artifact(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(data.get("artifactType") == "fixture-dependent-public-view", "unsupported fixture-view artifactType")
    require(isinstance(data.get("semanticRepresentation"), dict), "semanticRepresentation must be an object")
    if data.get("schema") == V1_SCHEMA:
        require(data.get("schemaVersion") == 2 and data.get("rendererContract") == "fixture-page/v1", "invalid fixture-page/v1 identity")
        require(isinstance(data.get("page", {}).get("articleHtml"), str), "v1 requires articleHtml")
    elif data.get("schema") == V2_SCHEMA:
        require(data.get("schemaVersion") == 1 and data.get("rendererContract") == "fixture-page/v2", "invalid fixture-page/v2 identity")
        require(data.get("contentModel") == "fixture-content-blocks/v1", "unsupported v2 content model")
        projected = render_article(data)
        if "articleHtml" in data["page"]:
            require(data["page"]["articleHtml"] == projected, "v2 articleHtml compatibility projection differs from contentBlocks")
    else:
        raise ConformanceError("unsupported fixture-view schema")
    return data


def render_template(template: str, data: dict) -> str:
    page = data["page"]
    alternate = page["alternate"]
    article = page["articleHtml"] if data["rendererContract"] == "fixture-page/v1" else render_article(data)
    values = {
        "language": html.escape(page["language"], quote=True),
        "description": html.escape(page["description"], quote=True),
        "title": html.escape(page["title"]),
        "canonical": html.escape(page["canonical"], quote=True),
        "alternate_media_type": html.escape(alternate["mediaType"], quote=True),
        "alternate_href": html.escape(alternate["href"], quote=True),
        "alternate_title": html.escape(alternate["title"], quote=True),
        "stylesheet": html.escape(page["stylesheet"], quote=True),
        "article_html": article,
    }
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    unresolved = {name for name in PLACEHOLDERS if "{{" + name + "}}" in template}
    require(not unresolved and "{{" not in template and "}}" not in template, f"unresolved template placeholders: {sorted(unresolved)}")
    return template


def build_counts(data: dict) -> dict:
    return {
        "schemaVersion": data["schemaVersion"],
        "schema": data["schema"],
        "rendererContract": data["rendererContract"],
        "resource": data["resource"],
        "activeRecordCount": data["activeRecordCount"],
        "representations": [
            {"id": group["id"], "label": group["label"], "count": group["count"], "provenanceCluster": group["provenanceCluster"]}
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
    try:
        generated = outputs(args.artifact, args.template, args.html, args.jsonld, args.manifest)
    except (ConformanceError, KeyError, TypeError) as exc:
        raise SystemExit(f"fixture-page conformance failed: {exc}")
    failed = False
    for path, rendered in generated.items():
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
