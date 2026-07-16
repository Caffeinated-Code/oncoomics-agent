# Execution Plan

## Summary

Build **OncoOmics Agent: NSCLC Atlas Edition**, a cost-conscious AWS project that curates public lung single-cell atlas data into PostgreSQL summary tables and exposes the database through a safe AI agent.

The first implementation prioritizes text-based database Q&A. Voice chat is added after the data model, SQL queries, and agent guardrails are reliable.

## Phase 1: Repo And Scientific Framing

- Center the project on NSCLC single-cell atlas exploration.
- Use HLCA as the lung reference context and LuCA as the NSCLC tumor atlas source.
- Use TRACERx/PEACE as biological motivation for tumor evolution and metastasis, not as the first ingestion target.
- Explain why the database stores summaries rather than raw single-cell matrices.

## Phase 2: Data Source Reconnaissance

- Confirm downloadable LuCA/CELLxGENE files, metadata fields, and licensing.
- Select a small gene panel covering immune checkpoints, tumor drivers, EMT/invasion, myeloid inflammation, proliferation, and hypoxia.
- Identify harmonized fields for sample, disease, tissue, cell type, dataset, and cell counts.
- Decide whether HLCA is used as source data in v1 or only as reference documentation.

## Phase 3: Local Curation

- Download or access public atlas files locally.
- Generate summary tables:
  - expression by gene and cell type
  - expression by gene, cell type, and disease/sample group
  - cell-type abundance by sample or dataset
  - dataset/sample/cell-type metadata
  - source provenance
- Keep raw large files outside Git and out of PostgreSQL.

## Phase 4: Local PostgreSQL

- Create the normalized atlas schema.
- Load curated summary tables.
- Write benchmark SQL queries for the MVP biological questions.
- Validate that every answer can cite a dataset/source file.

## Phase 5: AWS Deployment

- Configure AWS CLI locally.
- Create an AWS Budget before deploying resources.
- Create an S3 bucket for curated source files and manifests.
- Deploy a small RDS PostgreSQL or Aurora PostgreSQL database using the most cost-effective free-plan-compatible option.
- Load curated summaries into the AWS database.
- Use least-privilege credentials for app access.

## Phase 6: Backend And AI Agent

- Build read-only API endpoints for schema inspection, safe SQL execution, gene lookup, cell-type summaries, and source provenance.
- Build an agent that calls tools rather than answering from memory.
- Enforce `SELECT`-only queries, row limits, timeouts, and visible SQL.
- Return "not available in this curated database" when a question asks for unsupported data.

## Phase 7: Voice Interface

- Add speech-to-text after text Q&A works.
- Keep spoken answers concise.
- Show SQL, tables, plots, and provenance visually.

## MVP Questions

- Which NSCLC cell types express `CD274` / PD-L1 most highly?
- Which T cell populations express `PDCD1`, `CTLA4`, `LAG3`, or `TIGIT`?
- Which myeloid cell types express `S100A8`, `S100A9`, `CXCL8`, `IL1B`, or `SPP1`?
- Which malignant epithelial or stromal compartments express EMT genes such as `VIM`, `ZEB1`, `SNAI1`, and `MMP9`?
- How do selected tumor-driver genes such as `EGFR`, `KRAS`, `MET`, and `MYC` vary by cell type?
- What dataset, source file, and SQL query produced this answer?

## Acceptance Criteria

- The repo clearly explains the biology, data sources, database design, AWS plan, and customization path.
- Curated data is public, processed, and reproducible.
- PostgreSQL answers at least five MVP questions using summary tables.
- AWS resources are budget-protected and tagged.
- The agent never fabricates unsupported database answers.
- Every biological answer includes SQL and source provenance.

