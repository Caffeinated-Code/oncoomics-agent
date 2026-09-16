# Project Roadmap

The project goal is to teach novice bioinformatics learners how to build an impactful, evidence-backed public-data project while giving expert readers enough structure to evaluate the biology and engineering.

## Current Build

The current build includes:

- public TCGA LUAD/LUSC mutation, RNA expression, and copy-number summaries
- LuCA public metadata and curated cell-type evidence
- normalized SQL schema
- local SQLite database
- command-line query layer
- reproducible reports
- public Shiny app
- AWS groundwork

## Next Build Sequence

### 1. Matrix-Derived LuCA Expression

Goal: compute real gene-by-cell-type expression summaries from LuCA H5AD files.

Planned output:

- `luca_expression_by_cell_type.csv`
- `luca_expression_by_compartment.csv`
- SQL tables for cell-type expression
- app plots for cell-type-resolved markers

Why it matters:

- replaces curated evidence with quantitative single-cell summaries
- lets beginners see how a large atlas becomes a compact query table
- gives experts a stronger basis for interpreting checkpoint, myeloid, EMT, and antigen-presentation programs

### 2. Read-Only API Backend

Goal: expose the database through a small read-only API.

Planned output:

- `/health`
- `/datasets`
- `/genes`
- `/query/canned`
- `/gene/{symbol}`
- `/cell-context/{symbol}`

Why it matters:

- separates analysis logic from the Shiny front end
- makes the project easier to deploy on AWS
- prepares the database for an agent or voice interface

### 3. AWS Deployment

Goal: move from local SQLite and bundled CSVs to a cost-conscious cloud architecture.

Planned output:

- S3 curated-data bucket
- PostgreSQL on RDS or Aurora Serverless
- read-only API service
- budget alarms
- least-privilege IAM notes

Why it matters:

- teaches cloud architecture without overspending
- makes the project credible as a scalable bioinformatics application

### 4. Voice And Chat Interface

Goal: allow natural-language questions over curated, source-backed tables.

Planned output:

- question router
- SQL-safe tool layer
- response templates with evidence and caveats
- optional voice front end

Why it matters:

- shows how an agent should answer from a database rather than inventing biological claims

### 5. Expert Biology Modules

Goal: add focused analysis modules that matter in NSCLC interpretation.

Planned modules:

- LUAD versus LUSC driver landscape
- checkpoint axis and immune suppression
- myeloid inflammation and macrophage states
- EMT, stromal remodeling, and invasion
- antigen presentation and interferon response
- copy-number context and focality caveats

### 6. Testing And Teaching Assets

Goal: make the repo useful as a learning path.

Planned output:

- expected-output tests for key SQL queries
- app smoke tests
- beginner exercises
- glossary
- data-curation worksheets
- FAIR data checklist

## Definition Of Done

The project should be considered complete when a beginner can:

1. understand LUAD, LUSC, NSCLC, TCGA, LuCA, HLCA, and FAIR data practice
2. rerun the local pipeline
3. inspect the SQL schema
4. open the Shiny app and interpret the main plots
5. trace every claim back to a source table
6. understand what changes when the project moves to AWS

An expert reader should be able to:

1. see the biological rationale quickly
2. inspect assumptions and caveats
3. verify provenance
4. identify which layers are quantitative and which are curated
5. see a path toward real atlas-scale computation
