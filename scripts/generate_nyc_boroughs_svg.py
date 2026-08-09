#!/usr/bin/env python3
"""Generate the NYC borough SVG from the committed public fixture only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "data/fixtures/nyc-boroughs-water-excluded.json"
DEFAULT_OUTPUT = ROOT / "assets/nyc-boroughs.svg"

def render(data: dict) -> str:
    boroughs = data["boroughs"]
    names = [item["name"] for item in boroughs]
    if len(boroughs) != 5 or len(set(names)) != 5:
        raise ValueError("fixture must contain exactly five uniquely named boroughs")
    if any(not item["path"].strip() for item in boroughs):
        raise ValueError("every borough must contain non-empty SVG path data")
    style = data["presentation"]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{data["viewBox"]}" role="img" aria-labelledby="map-title map-desc">',
        '  <title id="map-title">Land boundaries of New York City\'s five boroughs</title>',
        '  <desc id="map-desc">A simplified shoreline map of the Bronx, Brooklyn, Manhattan, Queens and Staten Island.</desc>',
        f'  <g fill="{style["fill"]}" fill-rule="{style["fillRule"]}" stroke="{style["stroke"]}" stroke-linejoin="{style["strokeLinejoin"]}" stroke-width="{style["strokeWidth"]}">',
    ]
    for item in sorted(boroughs, key=lambda value: value["order"]):
        lines.append(f'  <path class="borough borough-{item["order"]}" data-borough="{item["name"]}" d="{item["path"]}"/>')
    lines.extend(["  </g>", "</svg>", ""])
    return "\n".join(lines)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render(json.loads(args.fixture.read_text(encoding="utf-8")))
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"{args.output} is not reproducible from {args.fixture}")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")

if __name__ == "__main__":
    main()
