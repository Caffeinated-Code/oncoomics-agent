# Data Sources

## Primary Source: LuCA

LuCA, the single-cell Lung Cancer Atlas, is the recommended primary source for v1 because it is focused on NSCLC and provides a strong basis for tumor microenvironment questions.

Source links:

- [LuCA GitHub](https://github.com/icbi-lab/luca)
- [LuCA web portal](https://luca.icbi.at/)
- [LuCA on CZ CELLxGENE](https://cellxgene.cziscience.com/collections/edb893ee-4066-4128-9aec-5eb2b03f8287)

Why it fits:

- NSCLC-focused
- single-cell scale
- annotated cell types
- useful for immune, malignant, stromal, and epithelial questions
- public and suitable for a curated summary database project

## Reference Source: Human Lung Cell Atlas

The Human Lung Cell Atlas provides healthy and disease lung reference context.

Source links:

- [HLCA on HCA Data Portal](https://data.humancellatlas.org/hca-bio-networks/lung/atlases/lung-v1-0)
- [HLCA GitHub](https://github.com/LungCellAtlas/HLCA)
- [HLCA publication](https://pmc.ncbi.nlm.nih.gov/articles/PMC10287567/)

Why it fits:

- broad lung reference atlas
- healthy and disease context
- harmonized cell type labels
- useful for comparing NSCLC-associated expression with lung reference cell types

## Biological Framing: TRACERx And PEACE

TRACERx and PEACE are valuable for explaining why NSCLC evolution and metastasis matter. They are not the first ingestion target because parts of the data are controlled-access or license-restricted.

Source links:

- [TRACERx metastases paper](https://www.nature.com/articles/s41586-023-05729-x)
- [TRACERx processed Zenodo record](https://zenodo.org/records/7649257)
- [TRACERx EGA data access page](https://www.ega-archive.org/dacs/EGAC00001000632)

How to use in v1:

- cite as motivation for tumor evolution, metastatic spread, and longitudinal sampling
- avoid ingesting controlled-access raw data
- optionally ingest only clearly licensed, processed, public summary files after reviewing terms

## V1 Data Policy

- Public data only.
- Processed data only.
- No controlled-access human genomic files.
- No raw FASTQ, BAM, CRAM, or massive `.h5ad` files in Git.
- Source license and provenance must be recorded before ingestion.

## Citation And Provenance Fields

Every imported source should be tracked with:

- source name
- source URL
- publication DOI or PubMed link, if available
- download date
- license or access note
- file name and checksum, if downloaded
- transformation script or notebook used

This keeps the project reproducible and prevents scientific claims from drifting away from the data.
