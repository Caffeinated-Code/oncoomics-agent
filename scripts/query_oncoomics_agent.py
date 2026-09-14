#!/usr/bin/env python3
"""Small read-only SQL agent for the local OncoOmics database."""

from __future__ import annotations

import argparse
import re
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "oncoomics_nsclc.sqlite"


QUESTION_MAP = [
    (
        ("driver", "mutat"),
        """
SELECT ms.cancer_type, g.symbol, g.theme, ms.mutated_samples, ms.sequenced_samples, ROUND(ms.mutation_frequency, 3) AS mutation_frequency, ms.recurrent_protein_changes
FROM mutation_summary ms
JOIN genes g ON g.gene_id = ms.gene_id
WHERE g.theme = 'tumor_driver'
ORDER BY ms.cancer_type, ms.mutation_frequency DESC
LIMIT 20;
""".strip(),
        "LUAD and LUSC should be interpreted separately. EGFR and KRAS are expected to be more informative in LUAD than in LUSC.",
    ),
    (
        ("cd274",),
        """
SELECT g.symbol, lct.cell_type_name, lct.compartment, e.expected_expression, e.quantitative_status, e.biological_rationale
FROM luca_cell_type_gene_evidence e
JOIN genes g ON g.gene_id = e.gene_id
JOIN cell_types lct ON lct.cell_type_id = e.cell_type_id
WHERE g.symbol = 'CD274'
ORDER BY lct.compartment, lct.cell_type_name;
""".strip(),
        "CD274/PD-L1 can come from malignant or antigen-presenting immune compartments. The next LuCA matrix step should quantify this by cell type.",
    ),
    (
        ("checkpoint", "express"),
        """
SELECT ges.cancer_type, g.symbol, ges.n_samples, ROUND(ges.mean_zscore, 3) AS mean_zscore, ROUND(ges.fraction_high_zscore, 3) AS fraction_high_zscore
FROM gene_expression_summary ges
JOIN genes g ON g.gene_id = ges.gene_id
WHERE g.theme = 'immune_checkpoint'
ORDER BY ges.cancer_type, ges.fraction_high_zscore DESC;
""".strip(),
        "This is bulk tumor RNA from TCGA. It cannot identify the cell type producing the checkpoint transcript.",
    ),
    (
        ("cell", "type", "express"),
        """
SELECT g.symbol, lct.cell_type_name, lct.compartment, e.expected_expression, e.quantitative_status, e.biological_rationale
FROM luca_cell_type_gene_evidence e
JOIN genes g ON g.gene_id = e.gene_id
JOIN cell_types lct ON lct.cell_type_id = e.cell_type_id
ORDER BY g.symbol, lct.compartment, lct.cell_type_name
LIMIT 40;
""".strip(),
        "This is a curated LuCA cell-type evidence layer, not a quantitative matrix-derived expression table.",
    ),
    (
        ("luca", "cell"),
        """
SELECT cell_type_name, compartment, ontology_term_id
FROM cell_types
ORDER BY compartment, cell_type_name;
""".strip(),
        "These are public LuCA CELLxGENE cell-type labels mapped into broad compartments for agent queries.",
    ),
    (
        ("copy", "number"),
        """
SELECT cs.cancer_type, g.symbol, g.theme, cs.n_samples, ROUND(cs.altered_fraction, 3) AS altered_fraction, ROUND(cs.amplification_fraction, 3) AS amplification_fraction, ROUND(cs.deep_deletion_fraction, 3) AS deep_deletion_fraction
FROM cna_summary cs
JOIN genes g ON g.gene_id = cs.gene_id
ORDER BY cs.cancer_type, cs.altered_fraction DESC
LIMIT 20;
""".strip(),
        "Discrete GISTIC calls are useful for screening. Focality, purity, and expression concordance need follow-up.",
    ),
    (
        ("myeloid",),
        """
SELECT ges.cancer_type, g.symbol, ROUND(ges.median_zscore, 3) AS median_zscore, ROUND(ges.fraction_high_zscore, 3) AS fraction_high_zscore
FROM gene_expression_summary ges
JOIN genes g ON g.gene_id = ges.gene_id
WHERE g.theme = 'myeloid_inflammation'
ORDER BY ges.cancer_type, ges.fraction_high_zscore DESC;
""".strip(),
        "Bulk tumor RNA suggests inflammatory context. LuCA single-cell summaries are the next step for cell-type localization.",
    ),
    (
        ("source", "provenance"),
        """
SELECT dataset_id, source_name, source_url, assay_scope, access_note
FROM datasets
ORDER BY dataset_id;
""".strip(),
        "Every answer should remain traceable to source records and curated tables.",
    ),
]


def is_safe_select(sql: str) -> bool:
    stripped = sql.strip().rstrip(";")
    if not re.match(r"(?is)^select\b", stripped):
        return False
    blocked = r"(?is)\b(insert|update|delete|drop|alter|create|attach|detach|pragma|vacuum|replace)\b"
    return re.search(blocked, stripped) is None


def choose_sql(question: str) -> tuple[str, str]:
    q = question.lower()
    for keywords, sql, note in QUESTION_MAP:
        if all(keyword in q for keyword in keywords):
            return sql, note
    return (
        """
SELECT question_id, question, interpretation_note
FROM canned_questions
ORDER BY question_id;
""".strip(),
        "I could not map the question to a specific curated query. Review the available canned questions or pass --sql with a safe SELECT query.",
    )


def print_table(columns: list[str], rows: list[sqlite3.Row]) -> None:
    print("\t".join(columns))
    for row in rows:
        print("\t".join("" if row[col] is None else str(row[col]) for col in columns))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="*", help="Natural-language question to map to a curated SQL query.")
    parser.add_argument("--sql", help="Run a direct read-only SELECT query.")
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args()

    if args.sql:
        sql = args.sql.strip()
        note = "Direct safe SQL query."
    else:
        sql, note = choose_sql(" ".join(args.question))
    if not is_safe_select(sql):
        raise SystemExit("Only read-only SELECT queries are allowed.")
    if not re.search(r"(?is)\blimit\b", sql):
        sql = f"{sql.rstrip(';')} LIMIT {max(1, min(args.limit, 100))}"

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql).fetchmany(max(1, min(args.limit, 100)))
    columns = list(rows[0].keys()) if rows else []
    print("Question:")
    print(" ".join(args.question) if args.question else "Direct SQL")
    print("\nSQL:")
    print(sql)
    print("\nResult:")
    if columns:
        print_table(columns, rows)
    else:
        print("No rows returned.")
    print("\nInterpretation note:")
    print(note)
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
