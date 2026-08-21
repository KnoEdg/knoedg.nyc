# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/): while this project
is pre-1.0, a MINOR bump means new pages or capability, a PATCH bump means
fixes only.

## [0.5.0] - 2026-08-21

### Added

- **The map is now displayed** on both
  [`/nyc-immigrant-enclaves/`](https://knoedg.nyc/nyc-immigrant-enclaves/) and
  [`/nyc-immigrant-enclaves-paper/`](https://knoedg.nyc/nyc-immigrant-enclaves-paper/),
  by reference to the publisher's own address. This project stores no copy and
  serves no bytes; the publisher serves every request, and if the asset is
  moved or withdrawn the image stops loading.
- **The rights position is unchanged and says so.** No permission has been
  located or granted. The earlier determination — cited and not reproduced —
  is superseded in the record rather than deleted, so the change is visible.
  If the rightsholder objects, the remedy is withdrawal.

- **A published date on both documents**, rendered from the artifact's own
  `issuedAt` rather than hand-written. The line says what the date means:
  every live value was checked on or before it, and the sources can change
  after it — one of them already has.

### Changed

- Site-wide `h1` scales at `clamp(3rem, 8vw, 7rem)`, down from `9vw`.
- **Both documents read neutrally about their primary source**, which is a New
  York City agency — a public body. The data paper was titled "A map with no
  publisher", which states a real finding as a gotcha; it is now **"The NYC
  Immigrant Enclaves map"**, with "What the record establishes, and what it
  does not" as the `h2` beneath it. "A promise is not an edit" — an aphorism
  about a public official's word — is gone from both pages, replaced by the
  same distinction stated as a property of the record. Also removed:
  *provenance is broken*, *a second life*, *the omission of Little Italy*, and
  the repeated possessive framing (*the office's own report*).
  **No finding was softened:** the map still does not include Little Italy, no
  amended map has been observed, the pages still decline to say it did not
  happen, and why the page was withdrawn is still not asserted. Direct
  quotations and source URLs are citations rather than this project's voice,
  and are untouched.
- **Loaded wording removed from both published documents.** "This collection
  *refuses* to let the second stand in for the first" attributed intent to a
  document and read as self-congratulation; a scan found twelve more of the
  same shape (*deliberately*, *most technically interesting*, *the easy
  failure here*, *reconciled into tidiness*, *glossed*, *quietly*, and others).
  Every claim is unchanged — only the posture is gone.
- No personal name appears in either published artifact; the rights record now
  reads "by decision of this project's owner".

## [0.4.1] - 2026-08-21

### Added

- The **thirty-entry roster** the Immigrant Enclaves map prints, on
  [`/nyc-immigrant-enclaves/`](https://knoedg.nyc/nyc-immigrant-enclaves/) —
  names and transit access, transcribed from the checksummed image and
  published **as printed**. The artifact prints "Little Bhod-Tibet"; that
  spelling survives to the page. Little Italy's absence is now established from
  the transcription rather than from an outlet reporting it.
- A direct link to the original map, served by its publisher, opening in a new
  tab with safe `rel` and assistive indication.

### Notes

- **The map image is still not reproduced.** No redistribution permission was
  located for it, and public accessibility is not permission. What is published
  is the factual content it prints — which is what the page is about.
- Whether the *selection* of those thirty carries thin protection as a
  compilation is **not settled**, and this project does not assert that it does
  not. The reasoning is recorded on the governed record so a reader can weigh
  it.

### Changed

- The roster cannot drift: a validator checks it against the governed record in
  **both** directions, and a seven-case negative harness proves that validator
  actually fails — including on a silently corrected misspelling.

## [0.4.0] - 2026-08-21

### Added

- The first **subject-axis** collection on the site, and the first publication
  carrying two artifact classes:
  [`/nyc-immigrant-enclaves/`](https://knoedg.nyc/nyc-immigrant-enclaves/) —
  the public view over eight governed records about the "New York City
  Immigrant Enclaves" map, and
  [`/nyc-immigrant-enclaves-paper/`](https://knoedg.nyc/nyc-immigrant-enclaves-paper/)
  — a **data paper**, a prose article that cites the view's claims and holds
  none of its own.
- `schemas/data-paper/v1` and `templates/data-paper.html` now serve a real
  published article rather than only a conformance vector.

### Changed

- The shared renderer emits a record-count manifest for a public view and
  **refuses one for a data paper**. A data paper holds no claims, so counts
  would be invented rather than rendered. Both directions are enforced and
  covered by the renderer conformance suite.
- `scripts/validate_jsonld.py` now expands **every** published JSON-LD
  document, discovered by glob. It previously expanded one hardcoded page, so
  the six source pages added after it were never checked — a gate covering one
  of nine files reported success in the same words as one covering all nine.

### Notes

- The collection governs a **map as an artifact**, not New York City's
  immigrant neighbourhoods. It takes no position on which neighbourhoods
  belong on any such map.
- The map itself is **cited and not reproduced**: no redistribution permission
  was located for it, so the pages describe and link the artifact and publish
  none of its bytes.

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
