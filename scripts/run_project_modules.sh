#!/usr/bin/env bash
set -euo pipefail

MODULE="${1:-help}"

usage() {
  cat <<'EOF'
Run OncoOmics Agent modules.

Usage:
  bash scripts/run_project_modules.sh <module>

Modules:
  curate      Pull public TCGA LUAD/LUSC summaries from cBioPortal.
  database    Build the local SQLite database from curated CSV tables.
  report      Generate the Markdown report and SVG figures.
  query       Run three example agent-style questions.
  validate    Run compile checks, SQL checks, and text hygiene checks.
  all         Run curate, database, report, query, and validate.

Examples:
  bash scripts/run_project_modules.sh curate
  bash scripts/run_project_modules.sh all
EOF
}

run_curate() {
  python3 scripts/curate_cbioportal_nsclc.py
}

run_database() {
  python3 scripts/build_sqlite_database.py
}

run_report() {
  python3 scripts/generate_nsclc_report.py
}

run_query() {
  python3 scripts/query_oncoomics_agent.py "Which driver genes are most frequently mutated in LUAD and LUSC?"
  python3 scripts/query_oncoomics_agent.py "Which immune checkpoint genes are expressed?"
  python3 scripts/query_oncoomics_agent.py "show source provenance"
}

run_validate() {
  python3 scripts/validate_project.py
}

case "${MODULE}" in
  curate)
    run_curate
    ;;
  database)
    run_database
    ;;
  report)
    run_report
    ;;
  query)
    run_query
    ;;
  validate)
    run_validate
    ;;
  all)
    run_curate
    run_database
    run_report
    run_query
    run_validate
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    echo "Unknown module: ${MODULE}" >&2
    usage >&2
    exit 2
    ;;
esac
