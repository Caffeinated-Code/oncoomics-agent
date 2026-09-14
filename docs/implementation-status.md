# Implementation Status

## What Works Now

The project has a local, reproducible v1.

Implemented components:

- public cBioPortal ingestion for TCGA LUAD and LUSC PanCancer Atlas studies
- curated 30-gene NSCLC panel
- mutation summary by cancer type and gene
- RNA expression z-score summary by cancer type and gene
- discrete copy-number summary by cancer type and gene
- source provenance for TCGA, LuCA, and HLCA
- public LuCA CELLxGENE metadata ingestion
- LuCA cell-type table with broad compartment mapping
- curated LuCA gene-by-cell-type evidence layer for the NSCLC panel
- normalized SQL schema
- local SQLite database for development
- safe read-only query CLI
- generated Markdown report and SVG figures
- modular runner for end-to-end reproduction

## Why This Is The Right First Build

The first build should prove the architecture before handling very large single-cell files. TCGA LUAD and LUSC provide compact public molecular data through cBioPortal. That makes it possible to build and test the database, SQL queries, provenance model, and answer format immediately.

LuCA remains the primary NSCLC single-cell atlas target. In v1 the project ingests public CELLxGENE metadata, cell-type labels, H5AD asset records, and a curated gene-by-cell-type evidence layer for the same gene panel. The next build should extract quantitative expression summaries from the large LuCA H5AD matrix.

## Current Data Layers

| Layer | Source | Status | Role |
|---|---|---|---|
| Mutation | TCGA LUAD/LUSC via cBioPortal | implemented | driver and immune-gene mutation context |
| RNA expression | TCGA LUAD/LUSC via cBioPortal | implemented | cohort-level expression context |
| Copy number | TCGA LUAD/LUSC via cBioPortal | implemented | discrete GISTIC alteration context |
| Single-cell atlas | LuCA / CELLxGENE | metadata and curated evidence implemented | cell-compartment interpretation layer |
| Lung reference atlas | HLCA | source recorded | next normal-lung reference layer |

## Biological Readout

The current report supports cautious statements such as:

- LUAD and LUSC should be analyzed separately.
- `KRAS` and `EGFR` mutation frequencies are higher in LUAD than LUSC in this selected panel.
- Immune checkpoint RNA summaries are bulk tumor context, not cell-type-resolved expression.
- LuCA cell-type evidence can identify plausible compartments for genes such as `CD274`, `PDCD1`, `SPP1`, `S100A8`, and `VIM`, with clear labels that the evidence is not yet matrix-quantified.
- CNA summaries are screening features and require focality and expression follow-up.

## Files To Review

- `configs/gene_panel.csv`
- `sql/schema.sql`
- `scripts/curate_cbioportal_nsclc.py`
- `scripts/curate_luca_metadata.py`
- `scripts/build_sqlite_database.py`
- `scripts/query_oncoomics_agent.py`
- `scripts/generate_nsclc_report.py`
- `scripts/run_project_modules.sh`
- `results/nsclc_atlas_report.md`

## Commands

```bash
bash scripts/run_project_modules.sh all
```

For AWS later, keep the same curated CSV tables and load them into PostgreSQL instead of SQLite.
