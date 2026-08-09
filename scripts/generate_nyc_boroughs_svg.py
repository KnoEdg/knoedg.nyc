#!/usr/bin/env python3
"""Generate land-only and boundary-comparison SVGs from public fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXCLUDED_FIXTURE = ROOT / "data/fixtures/nyc-boroughs-water-excluded.json"
DEFAULT_INCLUDED_FIXTURE = ROOT / "data/fixtures/nyc-boroughs-water-included.json"
DEFAULT_OUTPUT = ROOT / "assets/nyc-boroughs.svg"
DEFAULT_COMPARISON_OUTPUT = ROOT / "assets/nyc-boundaries-comparison.svg"


def validate_boroughs(data: dict) -> list[dict]:
    boroughs = data["boroughs"]
    names = [item["name"] for item in boroughs]
    if len(boroughs) != 5 or len(set(names)) != 5:
        raise ValueError("fixture must contain exactly five uniquely named boroughs")
    return sorted(boroughs, key=lambda value: value["order"])


def render(data: dict) -> str:
    boroughs = validate_boroughs(data)
    if any(not item.get("path", "").strip() for item in boroughs):
        raise ValueError("every water-excluded borough must contain non-empty SVG path data")
    style = data["presentation"]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{data["viewBox"]}" role="img" aria-labelledby="map-title map-desc">',
        '  <title id="map-title">Land boundaries of New York City\'s five boroughs</title>',
        '  <desc id="map-desc">A simplified shoreline map of the Bronx, Brooklyn, Manhattan, Queens and Staten Island.</desc>',
        f'  <g fill="{style["fill"]}" fill-rule="{style["fillRule"]}" stroke="{style["stroke"]}" stroke-linejoin="{style["strokeLinejoin"]}" stroke-width="{style["strokeWidth"]}">',
    ]
    for item in boroughs:
        lines.append(f'  <path class="borough borough-{item["order"]}" data-borough="{item["name"]}" d="{item["path"]}"/>')
    lines.extend(["  </g>", "</svg>", ""])
    return "\n".join(lines)


def project(coordinate: list[float], projection: dict) -> tuple[float, float]:
    longitude, latitude = coordinate[:2]
    x = projection["xOffset"] + (longitude - projection["minimumLongitude"]) * projection["scale"]
    y = projection["yOffset"] + (projection["maximumLatitude"] - latitude) * projection["scale"]
    return x, y


def geometry_path(geometry: dict, projection: dict) -> str:
    if geometry.get("type") != "MultiPolygon":
        raise ValueError("water-included geometry must be a MultiPolygon")
    decimal_places = projection["decimalPlaces"]
    segments = []
    for polygon in geometry["coordinates"]:
        for ring in polygon:
            points = []
            for coordinate in ring:
                x, y = project(coordinate, projection)
                point = f"{x:.{decimal_places}f},{y:.{decimal_places}f}"
                if not points or point != points[-1]:
                    points.append(point)
            if len(points) < 3:
                raise ValueError("projected ring must contain at least three distinct points")
            segments.append("M" + " L".join(points) + " Z")
    if not segments:
        raise ValueError("water-included geometry must contain at least one ring")
    return " ".join(segments)


def style_attributes(style: dict) -> str:
    attributes = [
        f'fill="{style["fill"]}"',
        f'fill-rule="{style["fillRule"]}"',
        f'stroke="{style["stroke"]}"',
        f'stroke-linejoin="{style["strokeLinejoin"]}"',
        f'stroke-width="{style["strokeWidth"]}"',
    ]
    if style.get("strokeDasharray"):
        attributes.append(f'stroke-dasharray="{style["strokeDasharray"]}"')
    return " ".join(attributes)


def render_comparison(excluded: dict, included: dict) -> str:
    excluded_boroughs = validate_boroughs(excluded)
    included_boroughs = validate_boroughs(included)
    if [item["name"] for item in excluded_boroughs] != [item["name"] for item in included_boroughs]:
        raise ValueError("water-excluded and water-included fixtures must contain the same boroughs")

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{excluded["viewBox"]}" role="img" aria-labelledby="map-title map-desc">',
        '  <title id="map-title">Water-included and water-excluded boundaries of New York City</title>',
        '  <desc id="map-desc">A comparison map showing water-included borough boundaries in blue behind water-excluded shoreline geometry in green.</desc>',
        f'  <g class="boundary-layer water-included" data-layer="water-included" {style_attributes(included["presentation"])}>',
    ]
    for item in included_boroughs:
        path = geometry_path(item["geometry"], included["projection"])
        lines.append(f'    <path class="borough borough-{item["order"]}" data-borough="{item["name"]}" d="{path}"/>')
    lines.append("  </g>")
    lines.append(
        f'  <g class="boundary-layer water-excluded" data-layer="water-excluded" {style_attributes(excluded["presentation"])}>'
    )
    for item in excluded_boroughs:
        if not item.get("path", "").strip():
            raise ValueError("every water-excluded borough must contain non-empty SVG path data")
        lines.append(f'    <path class="borough borough-{item["order"]}" data-borough="{item["name"]}" d="{item["path"]}"/>')
    lines.extend(["  </g>", "</svg>", ""])
    return "\n".join(lines)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--excluded-fixture", type=Path, default=DEFAULT_EXCLUDED_FIXTURE)
    parser.add_argument("--included-fixture", type=Path, default=DEFAULT_INCLUDED_FIXTURE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--comparison-output", type=Path, default=DEFAULT_COMPARISON_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    excluded = json.loads(args.excluded_fixture.read_text(encoding="utf-8"))
    included = json.loads(args.included_fixture.read_text(encoding="utf-8"))
    rendered = render(excluded)
    comparison_rendered = render_comparison(excluded, included)
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"{args.output} is not reproducible from {args.excluded_fixture}")
        if not args.comparison_output.exists() or args.comparison_output.read_text(encoding="utf-8") != comparison_rendered:
            raise SystemExit(
                f"{args.comparison_output} is not reproducible from "
                f"{args.excluded_fixture} and {args.included_fixture}"
            )
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    args.comparison_output.parent.mkdir(parents=True, exist_ok=True)
    args.comparison_output.write_text(comparison_rendered, encoding="utf-8")

if __name__ == "__main__":
    main()
