# Execution Plan

## Summary

Build a cost-conscious AWS bioinformatics project that curates a focused public cancer multi-omics dataset into PostgreSQL and exposes it through an AI agent. The project starts with text-based database Q&A, then adds voice after the SQL and data layer are reliable.

## Phase 1: Project Foundation

- Write primers for biology, database design, and AWS cost-aware architecture.
- Define the first biological question and supported question set.
- Keep v1 focused on breast cancer, selected cancer genes, and processed public data.
- Track all public sources and data transformations.

## Phase 2: Public Data Curation

- Select source datasets from cBioPortal, GDC, and CPTAC or Proteomic Data Commons.
- Download or query processed public data only.
- Keep selected genes, cancer types, samples, and omics layers.
- Create cleaned local CSV files for mutation, expression, copy number, proteomics, clinical metadata, and source provenance.

## Phase 3: Local SQL Database

- Create a PostgreSQL schema with studies, patients, samples, genes, omics tables, clinical attributes, and source provenance.
- Load curated CSV files locally.
- Write benchmark SQL queries for the biological questions.
- Validate sample joins and missing-data behavior.

## Phase 4: AWS Deployment

- Create AWS Budget and billing alerts before infrastructure.
- Store curated source files in S3.
- Deploy a small RDS PostgreSQL database.
- Load curated data into RDS.
- Use least-privilege database credentials for application access.

## Phase 5: Backend And Agent

- Build a small backend API for schema inspection, safe SQL execution, cohort summaries, and gene multi-omics profiles.
- Add an AI agent that calls backend tools instead of guessing.
- Require read-only SQL, row limits, and visible source provenance.
- Return answers with query text, source tables, and caveats.

## Phase 6: Voice Layer

- Add speech-to-text after text chat works.
- Add concise text-to-speech summaries.
- Keep detailed evidence in the visual UI.

## MVP Questions

- Which selected genes are most frequently mutated in breast cancer?
- For TP53, how does RNA expression differ between mutant and wildtype samples?
- Is protein abundance available for TP53 or related selected genes?
- Which samples have mutation, RNA, and clinical data?
- Which samples have mutation, RNA, and protein data?
- What clinical subtypes are represented?
- What SQL query produced this answer?
- What public source did this answer come from?

## Acceptance Criteria

- The repository explains the biology, database, AWS design, and implementation plan.
- The first curated dataset is public and reproducible.
- SQL queries answer at least five MVP biological questions.
- AWS resources are tagged and budget-protected.
- The agent never answers database questions without querying tools or explicitly stating that data is unavailable.
- Answers include enough provenance for a reader to reproduce the result.

