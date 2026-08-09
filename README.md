# KnoEdg.NYC

This repository publishes [knoedg.nyc](https://knoedg.nyc), an early-stage public project for exploring New York City through connected, traceable public sources.

The public site is intentionally limited while the underlying work is developed and reviewed.


## Reproducible NYC boundary map

The homepage map is generated entirely from the committed, public-safe fixture:

- `data/fixtures/nyc-boroughs-water-excluded.json` — five reviewed, preprojected borough paths plus source and governance metadata.
- `scripts/generate_nyc_boroughs_svg.py` — deterministic offline generator.
- `assets/nyc-boroughs.svg` — generated presentation artifact.
- `data/fixtures/SHA256SUMS` — fixture, generator, and output checksums.

Regenerate and verify without network access or a private repository:

```bash
python3 scripts/generate_nyc_boroughs_svg.py
python3 scripts/generate_nyc_boroughs_svg.py --check
sha256sum --check data/fixtures/SHA256SUMS
```

The fixture retains public source, review, confidence and transformation metadata without exposing private publication machinery. Its human-readable public view is [NYC Boundaries](https://knoedg.nyc/nyc-boundaries/), with a linked JSON-LD description.

The original upstream response checksum and first projection script were not retained; that limitation is disclosed publicly. Determinism begins at the reviewed public fixture for this first publication.
