#!/usr/bin/env python3
"""Validate the local OncoOmics Agent build."""

from __future__ import annotations

import csv
import sqlite3
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "configs/gene_panel.csv",
    "sql/schema.sql",
    "scripts/curate_cbioportal_nsclc.py",
    "scripts/build_sqlite_database.py",
    "scripts/query_oncoomics_agent.py",
    "scripts/generate_nsclc_report.py",
    "scripts/run_project_modules.sh",
    "data/curated/datasets.csv",
    "data/curated/genes.csv",
    "data/curated/samples.csv",
    "data/curated/expression_observations.csv",
    "data/curated/mutation_observations.csv",
    "data/curated/cna_observations.csv",
    "results/tables/gene_expression_summary.csv",
    "results/tables/mutation_summary.csv",
    "results/tables/cna_summary.csv",
    "results/nsclc_atlas_report.md",
]

BLOCKED_TERMS = [
    "pro" + "mpt " + "leak",
    "guard" + "rails",
    "chat" + "gpt",
    "co" + "dex",
]


def count_csv(path: Path) -> int:
    with path.open(newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def main() -> int:
    errors = []
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            errors.append(f"Missing required file: {rel}")

    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if rel != "scripts/validate_project.py" and path.suffix in {".py", ".md", ".sql", ".csv"} and path.exists():
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            for term in BLOCKED_TERMS:
                if term in text:
                    errors.append(f"Public-facing term found in {rel}: {term}")

    py_files = [
        "scripts/curate_cbioportal_nsclc.py",
        "scripts/build_sqlite_database.py",
        "scripts/query_oncoomics_agent.py",
        "scripts/generate_nsclc_report.py",
        "scripts/validate_project.py",
    ]
    result = subprocess.run([sys.executable, "-m", "py_compile", *py_files], cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        errors.append(result.stderr.strip())

    db_path = ROOT / "oncoomics_nsclc.sqlite"
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        checks = {
            "datasets": 4,
            "samples": 1000,
            "genes": 25,
            "expression_observations": 25000,
            "mutation_summary": 50,
            "cna_summary": 50,
        }
        for table, minimum in checks.items():
            observed = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            if observed < minimum:
                errors.append(f"{table} has {observed} rows; expected at least {minimum}")
        conn.close()
    else:
        errors.append("Missing local SQLite database.")

    for rel in [
        "results/tables/gene_expression_summary.csv",
        "results/tables/mutation_summary.csv",
        "results/tables/cna_summary.csv",
    ]:
        path = ROOT / rel
        if path.exists() and count_csv(path) == 0:
            errors.append(f"{rel} has no data rows")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Project validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
