# OncoOmics Agent Shiny Demo

This app summarizes the current NSCLC atlas build:

- TCGA LUAD/LUSC mutation frequency
- TCGA LUAD/LUSC bulk RNA expression context
- TCGA LUAD/LUSC discrete GISTIC copy-number context
- LuCA metadata and curated cell-type evidence

Public demo:

- https://caffeinated-code.shinyapps.io/oncoomics-agent-nsclc-atlas/

Run locally:

```r
shiny::runApp("shiny_app")
```

Refresh the deployable app data bundle:

```bash
python3 scripts/prepare_shiny_app_data.py
```

The app is intentionally summary-first. It does not download or host the full LuCA H5AD matrices.
