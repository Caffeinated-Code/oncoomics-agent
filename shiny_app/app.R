library(shiny)
library(bslib)
library(DT)
library(plotly)
library(ggplot2)
library(dplyr)
library(readr)
library(stringr)
library(scales)

options(shiny.maxRequestSize = 30 * 1024^2)

app_version <- "NSCLC Atlas demo v1"
data_dir <- file.path(getwd(), "data")

read_table <- function(name) {
  readr::read_csv(file.path(data_dir, name), show_col_types = FALSE, progress = FALSE)
}

datasets <- read_table("datasets.csv")
atlas_sources <- read_table("atlas_source_summaries.csv")
samples <- read_table("samples.csv")
mutation_summary <- read_table("mutation_summary.csv")
expression_summary <- read_table("gene_expression_summary.csv")
cna_summary <- read_table("cna_summary.csv")
luca_datasets <- read_table("luca_datasets.csv")
cell_types <- read_table("cell_types.csv")
luca_evidence <- read_table("luca_cell_type_gene_evidence.csv")
gene_panel <- read_table("gene_panel.csv")

theme_labels <- gene_panel |>
  distinct(theme) |>
  arrange(theme) |>
  pull(theme)

info_text <- list(
  mutation_frequency = "Fraction of sequenced samples with a mutation in the selected gene. Interpret by histology because LUAD and LUSC have different driver landscapes.",
  fraction_high_zscore = "Fraction of tumor samples with RNA expression z-score >= 1 for the selected gene. This is bulk tumor RNA, so it does not identify the exact producing cell type.",
  altered_fraction = "Fraction of samples with any non-neutral discrete GISTIC copy-number call for the selected gene. This is a screening signal and should be paired with expression, focality, purity, and histology context.",
  luca_evidence = "Curated LuCA cell-type evidence links genes to plausible cell compartments. Values marked not_matrix_quantified_in_v1 are evidence-backed but not yet computed from the full LuCA H5AD matrix.",
  multiomics = "This demo integrates mutation, RNA expression, copy number, source provenance, and single-cell atlas context in one small SQL-ready project.",
  tcga = "TCGA LUAD and LUSC PanCancer Atlas studies provide public cohort-scale mutation, RNA expression, and copy-number context for lung adenocarcinoma and lung squamous cell carcinoma.",
  luca = "LuCA is a single-cell lung cancer atlas. In this demo it contributes dataset metadata, cell-type labels, compartment mapping, and curated gene-cell evidence.",
  hlca = "HLCA is a healthy and diseased lung reference atlas. It anchors future normal-lung comparisons and helps keep NSCLC cell-state interpretation biologically grounded."
)

metric_help <- function(id, label) {
  actionLink(id, label, class = "metric-link")
}

value_box <- function(label, value, note = NULL) {
  div(
    class = "value-box",
    div(class = "value-label", label),
    div(class = "value-number", value),
    if (!is.null(note)) div(class = "value-note", note)
  )
}

clean_pct <- function(x) scales::percent(x, accuracy = 0.1)

plot_theme <- theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(face = "bold", color = "#16324f"),
    axis.title = element_text(color = "#23312d"),
    panel.grid.minor = element_blank(),
    legend.position = "bottom"
  )

