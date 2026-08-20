# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

This repository **is** the published site at [knoedg.nyc](https://knoedg.nyc) — a static, GitHub Pages-served public project for exploring New York City through connected, traceable public sources. There is no build step and no framework: `index.html`, `.nojekyll`, `CNAME`, `sitemap.xml`, and per-resource directories are the site.

It is deliberately limited in scope while the underlying work is developed and reviewed elsewhere. **This repository is the publication surface, not the governance layer.** It does not curate, decide what is eligible to publish, or hold the upstream corpus.

## The Central Rule

**Every fixture-dependent public page is generated. Nothing about it is hand-edited.**

```text
data/fixtures/*-public-view.json   ← the authored, public-safe artifact — the single source
        ↓  scripts/generate_*.py   ← thin renderers over scripts/generate_fixture_page.py
index.html · index.jsonld · count manifest
```

- The artifact is **authored**. The page, JSON-LD, and manifest are **rendered from it**.
- `templates/fixture-page.html` contains **only reusable site structure** — never a fact.
- **None of the generated outputs is an independent semantic source.** If a fact appears in the HTML, it came from the artifact; if it disagrees with the artifact, the HTML is wrong.
- Never write prose into a page that duplicates a fact the JSON-LD already carries.

To change what a page says, **change the artifact and regenerate.** Editing generated HTML will be caught by `--check` and will fail CI.

## Development Commands

No dependencies beyond the standard library, except CI's pinned `jsonschema==4.25.0` and `PyLD==2.0.4`. **Everything runs offline.**

```bash
# Regenerate, or verify nothing is stale (--check)
python3 scripts/generate_nyc_boundaries_view.py --check
python3 scripts/generate_nyc_dcp_source_view.py --check
python3 scripts/generate_nyc_census_gazetteer_source_view.py --check
python3 scripts/generate_nyc_openstreetmap_source_view.py --check
python3 scripts/generate_nyc_whos_on_first_source_view.py --check
python3 scripts/generate_nyc_geoboundaries_source_view.py --check
python3 scripts/generate_nyc_overture_source_view.py --check

# Maps
python3 scripts/build_nyc_water_included_fixture.py --check
python3 scripts/generate_nyc_boroughs_svg.py --check

# Validators
python3 scripts/test_fixture_page_renderer.py
python3 scripts/validate_no_private_coordinates.py
python3 scripts/validate_nyc_boundary_counts.py
python3 scripts/validate_jsonld.py
python3 scripts/validate_nyc_census_gazetteer_fixture.py
python3 scripts/validate_nyc_osm_relation_metadata_fixture.py
python3 scripts/validate_nyc_geoboundaries_fixture.py
python3 scripts/validate_nyc_whos_on_first_fixture.py
python3 scripts/validate_nyc_overture_fixture.py

sha256sum --check data/fixtures/SHA256SUMS
```

**Run the full set before pushing.** `.github/workflows/validate-nyc-boundary-counts.yml` runs all of it plus JSON Schema validation and JSON-LD expansion, and its `paths:` filters are explicit — **a new fixture, script, or schema must be added to both the `pull_request` and `push` lists**, or it silently escapes CI.

## Architecture

- `data/fixtures/` — authored public-safe artifacts and reviewed source fixtures, plus `SHA256SUMS` over sources, fixtures, scripts, and outputs.
- `data/sources/` — retained upstream responses.
- `scripts/generate_fixture_page.py` — the shared renderer. `generate_nyc_*_source_view.py` are thin wrappers with **no page-specific rendering logic**; keep it that way.
- `schemas/` — served publicly at `/schemas/...`. `fixture-dependent-public-view/v1` is a **frozen contract**; `v2` renders only from typed blocks and RFC 6901 pointers.
- `templates/`, `tests/fixture-page-v1.json`, `assets/`.
- Resource directories (`nyc-boundaries/`, `nyc-dcp-borough-boundaries/`, `nyc-census-gazetteer/`, `nyc-openstreetmap/`, `nyc-whos-on-first/`, `nyc-geoboundaries/`, `nyc-overture/`) hold **generated output only.**

Each source page carries the same nine canonical sections — Publisher, Dataset, measurements, Rights, Published material, Validation, Governance, Limitations, Publication history — and the same JSON-LD shape: claim-level lifecycle and confidence, `dcterms:provenance`, and `prov:Activity`-backed publication history.

## Key Constraints

- **No private coordinates in any tracked file.** `scripts/validate_no_private_coordinates.py` scans **every file this repository tracks** — prose and comments included, not just generated JSON — because that is exactly where they leaked before. Never name an upstream private repository, path, branch, or pull request anywhere here, including in this file.
- **This repository does not decide what gets published.** Eligibility and curation are governed upstream, and an upstream process is explicitly barred from writing here automatically after that happened once and had to be reverted. A change here needs a human authorizing *that change*.
- **Rights and limitations are published, not omitted.** Attribution requirements (ODbL, CC BY 4.0, WOF/Quattroshapes) and known limitations travel with the data. The unretained water-excluded upstream checksum is disclosed publicly rather than quietly dropped — **when provenance is incomplete, say so on the page.**
- **Time rendering:** displayed instants render in `America/New_York`; the underlying `<time datetime="...">` always keeps the original UTC instant unchanged. **A value the source recorded only as a calendar date is never given a fabricated time.**
- **Visitor navigation is internal-first.** Prefer an internal fixture page or knowledge resource over a direct external link. A direct external link is a transitional fallback: new tab, safe `rel`, visible and assistive indication, and it stays recorded in provenance after an internal page replaces it.
- **Branch naming: `<type>/<slug>`, always** — Conventional Commits type plus a kebab-case description. Never a harness-generated name like `claude/<random>`, and never named after the agent, model, or session that produced the work. See `knoedg/meta-knoedg`'s `docs/conventions/branch-naming.md`.
- **Extraction before summary** — record what a source actually says and what a query actually returned, verbatim and separately from any summary that interprets it. **A negative result states its query, or it is not a finding**; check first whether that query could have returned a positive at all. Never resolve a referent, a name, or a tool's semantics from memory — if a source names a category, record the category; if it names no one, no one is named. See `knoedg/meta-knoedg`'s `docs/conventions/extraction-before-summary.md`.
  This is the public surface, so it binds hardest here: a summary that asserts more than its artifact supports is not an internal error, it is a published claim.
- `CHANGELOG.md` follows Keep a Changelog; pre-1.0, MINOR means new pages or capability, PATCH means fixes only.
- Timestamp format in prose: `YYYY-MM-DD HH:MMZ (MMM DD HH:MM E?T)`.

## Collaboration Protocol

When a decision needs the user's input, present **numbered options with a recommendation flagged**. A bare "go" means execute the recommendation.
