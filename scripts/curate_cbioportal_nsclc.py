#!/usr/bin/env python3
"""Curate compact public NSCLC molecular summaries from cBioPortal."""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
API = "https://www.cbioportal.org/api"
STUDIES = {
    "luad_tcga_pan_can_atlas_2018": {
        "cancer_type": "LUAD",
        "histology": "lung adenocarcinoma",
        "rna_profile": "luad_tcga_pan_can_atlas_2018_rna_seq_v2_mrna_median_all_sample_Zscores",
        "mutation_profile": "luad_tcga_pan_can_atlas_2018_mutations",
        "cna_profile": "luad_tcga_pan_can_atlas_2018_gistic",
        "rna_sample_list": "luad_tcga_pan_can_atlas_2018_rna_seq_v2_mrna",
        "mutation_sample_list": "luad_tcga_pan_can_atlas_2018_sequenced",
        "cna_sample_list": "luad_tcga_pan_can_atlas_2018_cna",
    },
    "lusc_tcga_pan_can_atlas_2018": {
        "cancer_type": "LUSC",
        "histology": "lung squamous cell carcinoma",
        "rna_profile": "lusc_tcga_pan_can_atlas_2018_rna_seq_v2_mrna_median_all_sample_Zscores",
        "mutation_profile": "lusc_tcga_pan_can_atlas_2018_mutations",
        "cna_profile": "lusc_tcga_pan_can_atlas_2018_gistic",
        "rna_sample_list": "lusc_tcga_pan_can_atlas_2018_rna_seq_v2_mrna",
        "mutation_sample_list": "lusc_tcga_pan_can_atlas_2018_sequenced",
        "cna_sample_list": "lusc_tcga_pan_can_atlas_2018_cna",
    },
}