ui <- page_navbar(
  title = div(class = "brand-title", "OncoOmics Agent", span("NSCLC Atlas Edition")),
  theme = bs_theme(
    version = 5,
    bootswatch = "flatly",
    primary = "#2f6f73",
    secondary = "#67597a",
    success = "#2f7d5c",
    warning = "#b5792a",
    danger = "#a34040",
    base_font = font_google("Inter"),
    heading_font = font_google("Source Sans 3")
  ),
  header = tags$head(
    tags$style(HTML("
      body { background: #f6f8f6; color: #17201d; }
      .navbar { box-shadow: 0 1px 12px rgba(17, 34, 33, 0.08); }
      .navbar .nav-link { color: rgba(255,255,255,.92) !important; font-weight: 700; border-radius: 4px; margin: 0 2px; }
      .navbar .nav-link:hover, .navbar .nav-link:focus { background: rgba(255,255,255,.16) !important; color: #ffffff !important; }
      .navbar .nav-link.active, .navbar .show > .nav-link { background: #f4c95d !important; color: #142521 !important; box-shadow: inset 0 -3px 0 #9a5f17; }
      .brand-title { font-weight: 800; letter-spacing: 0; }
      .brand-title span { font-weight: 600; margin-left: .45rem; color: #dfeee8; }
      .app-hero { background: linear-gradient(135deg, #17384f, #2f6f73 55%, #67597a); color: white; padding: 28px; border-radius: 6px; margin-bottom: 18px; }
      .app-hero h2 { margin: 0 0 8px 0; font-weight: 800; }
      .app-hero p { max-width: 980px; margin: 0; font-size: 1.02rem; }
      .panel { background: white; border: 1px solid #d7e4de; border-radius: 6px; padding: 18px; margin-bottom: 16px; box-shadow: 0 1px 8px rgba(20, 40, 38, 0.04); }
      .panel h3, .panel h4 { color: #17384f; font-weight: 800; }
      .value-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; margin: 16px 0; }
      .value-box { background: #fbfcfb; border: 1px solid #cfe0d9; border-left: 5px solid #2f6f73; border-radius: 6px; padding: 14px; min-height: 112px; }
      .dataset-card { border-left-color: #67597a; }
      .value-label { color: #566662; font-weight: 700; font-size: .92rem; }
      .value-number { font-size: 2rem; color: #17201d; font-weight: 850; line-height: 1.2; overflow-wrap: anywhere; }
      .value-note { color: #5f6f69; font-size: .86rem; margin-top: 6px; }
      .insight-list li { margin-bottom: 8px; }
      .metric-link { font-weight: 800; color: #2f6f73; text-decoration: underline; cursor: pointer; }
      .selectize-input, .form-control { border-color: #b9cbc4; }
      .dataTables_wrapper { font-size: .92rem; }
      .status-chip { display: inline-block; border-radius: 999px; padding: 3px 9px; background: #e8f2ee; color: #1e5a42; font-weight: 750; margin-left: 6px; }
      @media (max-width: 760px) {
        .app-hero { padding: 20px; }
        .value-number { font-size: 1.55rem; }
      }
    "))
  ),
  nav_panel(
    "Demo",
    div(
      class = "app-hero",
      h2("NSCLC multi-omics atlas demo"),
      p("Explore public LUAD and LUSC mutation, RNA, copy-number, and LuCA cell-type context from one compact database-ready project.")
    ),
    div(
      class = "value-grid",
      value_box("TCGA samples", format(nrow(samples), big.mark = ","), "LUAD and LUSC sample records"),
      value_box("Curated genes", nrow(gene_panel), "Driver, checkpoint, myeloid, EMT, hypoxia, antigen-presentation, proliferation"),
      value_box("LuCA cells represented", format(sum(luca_datasets$cell_count), big.mark = ","), "Public CELLxGENE metadata"),
      value_box("LuCA cell types", nrow(cell_types), "Mapped to broad compartments")
    ),
    div(
      class = "panel",
      h3("Dataset background"),
      p("The demo uses public, processed datasets that are small enough for a review app and structured enough to become a database-backed analysis system."),
      div(
        class = "value-grid",
        div(
          class = "value-box dataset-card",
          div(class = "value-label", metric_help("help_tcga", "TCGA PanCancer LUAD/LUSC")),
          div(class = "value-note", "Primary use: cohort-scale molecular context for NSCLC histologies. The app uses mutation frequency, bulk RNA z-score summaries, and discrete GISTIC copy-number calls.")
        ),
        div(
          class = "value-box dataset-card",
          div(class = "value-label", metric_help("help_luca", "LuCA single-cell Lung Cancer Atlas")),
          div(class = "value-note", "Primary use: NSCLC cell-type and tumor microenvironment context. The app uses LuCA metadata, 33 public cell-type labels, broad compartments, and curated gene-cell evidence.")
        ),
        div(
          class = "value-box dataset-card",
          div(class = "value-label", metric_help("help_hlca", "Human Lung Cell Atlas")),
          div(class = "value-note", "Primary use: reference lung biology. HLCA is recorded as the normal-lung comparison layer for future cell-state and disease-context extensions.")
        )
      )
    ),
    div(
      class = "panel",
      h3("Actionable readout"),
      tags$ul(
        class = "insight-list",
        tags$li("Analyze LUAD and LUSC separately. KRAS and EGFR signals are much stronger in LUAD in this selected public panel."),
        tags$li("Treat checkpoint RNA as tumor-level context until quantitative single-cell LuCA expression summaries are computed."),
        tags$li("Use the LuCA evidence table to connect genes to plausible cell compartments, then prioritize full matrix extraction for high-value markers."),
        tags$li("Use copy-number results as screening signals. Pair them with mutation, RNA, histology, purity, and focality before biological claims."),
        tags$li("The app is a demo of the database and analysis pattern. The same structure can be deployed behind AWS RDS, S3, and a read-only API.")
      )
    ),
    div(
      class = "panel",
      h3("What the demo integrates"),
      fluidRow(
        column(6, tags$strong("Molecular layers"), tags$ul(tags$li("Mutation frequency"), tags$li("RNA z-score summaries"), tags$li("Discrete GISTIC copy-number summaries"))),
        column(6, tags$strong("Atlas layers"), tags$ul(tags$li("LuCA dataset metadata"), tags$li("Cell-type ontology labels"), tags$li("Curated gene-by-cell-type evidence")))
      )
    )
  ),
  nav_panel(
    "Drivers",
    layout_sidebar(
      sidebar = sidebar(
        selectInput("driver_histology", "Cancer type", choices = c("All", sort(unique(mutation_summary$cancer_type))), selected = "All"),
        selectInput("driver_theme", "Gene theme", choices = c("All", theme_labels), selected = "tumor_driver"),
        sliderInput("driver_top_n", "Genes to show", min = 5, max = 30, value = 15)
      ),
      div(
        class = "panel",
        h3("Mutation frequency"),
        p(metric_help("help_mutation_frequency", "mutation_frequency"), " shows recurrent driver context by histology."),
        plotlyOutput("driver_plot", height = "520px")
      ),
      div(class = "panel", h3("Driver table"), DTOutput("driver_table"))
    )
  ),
  nav_panel(
    "Checkpoint RNA",
    layout_sidebar(
      sidebar = sidebar(
        selectInput("expr_theme", "Gene theme", choices = c("All", theme_labels), selected = "immune_checkpoint"),
        selectInput("expr_histology", "Cancer type", choices = c("All", sort(unique(expression_summary$cancer_type))), selected = "All")
      ),
      div(
        class = "panel",
        h3("High-expression fraction"),
        p(metric_help("help_fraction_high_zscore", "fraction_high_zscore"), " gives a cohort-level expression screen."),
        plotlyOutput("expression_plot", height = "520px")
      ),
      div(class = "panel", h3("Expression table"), DTOutput("expression_table"))
    )
  ),
  nav_panel(
    "CNA",
    layout_sidebar(
      sidebar = sidebar(
        selectInput("cna_theme", "Gene theme", choices = c("All", theme_labels), selected = "All"),
        selectInput("cna_histology", "Cancer type", choices = c("All", sort(unique(cna_summary$cancer_type))), selected = "All")
      ),
      div(
        class = "panel",
        h3("Copy-number alteration fraction"),
        p(metric_help("help_altered_fraction", "altered_fraction"), " is best treated as a prioritization feature."),
        plotlyOutput("cna_plot", height = "520px")
      ),
      div(class = "panel", h3("Copy-number table"), DTOutput("cna_table"))
    )
  ),
  nav_panel(
    "LuCA Context",
    layout_sidebar(
      sidebar = sidebar(
        selectizeInput("luca_gene", "Gene", choices = sort(unique(luca_evidence$symbol)), selected = "CD274"),
        selectInput("luca_compartment", "Compartment", choices = c("All", sort(unique(luca_evidence$compartment))), selected = "All")
      ),
      div(
        class = "panel",
        h3("Cell-type evidence", span(class = "status-chip", "curated v1")),
        p(metric_help("help_luca_evidence", "LuCA evidence"), " connects genes to likely cellular sources and marks whether matrix quantification is complete."),
        DTOutput("luca_table")
      ),
      div(
        class = "panel",
        h3("LuCA compartment map"),
        plotlyOutput("luca_plot", height = "460px")
      ),
      div(class = "panel", h3("LuCA datasets"), DTOutput("luca_dataset_table"))
    )
  ),
  nav_panel(
    "Data",
    div(
      class = "panel",
      h3("Search all result tables"),
      tabsetPanel(
        tabPanel("Datasets", DTOutput("datasets_table")),
        tabPanel("Genes", DTOutput("genes_table")),
        tabPanel("Cell types", DTOutput("cell_types_table")),
        tabPanel("Atlas sources", DTOutput("atlas_table"))
      )
    )
  ),
  nav_panel(
    "Methods",
    div(
      class = "panel",
      h3("Methods and caveats"),
      tags$p(metric_help("help_multiomics", "Multi-omics scope"), " in this demo means mutation, RNA expression, copy-number, provenance, and single-cell atlas context."),
      tags$h4("Data sources"),
      tags$ul(
        tags$li("TCGA LUAD and LUSC PanCancer Atlas summaries from cBioPortal."),
        tags$li("LuCA CELLxGENE collection metadata and public cell-type labels."),
        tags$li("HLCA recorded as a reference source for future normal-lung comparison.")
      ),
      tags$h4("Current limitations"),
      tags$ul(
        tags$li("LuCA H5AD matrices are not downloaded into this demo app."),
        tags$li("Cell-type evidence is curated and explicitly labeled until matrix-derived expression is added."),
        tags$li("Bulk RNA cannot resolve which cell type produces a transcript."),
        tags$li("Copy-number summaries are discrete GISTIC screens and need focality-aware follow-up.")
      ),
      tags$h4("Next scalable implementation"),
      tags$p("Use S3 for curated files, AWS Batch or ECS for matrix extraction, RDS PostgreSQL for summary tables, and a read-only API for app and agent queries.")
    )
  )
)

server <- function(input, output, session) {
  show_help <- function(title, text) {
    showModal(modalDialog(title = title, easyClose = TRUE, footer = modalButton("Close"), p(text)))
  }
  observeEvent(input$help_mutation_frequency, show_help("mutation_frequency", info_text$mutation_frequency))
  observeEvent(input$help_fraction_high_zscore, show_help("fraction_high_zscore", info_text$fraction_high_zscore))
  observeEvent(input$help_altered_fraction, show_help("altered_fraction", info_text$altered_fraction))
  observeEvent(input$help_luca_evidence, show_help("LuCA evidence", info_text$luca_evidence))
  observeEvent(input$help_multiomics, show_help("Multi-omics scope", info_text$multiomics))
  observeEvent(input$help_tcga, show_help("TCGA PanCancer LUAD/LUSC", info_text$tcga))
  observeEvent(input$help_luca, show_help("LuCA single-cell Lung Cancer Atlas", info_text$luca))
  observeEvent(input$help_hlca, show_help("Human Lung Cell Atlas", info_text$hlca))

  filtered_mutations <- reactive({
    x <- mutation_summary |> left_join(gene_panel |> select(symbol, theme), by = "symbol")
    if (input$driver_histology != "All") x <- x |> filter(cancer_type == input$driver_histology)
    if (input$driver_theme != "All") x <- x |> filter(theme.x == input$driver_theme | theme.y == input$driver_theme)
    x |> mutate(label = paste(cancer_type, symbol), mutation_frequency_pct = clean_pct(mutation_frequency)) |>
      arrange(desc(mutation_frequency)) |>
      slice_head(n = input$driver_top_n)
  })

  output$driver_plot <- renderPlotly({
    p <- filtered_mutations() |>
      mutate(label = reorder(label, mutation_frequency)) |>
      ggplot(aes(x = mutation_frequency, y = label, fill = cancer_type, text = paste0(symbol, "<br>", cancer_type, "<br>Mutation frequency: ", clean_pct(mutation_frequency), "<br>Mutated samples: ", mutated_samples, "/", sequenced_samples))) +
      geom_col(width = 0.72) +
      scale_x_continuous(labels = percent_format(accuracy = 1)) +
      scale_fill_manual(values = c(LUAD = "#2f6f73", LUSC = "#67597a")) +
      labs(x = "Mutation frequency", y = NULL, title = "Selected mutation frequencies") +
      plot_theme
    ggplotly(p, tooltip = "text") |> layout(margin = list(l = 120))
  })

  output$driver_table <- renderDT({
    filtered_mutations() |>
      transmute(cancer_type, symbol, theme = coalesce(theme.x, theme.y), mutated_samples, sequenced_samples, mutation_frequency = round(mutation_frequency, 4), recurrent_protein_changes) |>
      datatable(rownames = FALSE, filter = "top", extensions = "Buttons", options = list(pageLength = 10, scrollX = TRUE, dom = "Bfrtip", buttons = c("copy", "csv")))
  })

  filtered_expression <- reactive({
    x <- expression_summary |> left_join(gene_panel |> select(symbol, theme), by = "symbol")
    if (input$expr_histology != "All") x <- x |> filter(cancer_type == input$expr_histology)
    if (input$expr_theme != "All") x <- x |> filter(theme.x == input$expr_theme | theme.y == input$expr_theme)
    x |> mutate(label = paste(cancer_type, symbol)) |> arrange(desc(fraction_high_zscore))
  })

  output$expression_plot <- renderPlotly({
    p <- filtered_expression() |>
      slice_head(n = 24) |>
      mutate(label = reorder(label, fraction_high_zscore)) |>
      ggplot(aes(x = fraction_high_zscore, y = label, fill = cancer_type, text = paste0(symbol, "<br>", cancer_type, "<br>High z-score fraction: ", clean_pct(fraction_high_zscore), "<br>Mean z-score: ", round(mean_zscore, 3)))) +
      geom_col(width = 0.72) +
      scale_x_continuous(labels = percent_format(accuracy = 1)) +
      scale_fill_manual(values = c(LUAD = "#2f6f73", LUSC = "#67597a")) +
      labs(x = "Fraction of samples with z-score >= 1", y = NULL, title = "Bulk RNA expression screen") +
      plot_theme
    ggplotly(p, tooltip = "text") |> layout(margin = list(l = 130))
  })

  output$expression_table <- renderDT({
    filtered_expression() |>
      transmute(cancer_type, symbol, theme = coalesce(theme.x, theme.y), n_samples, mean_zscore = round(mean_zscore, 4), median_zscore = round(median_zscore, 4), fraction_high_zscore = round(fraction_high_zscore, 4)) |>
      datatable(rownames = FALSE, filter = "top", extensions = "Buttons", options = list(pageLength = 12, scrollX = TRUE, dom = "Bfrtip", buttons = c("copy", "csv")))
  })

  filtered_cna <- reactive({
    x <- cna_summary |> left_join(gene_panel |> select(symbol, theme), by = "symbol")
    if (input$cna_histology != "All") x <- x |> filter(cancer_type == input$cna_histology)
    if (input$cna_theme != "All") x <- x |> filter(theme.x == input$cna_theme | theme.y == input$cna_theme)
    x |> mutate(label = paste(cancer_type, symbol)) |> arrange(desc(altered_fraction))
  })

  output$cna_plot <- renderPlotly({
    p <- filtered_cna() |>
      slice_head(n = 24) |>
      mutate(label = reorder(label, altered_fraction)) |>
      ggplot(aes(x = altered_fraction, y = label, fill = cancer_type, text = paste0(symbol, "<br>", cancer_type, "<br>Altered fraction: ", clean_pct(altered_fraction), "<br>Gain: ", clean_pct(gain_fraction), "<br>Amplification: ", clean_pct(amplification_fraction)))) +
      geom_col(width = 0.72) +
      scale_x_continuous(labels = percent_format(accuracy = 1)) +
      scale_fill_manual(values = c(LUAD = "#2f6f73", LUSC = "#67597a")) +
      labs(x = "Any non-neutral discrete CNA", y = NULL, title = "Copy-number alteration screen") +
      plot_theme
    ggplotly(p, tooltip = "text") |> layout(margin = list(l = 130))
  })

  output$cna_table <- renderDT({
    filtered_cna() |>
      transmute(cancer_type, symbol, theme = coalesce(theme.x, theme.y), n_samples, altered_fraction = round(altered_fraction, 4), gain_fraction = round(gain_fraction, 4), amplification_fraction = round(amplification_fraction, 4), deep_deletion_fraction = round(deep_deletion_fraction, 4)) |>
      datatable(rownames = FALSE, filter = "top", extensions = "Buttons", options = list(pageLength = 12, scrollX = TRUE, dom = "Bfrtip", buttons = c("copy", "csv")))
  })

  filtered_luca <- reactive({
    x <- luca_evidence
    if (!is.null(input$luca_gene) && length(input$luca_gene) > 0) x <- x |> filter(symbol %in% input$luca_gene)
    if (input$luca_compartment != "All") x <- x |> filter(compartment == input$luca_compartment)
    x |> arrange(symbol, compartment, cell_type_name)
  })

  output$luca_table <- renderDT({
    filtered_luca() |>
      select(symbol, cell_type_name, compartment, expected_expression, quantitative_status, biological_rationale) |>
      datatable(rownames = FALSE, filter = "top", extensions = "Buttons", options = list(pageLength = 12, scrollX = TRUE, dom = "Bfrtip", buttons = c("copy", "csv")))
  })

  output$luca_plot <- renderPlotly({
    x <- filtered_luca() |> count(compartment, expected_expression, name = "evidence_rows")
    p <- ggplot(x, aes(x = compartment, y = evidence_rows, fill = expected_expression, text = paste0(compartment, "<br>", expected_expression, ": ", evidence_rows, " rows"))) +
      geom_col(position = "stack", width = 0.7) +
      scale_fill_manual(values = c("high" = "#2f6f73", "moderate" = "#6aa88c", "context-dependent" = "#67597a")) +
      labs(x = NULL, y = "Evidence rows", title = "Gene evidence by LuCA compartment") +
      plot_theme +
      theme(axis.text.x = element_text(angle = 20, hjust = 1))
    ggplotly(p, tooltip = "text")
  })

  output$luca_dataset_table <- renderDT({
    luca_datasets |>
      transmute(title, cell_count, h5ad_filesize_gb, disease_labels, tissue_labels, assay_labels, collection_url) |>
      datatable(rownames = FALSE, filter = "top", extensions = "Buttons", options = list(pageLength = 5, scrollX = TRUE, dom = "Bfrtip", buttons = c("copy", "csv")))
  })

  output$datasets_table <- renderDT(datatable(datasets, rownames = FALSE, filter = "top", extensions = "Buttons", options = list(pageLength = 10, scrollX = TRUE, dom = "Bfrtip", buttons = c("copy", "csv"))))
  output$genes_table <- renderDT(datatable(gene_panel, rownames = FALSE, filter = "top", extensions = "Buttons", options = list(pageLength = 12, scrollX = TRUE, dom = "Bfrtip", buttons = c("copy", "csv"))))
  output$cell_types_table <- renderDT(datatable(cell_types, rownames = FALSE, filter = "top", extensions = "Buttons", options = list(pageLength = 12, scrollX = TRUE, dom = "Bfrtip", buttons = c("copy", "csv"))))
  output$atlas_table <- renderDT(datatable(atlas_sources, rownames = FALSE, filter = "top", extensions = "Buttons", options = list(pageLength = 5, scrollX = TRUE, dom = "Bfrtip", buttons = c("copy", "csv"))))
}

shinyApp(ui, server)
