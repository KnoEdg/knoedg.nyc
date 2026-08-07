# KnoEdg NYC

**New York City, connected.**

KnoEdg NYC brings together publicly available information about New York City’s places, people, organizations, events, and systems—making it easier to explore how they connect and change over time.

This repository contains the public website for **[knoedg.nyc](https://knoedg.nyc)**.

## About

Information about New York City is distributed across thousands of sources: public records, open datasets, news, research, archives, public websites, and social media.

KnoEdg NYC develops a structured, traceable knowledge landscape across those sources while preserving:

- where information came from;
- when it was published or observed;
- the context in which it was presented;
- how it has changed, been corrected, or been superseded;
- the rights and restrictions governing its use.

Publicly accessible information is not necessarily openly licensed or freely redistributable. KnoEdg NYC preserves that distinction.

## The website

The website is intended for the general public. It will provide ways to explore:

- places and neighborhoods;
- buildings, businesses, and institutions;
- people and organizations;
- transportation and city systems;
- news, events, and public activity;
- history and change over time.

The initial site will introduce the project and publish its research, sources, methods, and early knowledge-pack releases.

## NYC Knowledge Pack

[`nyc-knowledge-pack`](https://github.com/KnoEdg/nyc-knowledge-pack) is the structured knowledge foundation behind KnoEdg NYC.

It is a domain knowledge pack that catalogs and connects public sources while retaining source identity, provenance, authority, licensing, temporal context, and lifecycle history.

The knowledge pack is not intended to create a single unquestionable version of New York City. It preserves differing sources, perspectives, assertions, and levels of authority.

## Relationship to KEE

The NYC Knowledge Pack is intended to conform to [KEE](https://github.com/KnoEdg/kee), KnoEdg’s framework for epistemic governance and organizational memory.

KEE follows a prior-art-first method:

> Adopt → Compose → Profile → Extend → Research Gap

A KEEpack is used loosely as another name for a `<domain>-knowledge-pack`, with an important qualification: a KEEpack declares and satisfies applicable KEE conformance.

The public website does not require visitors to understand KEE. KEE provides the underlying discipline for provenance, authority, lifecycle, contestation, and conformance.

## Project status

KnoEdg NYC is at an early stage.

Current work includes:

- consolidating research on the NYC information landscape;
- establishing source and licensing inventories;
- defining the first `nyc-knowledge-pack` profile;
- identifying stable NYC identifiers and cross-source relationships;
- designing reproducible ingestion and release processes;
- developing the initial public website.

No claim of comprehensive NYC coverage is made.

## Principles

- **Traceable:** Information remains connected to its sources.
- **Contextual:** Authority, perspective, time, and scope are preserved.
- **Composable:** Established standards and identifiers are reused.
- **Portable:** The knowledge pack is not defined by one database or cloud provider.
- **Responsible:** Public availability is not treated as permission to copy or redistribute.
- **Durable:** Releases, changes, corrections, and supersession remain part of the record.
- **Useful:** Technical complexity should not obstruct public exploration.

## Repository scope

This repository contains the `knoedg.nyc` website and its public-facing content.

The knowledge pack, ingestion pipelines, schemas, research artifacts, and release data may be maintained in separate repositories as their boundaries become established.

## Development

Development instructions will be added after the initial application architecture is established.

## Governance and provenance

The project is currently personally maintained. Maintainer identity and responsibility will be recorded where required for governance, releases, provenance, legal notices, and external program applications.

The project itself—not its maintainer—is the primary public identity.

## License

The website’s software and original written content will receive explicit licenses before the first public release.

Third-party data, reporting, media, quotations, and other source material retain their respective rights and terms. No repository-level license should be interpreted as relicensing third-party material.
