# KnoEdg.NYC

This repository publishes [knoedg.nyc](https://knoedg.nyc), an early-stage public project for exploring New York City through connected, traceable public sources.

The public site is intentionally limited while the underlying work is developed and reviewed.


## Reproducible NYC boundary maps

The homepage shoreline map and the NYC Boundaries comparison overlay are generated entirely from committed public material:

- `data/fixtures/nyc-boroughs-water-excluded.json` — five reviewed, preprojected borough paths plus source and governance metadata.
- `data/sources/nyc-boroughs-water-included-2026-08-09.geojson` — retained DCP water-included API response.
- `scripts/build_nyc_water_included_fixture.py` — deterministic source-to-fixture normalization.
- `data/fixtures/nyc-boroughs-water-included.json` — five reviewed water-included GeoJSON MultiPolygons plus source, governance, and projection metadata.
- `data/fixtures/nyc-census-gazetteer-county-measurements.json` — five reviewed 2023 Census Gazetteer county records with ALAND, AWATER, internal points, source lineage, rights, and statistical-purpose limitations; no geometry.
- `data/fixtures/nyc-openstreetmap-relation-metadata.json` — ten exact OSM county/borough relation-version metadata records with stable identities, timestamps, selected administrative tags, lifecycle/confidence, provenance checksums, and ODbL attribution; no geometry, relation members, Nominatim bounds/centroids, or numeric area.
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


## NYC Boundaries generation and validation

`data/fixtures/nyc-boundary-public-view.json` is the canonical public-safe
artifact for every fixture-dependent fact and disposition on the NYC Boundaries
resource. `templates/fixture-page.html` contains only reusable site structure.
The artifact declares `fixture-page/v2` and carries authoritative
`fixture-content-blocks/v1`. The generic `scripts/generate_fixture_page.py`
renderer accepts both the frozen v1 contract and v2, renders v2 only from typed
blocks and RFC 6901 pointers, and produces the complete HTML article, JSON-LD
representation, and count manifest. None is an independent semantic source.

Regenerate and verify without network access:

```bash
python3 scripts/generate_nyc_boundaries_view.py
python3 scripts/generate_nyc_boundaries_view.py --check
python3 scripts/validate_nyc_boundary_counts.py
python3 scripts/validate_jsonld.py
python3 scripts/validate_nyc_census_gazetteer_fixture.py
python3 scripts/validate_nyc_osm_relation_metadata_fixture.py
```

The repository workflow validates the public JSON Schema, expands JSON-LD,
rejects stale generated output, and rejects disagreement between the artifact,
HTML, JSON-LD, and count manifest. Public schemas are served from
`/schemas/fixture-dependent-public-view/v1` and
`/schemas/fixture-dependent-public-view/v2`. The OSM metadata fixture schema is
served from `/schemas/nyc-openstreetmap-relation-metadata/v1`.