def read_gene_panel(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def request_json(path: str, payload: dict | None = None) -> object:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(f"{API}{path}", data=data, headers=headers, method="POST" if payload is not None else "GET")
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not fields:
        fields = list(rows[0]) if rows else []
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def median(values: list[float]) -> float:
    return statistics.median(values) if values else 0.0


def fetch_study(study_id: str, cfg: dict[str, str], genes: list[dict[str, str]]) -> dict[str, list[dict[str, object]]]:
    study = request_json(f"/studies/{study_id}")
    profiles = request_json(f"/studies/{study_id}/molecular-profiles")
    samples = request_json(f"/studies/{study_id}/samples?projection=SUMMARY&pageSize=100000")
    entrez_ids = [int(gene["entrez_gene_id"]) for gene in genes]

    expression = request_json(
        f"/molecular-profiles/{cfg['rna_profile']}/molecular-data/fetch?projection=SUMMARY",
        {"entrezGeneIds": entrez_ids, "sampleListId": cfg["rna_sample_list"]},
    )
    mutations = request_json(
        f"/molecular-profiles/{cfg['mutation_profile']}/mutations/fetch?projection=SUMMARY",
        {"entrezGeneIds": entrez_ids, "sampleListId": cfg["mutation_sample_list"]},
    )
    cna = request_json(
        f"/molecular-profiles/{cfg['cna_profile']}/molecular-data/fetch?projection=SUMMARY",
        {"entrezGeneIds": entrez_ids, "sampleListId": cfg["cna_sample_list"]},
    )

    dataset_row = {
        "dataset_id": study_id,
        "source_name": study.get("name", study_id),
        "source_url": f"https://www.cbioportal.org/study/summary?id={study_id}",
        "organism": "Homo sapiens",
        "disease_focus": "non-small cell lung cancer",
        "assay_scope": "TCGA PanCancer molecular profiles: mutation, copy number, methylation, mRNA, RPPA availability",
        "access_note": "public cBioPortal study",
    }

    profile_rows = []
    for profile in profiles:
        profile_rows.append(
            {
                "molecular_profile_id": profile.get("molecularProfileId", ""),
                "dataset_id": study_id,
                "alteration_type": profile.get("molecularAlterationType", ""),
                "datatype": profile.get("datatype", ""),
                "name": profile.get("name", ""),
                "patient_level": int(bool(profile.get("patientLevel", False))),
            }
        )

    sample_rows = []
    for sample in samples:
        sample_rows.append(
            {
                "sample_id": sample.get("sampleId", ""),
                "patient_id": sample.get("patientId", ""),
                "dataset_id": study_id,
                "cancer_type": cfg["cancer_type"],
                "histology": cfg["histology"],
                "sample_type": sample.get("sampleType", ""),
            }
        )

    gene_by_id = {int(gene["entrez_gene_id"]): gene for gene in genes}
    expr_rows = []
    expr_by_gene = defaultdict(list)
    for row in expression:
        gene_id = int(row["entrezGeneId"])
        value = float(row["value"])
        expr_rows.append(
            {
                "dataset_id": study_id,
                "sample_id": row["sampleId"],
                "gene_id": gene_id,
                "expression_zscore": round(value, 6),
            }
        )
        expr_by_gene[gene_id].append(value)

    expression_summary = []
    for gene_id, values in sorted(expr_by_gene.items()):
        expression_summary.append(
            {
                "dataset_id": study_id,
                "cancer_type": cfg["cancer_type"],
                "histology": cfg["histology"],
                "gene_id": gene_id,
                "symbol": gene_by_id[gene_id]["symbol"],
                "theme": gene_by_id[gene_id]["theme"],
                "n_samples": len(values),
                "mean_zscore": round(sum(values) / len(values), 6),
                "median_zscore": round(median(values), 6),
                "fraction_high_zscore": round(sum(1 for value in values if value >= 1.0) / len(values), 6),
            }
        )

    mut_rows = []
    mutation_counts = defaultdict(set)
    protein_changes = defaultdict(Counter)
    for index, row in enumerate(mutations, start=1):
        gene_id = int(row["entrezGeneId"])
        sample_id = row.get("sampleId", "")
        protein = row.get("proteinChange", "") or ""
        mutation_id = sha256_text(f"{study_id}|{sample_id}|{gene_id}|{protein}|{row.get('startPosition', '')}|{index}")[:20]
        mut_rows.append(
            {
                "mutation_id": mutation_id,
                "dataset_id": study_id,
                "sample_id": sample_id,
                "patient_id": row.get("patientId", ""),
                "gene_id": gene_id,
                "symbol": gene_by_id[gene_id]["symbol"],
                "protein_change": protein,
                "mutation_type": row.get("mutationType", ""),
                "chromosome": row.get("chr", ""),
                "start_position": row.get("startPosition", ""),
                "variant_type": row.get("variantType", ""),
                "keyword": row.get("keyword", ""),
            }
        )
        mutation_counts[gene_id].add(sample_id)
        if protein:
            protein_changes[gene_id][protein] += 1

    sequenced_samples = len(samples)
    mutation_summary = []
    for gene in genes:
        gene_id = int(gene["entrez_gene_id"])
        recurrent = ";".join([f"{protein}:{count}" for protein, count in protein_changes[gene_id].most_common(5)])
        mutated = len(mutation_counts[gene_id])
        mutation_summary.append(
            {
                "dataset_id": study_id,
                "cancer_type": cfg["cancer_type"],
                "histology": cfg["histology"],
                "gene_id": gene_id,
                "symbol": gene["symbol"],
                "theme": gene["theme"],
                "mutated_samples": mutated,
                "sequenced_samples": sequenced_samples,
                "mutation_frequency": round(mutated / sequenced_samples, 6) if sequenced_samples else 0,
                "recurrent_protein_changes": recurrent,
            }
        )

    cna_rows = []
    cna_by_gene = defaultdict(list)
    for row in cna:
        gene_id = int(row["entrezGeneId"])
        value = int(float(row["value"]))
        cna_rows.append(
            {
                "dataset_id": study_id,
                "sample_id": row["sampleId"],
                "gene_id": gene_id,
                "symbol": gene_by_id[gene_id]["symbol"],
                "discrete_cna": value,
            }
        )
        cna_by_gene[gene_id].append(value)

    cna_summary = []
    for gene in genes:
        gene_id = int(gene["entrez_gene_id"])
        values = cna_by_gene[gene_id]
        n_values = len(values)
        cna_summary.append(
            {
                "dataset_id": study_id,
                "cancer_type": cfg["cancer_type"],
                "histology": cfg["histology"],
                "gene_id": gene_id,
                "symbol": gene["symbol"],
                "theme": gene["theme"],
                "n_samples": n_values,
                "deep_deletion_fraction": round(sum(1 for value in values if value == -2) / n_values, 6) if n_values else 0,
                "gain_fraction": round(sum(1 for value in values if value == 1) / n_values, 6) if n_values else 0,
                "amplification_fraction": round(sum(1 for value in values if value == 2) / n_values, 6) if n_values else 0,
                "altered_fraction": round(sum(1 for value in values if value != 0) / n_values, 6) if n_values else 0,
            }
        )

    return {
        "datasets": [dataset_row],
        "molecular_profiles": profile_rows,
        "samples": sample_rows,
        "expression_observations": expr_rows,
        "gene_expression_summary": expression_summary,
        "mutation_observations": mut_rows,
        "mutation_summary": mutation_summary,
        "cna_observations": cna_rows,
        "cna_summary": cna_summary,
    }


def main() -> int:
    outdir = ROOT / "data" / "curated"
    results_dir = ROOT / "results" / "tables"
    genes = read_gene_panel(ROOT / "configs" / "gene_panel.csv")

    all_rows = {
        "datasets": [],
        "molecular_profiles": [],
        "samples": [],
        "expression_observations": [],
        "gene_expression_summary": [],
        "mutation_observations": [],
        "mutation_summary": [],
        "cna_observations": [],
        "cna_summary": [],
    }
    for study_id, cfg in STUDIES.items():
        study_rows = fetch_study(study_id, cfg, genes)
        for key, rows in study_rows.items():
            all_rows[key].extend(rows)

    gene_rows = [
        {
            "gene_id": int(row["entrez_gene_id"]),
            "symbol": row["symbol"],
            "theme": row["theme"],
            "reason": row["reason"],
        }
        for row in genes
    ]

    atlas_sources = [
        {
            "dataset_id": "luca_cellxgene_collection",
            "atlas_name": "LuCA single-cell Lung Cancer Atlas",
            "disease_focus": "non-small cell lung cancer tumor microenvironment",
            "assay_scope": "single-cell RNA-seq atlas",
            "reported_cells": "more than 1.2 million",
            "reported_patients": "309",
            "public_access": "CZ CELLxGENE collection and LuCA project resources",
            "v1_use": "source-level atlas record; full cell matrix reserved for scalable processing",
            "source_url": "https://cellxgene.cziscience.com/collections/edb893ee-4066-4128-9aec-5eb2b03f8287",
        },
        {
            "dataset_id": "hlca_reference_atlas",
            "atlas_name": "Human Lung Cell Atlas v1.0",
            "disease_focus": "healthy and diseased human lung reference",
            "assay_scope": "integrated single-cell lung reference atlas",
            "reported_cells": "large-scale integrated lung single-cell reference",
            "reported_patients": "multiple public cohorts",
            "public_access": "Human Cell Atlas and HLCA project resources",
            "v1_use": "reference context for lung cell identity and future normal-lung comparison",
            "source_url": "https://data.humancellatlas.org/hca-bio-networks/lung/atlases/lung-v1-0",
        },
    ]
    atlas_dataset_rows = [
        {
            "dataset_id": atlas["dataset_id"],
            "source_name": atlas["atlas_name"],
            "source_url": atlas["source_url"],
            "organism": "Homo sapiens",
            "disease_focus": atlas["disease_focus"],
            "assay_scope": atlas["assay_scope"],
            "access_note": atlas["public_access"],
        }
        for atlas in atlas_sources
    ]

    source_rows = []
    today = date.today().isoformat()
    for dataset in all_rows["datasets"]:
        source_rows.append(
            {
                "source_file_id": f"{dataset['dataset_id']}_cbioportal_api",
                "dataset_id": dataset["dataset_id"],
                "file_role": "public_api_response",
                "source_url": dataset["source_url"],
                "retrieval_method": "cBioPortal REST API",
                "retrieval_date": today,
                "local_path": "data/curated",
                "checksum_sha256": "",
            }
        )
    for atlas in atlas_sources:
        source_rows.append(
            {
                "source_file_id": f"{atlas['dataset_id']}_source_record",
                "dataset_id": atlas["dataset_id"],
                "file_role": "source_metadata",
                "source_url": atlas["source_url"],
                "retrieval_method": "public source review",
                "retrieval_date": today,
                "local_path": "",
                "checksum_sha256": "",
            }
        )

    outputs = {
        "datasets.csv": all_rows["datasets"] + atlas_dataset_rows,
        "genes.csv": gene_rows,
        "source_files.csv": source_rows,
        "molecular_profiles.csv": all_rows["molecular_profiles"],
        "samples.csv": all_rows["samples"],
        "expression_observations.csv": all_rows["expression_observations"],
        "gene_expression_summary.csv": all_rows["gene_expression_summary"],
        "mutation_observations.csv": all_rows["mutation_observations"],
        "mutation_summary.csv": all_rows["mutation_summary"],
        "cna_observations.csv": all_rows["cna_observations"],
        "cna_summary.csv": all_rows["cna_summary"],
        "atlas_source_summaries.csv": atlas_sources,
    }
    for name, rows in outputs.items():
        write_csv(outdir / name, rows)
        if name in {"gene_expression_summary.csv", "mutation_summary.csv", "cna_summary.csv", "atlas_source_summaries.csv", "datasets.csv"}:
            write_csv(results_dir / name, rows)

    print(f"Wrote curated NSCLC tables to {outdir}")
    print(f"Wrote summary result tables to {results_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
