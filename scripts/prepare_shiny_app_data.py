#!/usr/bin/env python3
"""Prepare the compact data bundle used by the Shiny demo app."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_DATA = ROOT / "shiny_app" / "data"
TABLES = [
    ROOT / "results" / "tables" / "datasets.csv",
    ROOT / "results" / "tables" / "atlas_source_summaries.csv",
    ROOT / "data" / "curated" / "samples.csv",
    ROOT / "results" / "tables" / "mutation_summary.csv",
    ROOT / "results" / "tables" / "gene_expression_summary.csv",
    ROOT / "results" / "tables" / "cna_summary.csv",
    ROOT / "results" / "tables" / "luca_datasets.csv",
    ROOT / "results" / "tables" / "cell_types.csv",
    ROOT / "results" / "tables" / "luca_cell_type_gene_evidence.csv",
    ROOT / "configs" / "gene_panel.csv",
]


def main() -> int:
    APP_DATA.mkdir(parents=True, exist_ok=True)
    for table in TABLES:
        if not table.exists():
            raise FileNotFoundError(table)
        shutil.copy2(table, APP_DATA / table.name)
    print(f"Wrote Shiny data bundle to {APP_DATA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
