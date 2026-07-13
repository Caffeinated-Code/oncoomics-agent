# OncoOmics Agent

An advanced Bioinformatics Field Guide project: curate a small public cancer multi-omics dataset, load it into a cost-conscious AWS-hosted SQL database, and build an AI agent that can answer biological questions from the database with evidence.

## Big Idea

Public omics data is abundant, but using it still requires knowing where the data lives, how the metadata is structured, which identifiers match across modalities, and how to query it responsibly. This project turns a focused public oncology multi-omics dataset into a queryable research system.

The first biological question:

> In selected cancer cohorts, how do alterations in key cancer genes relate to RNA expression, protein abundance, copy number, and clinical context?

The first technical goal:

> Build a small, reproducible AWS-backed SQL database and a safe AI agent that can answer natural-language questions against curated public data.

## What This Showcases

- Bioinformatics public data curation
- Relational database design and SQL
- Multi-omics data integration
- AWS cost-aware architecture
- AI agent tool use over structured data
- Reproducible scientific answers with source traceability
- A path toward voice-based database interaction

## Project Shape

```mermaid
flowchart LR
    A["Public sources<br/>cBioPortal, GDC, CPTAC"] --> B["Curated CSV/Parquet files"]
    B --> C["PostgreSQL schema"]
    C --> D["AWS RDS PostgreSQL"]
    B --> E["S3 source archive"]
    D --> F["Backend query API"]
    F --> G["AI SQL agent"]
    G --> H["Text chat first"]
    H --> I["Voice chat later"]
```

## Primers

- [Biology Primer](docs/biology-primer.md)
- [Database Primer](docs/database-primer.md)
- [AWS Primer](docs/aws-primer.md)
- [AWS Account Prep](docs/aws-account-prep.md)
- [Execution Plan](docs/execution-plan.md)

## Guiding Constraint

This project is intentionally scoped for learning and portfolio value, not for mirroring all of TCGA or CPTAC. The first version should use processed, public, curated data only and stay small enough to run cheaply.

