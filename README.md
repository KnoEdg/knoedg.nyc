# KnoEdg.NYC

This repository publishes [knoedg.nyc](https://knoedg.nyc), an early-stage public project for exploring New York City through connected, traceable public sources.

The public site is intentionally limited while the underlying work is developed and reviewed.


## Reproducible NYC boundary maps

The homepage shoreline map and the NYC Boundaries comparison overlay are generated entirely from committed public material:

- `data/fixtures/nyc-boroughs-water-excluded.json` — five reviewed, preprojected borough paths plus source and governance metadata.
- `data/sources/nyc-boroughs-water-included-2026-08-09.geojson` — retained DCP water-included API response.
- `scripts/build_nyc_water_included_fixture.py` — deterministic source-to-fixture normalization.
- `data/fixtures/nyc-boroughs-water-included.json` — five reviewed water-included GeoJSON MultiPolygons plus source, governance, and projection metadata.
- `scripts/generate_nyc_boroughs_svg.py` — deterministic offline generator for both maps.
- `assets/nyc-boroughs.svg` — generated water-excluded presentation artifact.
- `assets/nyc-boundaries-comparison.svg` — generated water-included/water-excluded overlay.
- `data/fixtures/SHA256SUMS` — source, fixture, scripts, and output checksums.

Regenerate and verify without network access or a private repository:

```bash
python3 scripts/build_nyc_water_included_fixture.py
python3 scripts/build_nyc_water_included_fixture.py --check
python3 scripts/generate_nyc_boroughs_svg.py
python3 scripts/generate_nyc_boroughs_svg.py --check
sha256sum --check data/fixtures/SHA256SUMS
```

The fixture retains public source, review, confidence and transformation metadata without exposing private publication machinery. Its human-readable public view is [NYC Boundaries](https://knoedg.nyc/nyc-boundaries/), with a linked JSON-LD description.

The original water-excluded upstream response checksum and first projection script were not retained; that limitation is disclosed publicly. Determinism for that first publication begins at the reviewed public fixture. The later water-included publication retains the full source-to-fixture-to-overlay chain.


## NYC boundary count validation

`nyc-boundaries/record-counts.json` is the single count manifest for the public
NYC Boundaries resource. Whenever an intake changes representation coverage,
update the manifest and every affected human- and machine-readable surface
together, then run:

```bash
python3 scripts/validate_nyc_boundary_counts.py
```

The repository workflow runs the same reconciliation check for pull requests
that change the resource, manifest, validator, or workflow.
