#!/usr/bin/env python3
"""Generate a concise scientific and product-facing report for the Shiny demo."""

from __future__ import annotations

import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "oncoomics_nsclc.sqlite"
OUT = ROOT / "results" / "oncoomics_nsclc_action_report.md"


def rows(conn: sqlite3.Connection, sql: str) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    return list(conn.execute(sql))


def table(rs: list[sqlite3.Row]) -> str:
    if not rs:
        return "No rows returned.\n"
    cols = rs[0].keys()
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for row in rs:
        lines.append("| " + " | ".join(str(row[col]) if row[col] is not None else "" for col in cols) + " |")
    return "\n".join(lines) + "\n"


def main() -> int:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    database_counts = rows(
        conn,
        """
SELECT 'samples' AS entity, COUNT(*) AS count FROM samples
UNION ALL SELECT 'genes', COUNT(*) FROM genes
UNION ALL SELECT 'expression observations', COUNT(*) FROM expression_observations
UNION ALL SELECT 'mutation observations', COUNT(*) FROM mutation_observations
UNION ALL SELECT 'copy-number observations', COUNT(*) FROM cna_observations
UNION ALL SELECT 'LuCA cell types', COUNT(*) FROM cell_types
UNION ALL SELECT 'LuCA gene-cell evidence rows', COUNT(*) FROM luca_cell_type_gene_evidence;
""",
    )
    drivers = rows(
        conn,
        """
SELECT ms.cancer_type, g.symbol, ms.mutated_samples, ms.sequenced_samples,
       ROUND(ms.mutation_frequency, 3) AS mutation_frequency,
       ms.recurrent_protein_changes
FROM mutation_summary ms
JOIN genes g ON g.gene_id = ms.gene_id
WHERE g.theme = 'tumor_driver'
ORDER BY ms.cancer_type, ms.mutation_frequency DESC;
""",
    )
    checkpoints = rows(
        conn,
        """
SELECT ges.cancer_type, g.symbol, ges.n_samples,
       ROUND(ges.fraction_high_zscore, 3) AS fraction_high_zscore
FROM gene_expression_summary ges
JOIN genes g ON g.gene_id = ges.gene_id
WHERE g.theme = 'immune_checkpoint'
ORDER BY ges.cancer_type, ges.fraction_high_zscore DESC;
""",
    )
    luca = rows(
        conn,
        """
SELECT g.symbol, c.cell_type_name, c.compartment, e.expected_expression, e.quantitative_status
FROM luca_cell_type_gene_evidence e
JOIN genes g ON g.gene_id = e.gene_id
JOIN cell_types c ON c.cell_type_id = e.cell_type_id
WHERE g.symbol IN ('CD274', 'PDCD1', 'CTLA4', 'EGFR', 'KRAS', 'VIM', 'SPP1', 'S100A8')
ORDER BY g.symbol, c.compartment, c.cell_type_name;
""",
    )
    luca_datasets = rows(
        conn,
        """
SELECT title, cell_count, h5ad_filesize_gb, disease_labels
FROM luca_datasets
ORDER BY cell_count DESC;
""",
    )

    OUT.write_text(
        "\n".join(
            [
                "# OncoOmics Agent: NSCLC Atlas Action Report",
                "",
                "## Executive Summary",
                "",
                "This project now has a compact, reproducible NSCLC atlas database and a Shiny demo app for interactive review. The current build integrates public TCGA LUAD/LUSC mutation, RNA expression, and copy-number summaries with LuCA single-cell atlas metadata and curated gene-by-cell-type evidence.",
                "",
                "The main value is fast biological triage. A user can compare LUAD and LUSC driver patterns, inspect checkpoint expression context, review copy-number alteration signals, and connect selected markers to plausible LuCA cell compartments.",
                "",
                "## Database Coverage",
                "",
                table(database_counts),
                "## Key Biological Findings",
                "",
                "### Driver Landscape",
                "",
                table(drivers),
                "KRAS and EGFR are more prominent in LUAD than LUSC in this selected gene panel. This supports histology-aware interpretation and prevents mixing LUAD and LUSC into one generic NSCLC signal.",
                "",
                "### Immune Checkpoint RNA Context",
                "",
                table(checkpoints),
                "Checkpoint RNA summaries are useful for cohort-level screening. They remain bulk tumor measurements and should not be interpreted as cell-source-resolved signals.",
                "",
                "### LuCA Cell-Type Context",
                "",
                table(luca_datasets),
                table(luca),
                "The LuCA layer gives the app a cell-compartment interpretation path. The current evidence table is curated and transparent. The next data layer should compute expression summaries directly from the LuCA H5AD matrices.",
                "",
                "## Actionable Insights",
                "",
                "- Prioritize LUAD and LUSC as separate analysis tracks.",
                "- Use KRAS, EGFR, MET, ALK, and MYC as driver-context examples, with mutation frequency and copy-number context shown side by side.",
                "- Treat CD274, PDCD1, CTLA4, LAG3, TIGIT, and HAVCR2 as immune-context markers requiring single-cell validation for cell source.",
                "- Use LuCA cell-type evidence to frame hypotheses about malignant, myeloid, lymphoid, stromal, and epithelial compartments.",
                "- Use the Shiny app as the review layer and the SQL schema as the scalable backend pattern.",
                "",
                "## App Scope",
                "",
                "The Shiny app provides a demo-ready interface with searchable tables, interactive plots, dataset background, metric explanations, and caveats. It is designed for lightweight public deployment. It does not host raw human genomic files or large H5AD matrices.",
                "",
                "## Recommended Next Step",
                "",
                "Add a matrix-processing module that downloads LuCA H5AD files outside Git, computes gene-by-cell-type expression summaries for the curated panel, and writes compact tables back into the same schema.",
            ]
        ),
        encoding="utf-8",
    )
    conn.close()
    print(f"Wrote action report to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
