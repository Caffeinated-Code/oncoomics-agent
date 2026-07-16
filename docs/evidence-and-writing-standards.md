# Evidence And Writing Standards

## Purpose

This repo is written for readers who want to learn NSCLC biology, understand public single-cell atlas data, and build a similar AI database agent. The content should be clear enough for an advanced learner and rigorous enough for a scientific/computational biology portfolio.

## Non-Negotiables

- Do not include prompts, hidden instructions, model notes, or draft scaffolding in reader-facing files.
- Do not make biological claims without evidence or a clearly marked hypothesis.
- Do not let the agent answer from memory when the database should be queried.
- Do not store private credentials, controlled-access data, or restricted patient-level files.
- Do not overstate the project as clinical decision support.

## Writing Style

- Lead with the biological question.
- Explain unfamiliar terms once, then use them consistently.
- Use diagrams when they clarify data flow, biology, or architecture.
- Keep sections short and skimmable.
- Prefer concrete examples: gene, cell type, table, query, source.
- Avoid hype, filler, and generic AI language.

## Scientific Evidence Standard

Use primary publications, official dataset portals, or well-maintained project repositories for factual claims.

Recommended source types:

- peer-reviewed papers
- HCA, CELLxGENE, LuCA, or official project pages
- official AWS documentation for infrastructure claims
- dataset manifests, licenses, and provenance files

Every biological result produced by the agent should include:

- the SQL query or tool call used
- the source dataset
- the gene or cell-type filters
- the number of cells/samples summarized
- the limitation of the curated database

## Current Evidence Anchors

- HLCA: integrated human lung reference atlas with broad lung cell type context.
- LuCA: NSCLC-focused single-cell lung cancer atlas for tumor microenvironment questions.
- TRACERx/PEACE: biological motivation for NSCLC evolution, metastasis, and longitudinal disease context.
- AWS Free Tier docs: source for cost-conscious infrastructure decisions.

See [Scientific References](scientific-references.md) for the current citation set.

## Agent Answer Standard

The agent should follow this response pattern:

1. Short direct answer.
2. Evidence table or key numbers.
3. SQL/query shown or linked.
4. Source provenance.
5. Caveat if data is incomplete or unsupported.

Example:

```text
CD274 expression is highest in [cell types] within the curated NSCLC atlas summary.
This result is based on [n] cells across [n] samples from [source].
The query grouped expression_summaries by cell_type_name and filtered gene symbol = 'CD274'.
Caveat: this summary does not prove protein-level PD-L1 abundance or clinical response.
```

## EB1A-Level Portfolio Standard

The repo should make expertise visible through execution quality:

- scientific framing is accurate and sourced
- data engineering choices are cost-aware and reproducible
- SQL schema reflects biological entities cleanly
- AWS design is practical, tagged, and budget-protected
- AI agent behavior is auditable and conservative
- the project can be generalized to other public or private atlas databases

The strongest signal is not complexity for its own sake. It is a polished, reproducible system that connects biology, data infrastructure, and AI safely.
