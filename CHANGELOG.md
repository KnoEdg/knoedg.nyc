# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/): while this project
is pre-1.0, a MINOR bump means new pages or capability, a PATCH bump means
fixes only.

## [0.3.0] - 2026-08-10

### Added

- Six internal source pages, one per publisher family behind the NYC
  Boundaries comparison, replacing the previous transitional direct
  external-evidence links: [`/nyc-dcp-borough-boundaries/`](https://knoedg.nyc/nyc-dcp-borough-boundaries/),
  [`/nyc-census-gazetteer/`](https://knoedg.nyc/nyc-census-gazetteer/),
  [`/nyc-openstreetmap/`](https://knoedg.nyc/nyc-openstreetmap/),
  [`/nyc-whos-on-first/`](https://knoedg.nyc/nyc-whos-on-first/),
  [`/nyc-geoboundaries/`](https://knoedg.nyc/nyc-geoboundaries/), and
  [`/nyc-overture/`](https://knoedg.nyc/nyc-overture/). Each presents its
  publisher's own records with structured JSON-LD — claim-level
  lifecycle/confidence and `prov:Activity`-backed publication history, not
  just human-readable prose.
- A documented internal-source-page pattern that every source page follows:
  nine canonical sections (Publisher, Dataset, Measurements, Rights,
  Published material, Validation, Governance, Limitations, Publication
  history) shared by a single generic renderer and template.

### Fixed

- Instant text near a UTC day boundary could display the wrong calendar
  date — e.g. `03:55 UTC` on the 10th rendered as "August 10" even though
  the actual New York local time was "August 9, 11:55 PM." All
  `datetime`-format values now render in `America/New_York` local time; the
  machine `<time datetime="...">` attribute is unchanged, still the exact
  original UTC instant.
- 19 table cells on `/nyc-boundaries/` held hardcoded literal
  UTC-suffixed text ("... 19:35:50 UTC") bypassing the time-rendering
  mechanism entirely, so the fix above never reached them. All now resolve
  through the same governed mechanism as everywhere else on the site.
- `/nyc-boundaries/`'s 15-entry Publication History rendered as hardcoded
  prose, including entries that already had an exact recorded time going
  unused. Corrected so every entry resolves from its own governed record;
  entries whose exact time was never captured now render a plain date
  rather than a fabricated time. Two dataset "Source last updated" cells
  (DCP, Census Gazetteer) were similarly truncated to date-only despite
  full precision already being governed elsewhere in the pack; corrected.
- A duplicated per-relation OpenStreetMap detail table on `/nyc-boundaries/`
  (and the equivalent for Who's On First) removed once each publisher's own
  dedicated source page existed to own that content, closing a real drift
  risk between the two copies of the same facts.

### Changed

- Every displayed instant across the site is now held to one standing
  rule: never silently downgrade to date-only precision when fuller
  precision is known elsewhere in the pack, and never hardcode a governed
  timestamp as prose instead of resolving it from the record.

## [0.2.0] - 2026-08-09

### Added

- Downloadable public fixtures for every governed NYC Boundaries comparison
  source: DCP water-excluded/water-included borough geometry, 2023 Census
  Gazetteer county measurements, 10 exact OpenStreetMap relation-version
  metadata records, 5 geoBoundaries USA ADM2 county geometries (CC BY 4.0),
  5 Who's On First current county geometries (CC0 / CC BY, Quattroshapes),
  and 11 Overture Maps division-area geometries including both of Richmond
  County's land and maritime representations (ODbL 1.0).
- 46 active governed comparison records across 6 independently-sourced
  provenance families, each disclosing its rights, lineage, and
  independence disposition rather than treating agreement as unexamined
  corroboration.

### Fixed

- A land/maritime classification discrepancy in the Overture geometry
  fixture, found against the governed source's original capture.
  Root-caused (confirmed unchanged upstream release asset, a reproducible
  query, and a release-wide base-rate check) to an error in the original
  capture rather than a live Overture data change, and corrected —
  disclosed in the public page's own limitations text rather than silently
  fixed.

## [0.1.1] - 2026-08-08

### Added

- `robots.txt` with normal crawling enabled and a sitemap reference.
- `sitemap.xml` covering all four indexable pages (Home, About, How it
  works, KEE technical overview).
- Consistent self-referencing canonical URLs across all four pages.

## [0.1.0] - 2026-08-08

### Added

- Initial public release of [knoedg.nyc](https://knoedg.nyc): the homepage,
  About, How it works, and KEE technical overview pages, plus the first
  NYC Boundaries knowledge resource.
