#!/usr/bin/env python3
"""Repo-wide scan for private repository coordinates in every tracked file.

The per-fixture validate_nyc_*.py scripts each scan their own generated
artifact JSON for these coordinates, but nothing previously scanned prose or
comments -- where the same coordinates leaked from README.md and a script
comment (org stocktake edition 2, Finding 7). This script covers the full
scan scope instead: every file this repository tracks.
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()

PRIVATE_COORDINATES = [
    "knoedg/pack-nyc",
    "github.com/knoedg/pack-nyc",
    "meta-knoedg-nyc",
    "docs/publications/",
]

# Allowed to name a coordinate because each exists to define a per-fixture
# leak check against it, not to disclose one -- same reasoning as SELF.
EXEMPT = {SELF, *(ROOT / "scripts").glob("validate_nyc_*.py")}


def tracked_files():
    output = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [ROOT / line for line in output.splitlines() if line]


files = tracked_files()
failures = []
for path in files:
    if path in EXEMPT or not path.is_file():
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue  # binary asset; coordinates are not embedded there as text
    lowered = text.lower()
    for coordinate in PRIVATE_COORDINATES:
        if coordinate in lowered:
            failures.append(f"{path.relative_to(ROOT)}: {coordinate}")

if failures:
    joined = "\n".join(f"  {line}" for line in failures)
    raise SystemExit(f"private repository coordinate leaked:\n{joined}")

print(f"No private repository coordinates found across {len(files)} tracked files.")
