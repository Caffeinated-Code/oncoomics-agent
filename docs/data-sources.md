# Data Sources

## Primary Source: LuCA

[**LuCA**](https://github.com/icbi-lab/luca), the single-cell Lung Cancer Atlas, is the recommended primary source for v1 because it is focused on [NSCLC](biology-primer.md#why-nsclc) and provides a strong basis for [tumor microenvironment](biology-primer.md#the-biological-setting) questions.

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

The [**Human Lung Cell Atlas**](https://data.humancellatlas.org/hca-bio-networks/lung/atlases/lung-v1-0) provides healthy and disease lung reference context.

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

[**TRACERx and PEACE**](https://www.nature.com/articles/s41586-023-05729-x) are valuable for explaining why [NSCLC](biology-primer.md#why-nsclc) evolution and metastasis matter. They are not the first ingestion target because parts of the data are controlled-access or license-restricted.

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

## Implemented V1 Sources

The current local build ingests compact public cBioPortal data from:

- `luad_tcga_pan_can_atlas_2018`
- `lusc_tcga_pan_can_atlas_2018`

These sources provide mutation, RNA expression, copy-number, methylation, RPPA, and structural-variant profile availability. The implemented scripts currently summarize mutation, RNA expression z-scores, and discrete GISTIC copy-number calls for the curated NSCLC gene panel.

Primary use in this project:

- separate [LUAD and LUSC](biology-primer.md#why-nsclc) driver interpretation
- provide cohort-level mutation frequencies for genes such as `KRAS`, `EGFR`, `MET`, `ALK`, and `MYC`
- provide bulk tumor expression context for [immune checkpoint](biology-primer.md#v1-gene-themes), myeloid, EMT, proliferation, hypoxia, and antigen-presentation genes
- provide discrete GISTIC copy-number summaries as screening features for follow-up analysis

The current local build also ingests public LuCA CELLxGENE metadata:

- core and extended LuCA dataset records
- cell counts
- disease labels
- tissue labels
- assay labels
- H5AD asset URLs and file sizes
- 33 LuCA cell-type labels
- broad compartment mapping for agent queries
- curated gene-by-cell-type evidence for the NSCLC panel

Primary use in this project:

- connect genes such as `CD274`, `PDCD1`, `CTLA4`, `SPP1`, `S100A8`, and `VIM` to plausible malignant, lymphoid, myeloid, stromal, or epithelial compartments
- expose [cell-type](biology-primer.md#the-biological-setting) context for app users and database queries
- mark evidence status transparently until full matrix-derived expression summaries are computed

The full LuCA single-cell matrices are kept out of Git and out of the first database build because v1 is designed to stay small, inspectable, and AWS-friendly. Quantitative expression extraction from the large H5AD assets is the next scalable processing step.

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
