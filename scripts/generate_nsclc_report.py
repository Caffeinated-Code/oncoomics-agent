#!/usr/bin/env python3
"""Generate compact report and SVG figures from the local SQL database."""

from __future__ import annotations

import html
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "oncoomics_nsclc.sqlite"
REPORT = ROOT / "results" / "nsclc_atlas_report.md"
FIGDIR = ROOT / "results" / "figures"


def query(conn: sqlite3.Connection, sql: str) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    return list(conn.execute(sql))


def markdown_table(rows: list[sqlite3.Row]) -> str:
    if not rows:
        return "No rows returned.\n"
    cols = rows[0].keys()
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row[col]) if row[col] is not None else "" for col in cols) + " |")
    return "\n".join(out) + "\n"


def bar_svg(rows: list[sqlite3.Row], label_col: str, value_col: str, title: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    width = 920
    row_h = 28
    left = 180
    top = 60
    height = top + row_h * len(rows) + 30
    max_value = max([float(row[value_col]) for row in rows] + [1.0])
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f7faf9"/>',
        f'<text x="24" y="34" font-family="Arial" font-size="22" font-weight="700" fill="#17384f">{html.escape(title)}</text>',
    ]
    for i, row in enumerate(rows):
        y = top + i * row_h
        value = float(row[value_col])
        label = str(row[label_col])
        bar_w = int((width - left - 90) * value / max_value)
        parts.append(f'<text x="24" y="{y + 18}" font-family="Arial" font-size="13" fill="#17201d">{html.escape(label)}</text>')
        parts.append(f'<rect x="{left}" y="{y + 5}" width="{bar_w}" height="17" fill="#2f7d5c"/>')
        parts.append(f'<text x="{left + bar_w + 8}" y="{y + 18}" font-family="Arial" font-size="13" fill="#17201d">{value:.3f}</text>')
    parts.append("</svg>")
    out.write_text("\n".join(parts), encoding="utf-8")


