# FAIR Data Practices Primer

This project is designed to teach beginners how to build an impactful bioinformatics project using FAIR data practices.

FAIR means:

- **Findable:** datasets, tables, and reports should have clear names, source URLs, and identifiers.
- **Accessible:** public data sources and access notes should be recorded before analysis.
- **Interoperable:** tables should use stable identifiers, controlled labels where possible, and schemas that can move from CSV to SQL.
- **Reusable:** every analysis should preserve provenance, assumptions, caveats, and enough metadata for another person to rerun it.

## How FAIR Shows Up In This Repo

| FAIR principle | Project implementation |
|---|---|
| Findable | `datasets`, `source_files`, `luca_datasets`, and README links point back to public sources |
| Accessible | only public, processed, non-controlled data are used in the first build |
| Interoperable | curated CSV tables map into a normalized SQL schema |
| Reusable | scripts regenerate curation tables, reports, app data, and validation checks |

## Beginner Checklist

Before adding a new dataset:

1. Record the dataset name, source URL, publication, and access terms.
2. Decide whether the data are public, controlled-access, or license-restricted.
3. Keep raw large files out of Git.
4. Store compact curated outputs in `data/curated/` or `results/tables/`.
5. Add the dataset to the schema or a clear staging table.
6. Add a validation check so broken or empty tables are caught early.
7. Explain biological assumptions in the report and app.

## Why This Matters

A strong bioinformatics project is more than an analysis. It is a small evidence system. Readers should be able to tell:

- where the data came from
- what was transformed
- which assumptions were made
- which tables support each claim
- what should be done before clinical or translational interpretation

For this repo, FAIR practice is the difference between a demo and a project that can scale into a credible atlas-backed analysis product.
