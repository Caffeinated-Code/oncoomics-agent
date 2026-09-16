# OncoOmics Agent: NSCLC Atlas Action Report

## Executive Summary

This project now has a compact, reproducible NSCLC atlas database and a Shiny demo app for interactive review. The current build integrates public TCGA LUAD/LUSC mutation, RNA expression, and copy-number summaries with LuCA single-cell atlas metadata and curated gene-by-cell-type evidence.

The main value is fast biological triage. A user can compare LUAD and LUSC driver patterns, inspect checkpoint expression context, review copy-number alteration signals, and connect selected markers to plausible LuCA cell compartments.

## Database Coverage

| entity | count |
| --- | --- |
| samples | 1053 |
| genes | 30 |
| expression observations | 29820 |
| mutation observations | 776 |
| copy-number observations | 29940 |
| LuCA cell types | 33 |
| LuCA gene-cell evidence rows | 63 |

## Key Biological Findings

### Driver Landscape

| cancer_type | symbol | mutated_samples | sequenced_samples | mutation_frequency | recurrent_protein_changes |
| --- | --- | --- | --- | --- | --- |
| LUAD | KRAS | 168 | 566 | 0.297 | G12C:70;G12V:40;G12D:20;G12A:17;G13C:7 |
| LUAD | EGFR | 70 | 566 | 0.124 | L858R:23;E746_A750del:16;L861Q:3;E709_T710delinsD:3;L62R:2 |
| LUAD | ALK | 34 | 566 | 0.06 | V349F:1;L80M:1;T1102I:1;X263_splice:1;G263V:1 |
| LUAD | MET | 21 | 566 | 0.037 | X1010_splice:6;H476Y:1;R1279I:1;N315S:1;T660R:1 |
| LUAD | MYC | 4 | 566 | 0.007 | M116V:1;S161L:1;K66N:1;P74T:1 |
| LUSC | ALK | 18 | 487 | 0.037 | P1260Q:1;L1145M:1;T1512K:1;P1112Q:1;R353S:1 |
| LUSC | EGFR | 14 | 487 | 0.029 | L861Q:2;X297_splice:1;P1019L:1;S229C:1;X1039_splice:1 |
| LUSC | MET | 8 | 487 | 0.016 | Q328K:1;T1096S:1;I565M:1;Q272*:1;E719*:1 |
| LUSC | KRAS | 7 | 487 | 0.014 | V14I:1;G12V:1;G12A:1;Q61H:1;R123*:1 |
| LUSC | MYC | 4 | 487 | 0.008 | Q448H:1;Q321E:1;L164V:1;R387W:1 |

KRAS and EGFR are more prominent in LUAD than LUSC in this selected gene panel. This supports histology-aware interpretation and prevents mixing LUAD and LUSC into one generic NSCLC signal.

### Immune Checkpoint RNA Context

| cancer_type | symbol | n_samples | fraction_high_zscore |
| --- | --- | --- | --- |
| LUAD | LAG3 | 510 | 0.165 |
| LUAD | PDCD1 | 510 | 0.165 |
| LUAD | TIGIT | 510 | 0.159 |
| LUAD | CD274 | 510 | 0.155 |
| LUAD | CTLA4 | 510 | 0.153 |
| LUAD | HAVCR2 | 510 | 0.143 |
| LUSC | CD274 | 484 | 0.186 |
| LUSC | HAVCR2 | 484 | 0.167 |
| LUSC | PDCD1 | 484 | 0.163 |
| LUSC | CTLA4 | 484 | 0.157 |
| LUSC | TIGIT | 484 | 0.157 |
| LUSC | LAG3 | 484 | 0.153 |

Checkpoint RNA summaries are useful for cohort-level screening. They remain bulk tumor measurements and should not be interpreted as cell-source-resolved signals.

### LuCA Cell-Type Context

| title | cell_count | h5ad_filesize_gb | disease_labels |
| --- | --- | --- | --- |
| The single-cell lung cancer atlas (LuCA) -- extended atlas | 1283972 | 17.617 | chronic obstructive pulmonary disease;lung adenocarcinoma;non-small cell lung carcinoma;normal;squamous cell lung carcinoma |
| The single-cell lung cancer atlas (LuCA) -- core atlas | 892296 | 12.897 | chronic obstructive pulmonary disease;lung adenocarcinoma;non-small cell lung carcinoma;normal;squamous cell lung carcinoma |

| symbol | cell_type_name | compartment | expected_expression | quantitative_status |
| --- | --- | --- | --- | --- |
| CD274 | malignant cell | malignant tumor | context-dependent | not_matrix_quantified_in_v1 |
| CD274 | dendritic cell | myeloid immune | moderate | not_matrix_quantified_in_v1 |
| CD274 | macrophage | myeloid immune | moderate | not_matrix_quantified_in_v1 |
| CTLA4 | CD4-positive, alpha-beta T cell | lymphoid immune | moderate | not_matrix_quantified_in_v1 |
| CTLA4 | regulatory T cell | lymphoid immune | high | not_matrix_quantified_in_v1 |
| EGFR | epithelial cell of lung | epithelial | moderate | not_matrix_quantified_in_v1 |
| EGFR | malignant cell | malignant tumor | high | not_matrix_quantified_in_v1 |
| KRAS | malignant cell | malignant tumor | context-dependent | not_matrix_quantified_in_v1 |
| PDCD1 | CD4-positive, alpha-beta T cell | lymphoid immune | moderate | not_matrix_quantified_in_v1 |
| PDCD1 | CD8-positive, alpha-beta T cell | lymphoid immune | high | not_matrix_quantified_in_v1 |
| PDCD1 | regulatory T cell | lymphoid immune | moderate | not_matrix_quantified_in_v1 |
| S100A8 | classical monocyte | myeloid immune | high | not_matrix_quantified_in_v1 |
| S100A8 | neutrophil | myeloid immune | high | not_matrix_quantified_in_v1 |
| SPP1 | malignant cell | malignant tumor | context-dependent | not_matrix_quantified_in_v1 |
| SPP1 | macrophage | myeloid immune | high | not_matrix_quantified_in_v1 |
| VIM | malignant cell | malignant tumor | context-dependent | not_matrix_quantified_in_v1 |
| VIM | fibroblast of lung | stromal | high | not_matrix_quantified_in_v1 |
| VIM | stromal cell | stromal | high | not_matrix_quantified_in_v1 |

The LuCA layer gives the app a cell-compartment interpretation path. The current evidence table is curated and transparent. The next data layer should compute expression summaries directly from the LuCA H5AD matrices.

## Actionable Insights

- Prioritize LUAD and LUSC as separate analysis tracks.
- Use KRAS, EGFR, MET, ALK, and MYC as driver-context examples, with mutation frequency and copy-number context shown side by side.
- Treat CD274, PDCD1, CTLA4, LAG3, TIGIT, and HAVCR2 as immune-context markers requiring single-cell validation for cell source.
- Use LuCA cell-type evidence to frame hypotheses about malignant, myeloid, lymphoid, stromal, and epithelial compartments.
- Use the Shiny app as the review layer and the SQL schema as the scalable backend pattern.

## App Scope

The Shiny app provides a demo-ready interface with searchable tables, interactive plots, dataset background, metric explanations, and caveats. It is designed for lightweight public deployment. It does not host raw human genomic files or large H5AD matrices.

## Recommended Next Step

Add a matrix-processing module that downloads LuCA H5AD files outside Git, computes gene-by-cell-type expression summaries for the curated panel, and writes compact tables back into the same schema.