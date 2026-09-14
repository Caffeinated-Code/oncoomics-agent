#!/usr/bin/env python3
"""Build a local SQLite copy of the OncoOmics summary database."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "curated"
DB_PATH = ROOT / "oncoomics_nsclc.sqlite"

TABLE_FILES = [
    ("datasets", "datasets.csv"),
    ("source_files", "source_files.csv"),
    ("genes", "genes.csv"),
    ("samples", "samples.csv"),
    ("molecular_profiles", "molecular_profiles.csv"),
    ("expression_observations", "expression_observations.csv"),
    ("gene_expression_summary", "gene_expression_summary.csv"),
    ("mutation_observations", "mutation_observations.csv"),
    ("mutation_summary", "mutation_summary.csv"),
    ("cna_observations", "cna_observations.csv"),
    ("cna_summary", "cna_summary.csv"),
    ("atlas_source_summaries", "atlas_source_summaries.csv"),
    ("luca_datasets", "luca_datasets.csv"),
    ("cell_types", "cell_types.csv"),
    ("luca_cell_type_gene_evidence", "luca_cell_type_gene_evidence.csv"),
]

CANNED_QUESTIONS = [
    {
        "question_id": "top_mutated_drivers",
        "question": "Which driver genes are most frequently mutated in TCGA LUAD and LUSC?",
        "sql_text": """
SELECT ms.cancer_type, g.symbol, g.theme, ms.mutated_samples, ms.sequenced_samples, ROUND(ms.mutation_frequency, 3) AS mutation_frequency
FROM mutation_summary ms
JOIN genes g ON g.gene_id = ms.gene_id
WHERE g.theme = 'tumor_driver'
ORDER BY ms.cancer_type, ms.mutation_frequency DESC
LIMIT 20;
""".strip(),
        "interpretation_note": "Use this to compare expected LUAD-enriched KRAS/EGFR biology against LUSC-heavy mutation patterns.",
    },
    {
        "question_id": "checkpoint_expression",
        "question": "Which immune checkpoint genes have high RNA z-score fractions in LUAD and LUSC?",
        "sql_text": """
SELECT ges.cancer_type, g.symbol, ges.n_samples, ROUND(ges.mean_zscore, 3) AS mean_zscore, ROUND(ges.fraction_high_zscore, 3) AS fraction_high_zscore
FROM gene_expression_summary ges
JOIN genes g ON g.gene_id = ges.gene_id
WHERE g.theme = 'immune_checkpoint'
ORDER BY ges.cancer_type, ges.fraction_high_zscore DESC;
""".strip(),
        "interpretation_note": "Bulk tumor RNA can reflect tumor, immune, and stromal compartments. Single-cell LuCA is needed to assign cell source.",
    },
    {
        "question_id": "copy_number_hotspots",
        "question": "Which selected genes have the highest copy-number alteration fractions?",
        "sql_text": """
SELECT cs.cancer_type, g.symbol, g.theme, cs.n_samples, ROUND(cs.altered_fraction, 3) AS altered_fraction, ROUND(cs.amplification_fraction, 3) AS amplification_fraction
FROM cna_summary cs
JOIN genes g ON g.gene_id = cs.gene_id
ORDER BY cs.cancer_type, cs.altered_fraction DESC
LIMIT 20;
""".strip(),
        "interpretation_note": "Discrete GISTIC calls summarize copy-number state. Pair this with RNA and mutation evidence before assigning biological importance.",
    },
    {
        "question_id": "myeloid_programs",
        "question": "Which inflammatory myeloid genes are most prominent by cohort-level RNA z-score?",
        "sql_text": """
SELECT ges.cancer_type, g.symbol, ROUND(ges.median_zscore, 3) AS median_zscore, ROUND(ges.fraction_high_zscore, 3) AS fraction_high_zscore
FROM gene_expression_summary ges
JOIN genes g ON g.gene_id = ges.gene_id
WHERE g.theme = 'myeloid_inflammation'
ORDER BY ges.cancer_type, ges.fraction_high_zscore DESC;
""".strip(),
        "interpretation_note": "These are cohort-level RNA patterns. Cell-type localization should be checked against single-cell summaries.",
    },
    {
        "question_id": "luca_cell_type_checkpoint_context",
        "question": "Which LuCA cell types are expected to express immune checkpoint genes?",
        "sql_text": """
SELECT g.symbol, lct.cell_type_name, lct.compartment, e.expected_expression, e.quantitative_status
FROM luca_cell_type_gene_evidence e
JOIN genes g ON g.gene_id = e.gene_id
JOIN cell_types lct ON lct.cell_type_id = e.cell_type_id
WHERE g.theme = 'immune_checkpoint'
ORDER BY g.symbol, e.expected_expression, lct.cell_type_name
LIMIT 30;
""".strip(),
        "interpretation_note": "This table is a curated LuCA cell-type evidence layer. Quantitative LuCA expression extraction is the next large-matrix processing step.",
    },
]


def load_csv(conn: sqlite3.Connection, table: str, path: Path) -> None:
    table_columns = {
        row[1]
        for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    }
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        if not rows:
            return
        columns = [col for col in (reader.fieldnames or []) if col in table_columns]
    placeholders = ", ".join(["?"] * len(columns))
    column_sql = ", ".join(columns)
    values = [[row[col] for col in columns] for row in rows]
    conn.executemany(f"INSERT OR REPLACE INTO {table} ({column_sql}) VALUES ({placeholders})", values)


def main() -> int:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    with (ROOT / "sql" / "schema.sql").open() as handle:
        conn.executescript(handle.read())
    for table, filename in TABLE_FILES:
        load_csv(conn, table, CURATED / filename)
    conn.executemany(
        "INSERT OR REPLACE INTO canned_questions (question_id, question, sql_text, interpretation_note) VALUES (:question_id, :question, :sql_text, :interpretation_note)",
        CANNED_QUESTIONS,
    )
    conn.commit()
    conn.close()
    print(f"Wrote SQLite database to {DB_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