def main() -> int:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    counts = query(
        conn,
        """
SELECT 'datasets' AS table_name, COUNT(*) AS rows FROM datasets
UNION ALL SELECT 'samples', COUNT(*) FROM samples
UNION ALL SELECT 'genes', COUNT(*) FROM genes
UNION ALL SELECT 'expression_observations', COUNT(*) FROM expression_observations
UNION ALL SELECT 'mutation_observations', COUNT(*) FROM mutation_observations
UNION ALL SELECT 'cna_observations', COUNT(*) FROM cna_observations;
""",
    )
    drivers = query(
        conn,
        """
SELECT ms.cancer_type, g.symbol, ms.cancer_type || ' ' || g.symbol AS label, ms.mutated_samples, ms.sequenced_samples, ROUND(ms.mutation_frequency, 3) AS mutation_frequency
FROM mutation_summary ms
JOIN genes g ON g.gene_id = ms.gene_id
WHERE g.theme = 'tumor_driver'
ORDER BY ms.cancer_type, ms.mutation_frequency DESC
LIMIT 12;
""",
    )
    checkpoints = query(
        conn,
        """
SELECT ges.cancer_type, g.symbol, ges.n_samples, ROUND(ges.fraction_high_zscore, 3) AS fraction_high_zscore
FROM gene_expression_summary ges
JOIN genes g ON g.gene_id = ges.gene_id
WHERE g.theme = 'immune_checkpoint'
ORDER BY ges.cancer_type, ges.fraction_high_zscore DESC;
""",
    )
    cna = query(
        conn,
        """
SELECT cs.cancer_type || ' ' || g.symbol AS label, ROUND(cs.altered_fraction, 3) AS altered_fraction
FROM cna_summary cs
JOIN genes g ON g.gene_id = cs.gene_id
WHERE g.theme IN ('tumor_driver', 'immune_checkpoint', 'antigen_presentation')
ORDER BY cs.altered_fraction DESC
LIMIT 15;
""",
    )
    luca_meta = query(
        conn,
        """
SELECT title, cell_count, h5ad_filesize_gb, disease_labels
FROM luca_datasets
ORDER BY cell_count DESC;
""",
    )
    luca_evidence = query(
        conn,
        """
SELECT g.symbol, lct.cell_type_name, lct.compartment, e.expected_expression, e.quantitative_status
FROM luca_cell_type_gene_evidence e
JOIN genes g ON g.gene_id = e.gene_id
JOIN cell_types lct ON lct.cell_type_id = e.cell_type_id
WHERE g.symbol IN ('CD274', 'PDCD1', 'CTLA4', 'EGFR', 'VIM', 'SPP1', 'S100A8', 'MKI67')
ORDER BY g.symbol, lct.compartment, lct.cell_type_name;
""",
    )

    bar_svg(drivers, "label", "mutation_frequency", "Selected Tumor Driver Mutation Frequency", FIGDIR / "driver_mutation_frequency.svg")
    bar_svg(cna, "label", "altered_fraction", "Selected Gene Copy-Number Alteration Fraction", FIGDIR / "copy_number_alteration_fraction.svg")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "\n".join(
            [
                "# OncoOmics Agent NSCLC Atlas Report",
                "",
                "## Scope",
                "",
                "This v1 report builds a compact public NSCLC database from cBioPortal TCGA PanCancer LUAD and LUSC studies, then records LuCA and HLCA as single-cell atlas sources for the next curation layer.",
                "",
                "The database is intentionally summary-first. It stores gene-panel mutation, RNA expression z-score, and discrete copy-number summaries for fast SQL queries. Raw single-cell matrices remain outside the database.",
                "",
                "## Database Contents",
                "",
                markdown_table(counts),
                "## Driver Mutation Patterns",
                "",
                markdown_table(drivers),
                "LUAD shows the expected enrichment of `KRAS` and `EGFR` mutations in this selected panel. LUSC has lower frequencies for those LUAD-associated drivers, consistent with treating LUAD and LUSC as distinct biological contexts.",
                "",
                "![Driver mutation frequency](figures/driver_mutation_frequency.svg)",
                "",
                "## Immune Checkpoint RNA Context",
                "",
                markdown_table(checkpoints),
                "These are bulk tumor RNA z-score summaries. They support cohort-level immune-context questions but cannot identify the exact cell type producing each transcript. LuCA single-cell summaries are the correct next layer for cell-source resolution.",
                "",
                "## LuCA Cell-Type Context",
                "",
                markdown_table(luca_meta),
                "The LuCA collection is represented as public CELLxGENE metadata and a curated cell-type evidence layer in this v1 database. The H5AD assets are large, so quantitative matrix extraction is kept as the scalable next step.",
                "",
                markdown_table(luca_evidence),
                "This table is designed for transparent agent behavior. It can answer compartment-level questions now while marking the quantitative status of each statement.",
                "",
                "## Copy-Number Context",
                "",
                markdown_table(cna),
                "Discrete GISTIC values are useful screening features. They should be interpreted with mutation, expression, focality, purity, and histology context.",
                "",
                "![Copy-number alteration fraction](figures/copy_number_alteration_fraction.svg)",
                "",
                "## Current Biological Interpretation",
                "",
                "- The project now has a real SQL-backed NSCLC molecular context using public LUAD and LUSC data.",
                "- The strongest v1 signal is disease-aware separation of LUAD and LUSC driver biology.",
                "- Checkpoint and myeloid RNA summaries should be treated as tumor-level context until single-cell LuCA summaries are ingested.",
                "- The LuCA evidence layer enables cell-compartment reasoning, with explicit status labels for matrix-derived versus curated evidence.",
                "- Multi-omics in v1 means mutation, RNA expression, copy number, source provenance, and single-cell atlas source mapping.",
                "",
                "## Next Data Layer",
                "",
                "The next implementation step is to ingest LuCA-derived cell-type expression summaries for the same gene panel. That will allow the agent to answer which malignant, immune, or stromal cell compartments express each marker.",
            ]
        ),
        encoding="utf-8",
    )
    conn.close()
    print(f"Wrote report to {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
