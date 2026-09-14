#!/usr/bin/env python3
"""Curate LuCA CELLxGENE metadata and a transparent cell-type evidence layer."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
COLLECTION_ID = "edb893ee-4066-4128-9aec-5eb2b03f8287"
COLLECTION_URL = f"https://cellxgene.cziscience.com/collections/{COLLECTION_ID}"
API_URL = f"https://api.cellxgene.cziscience.com/curation/v1/collections/{COLLECTION_ID}"

COMPARTMENT_RULES = [
    ("malignant", "malignant tumor"),
    ("macrophage", "myeloid immune"),
    ("monocyte", "myeloid immune"),
    ("dendritic", "myeloid immune"),
    ("myeloid", "myeloid immune"),
    ("neutrophil", "myeloid immune"),
    ("mast", "myeloid immune"),
    ("regulatory t", "lymphoid immune"),
    ("t cell", "lymphoid immune"),
    ("natural killer", "lymphoid immune"),
    ("b cell", "lymphoid immune"),
    ("plasma", "lymphoid immune"),
    ("epithelial", "epithelial"),
    ("alveolar", "epithelial"),
    ("club cell", "epithelial"),
    ("multiciliated", "epithelial"),
    ("fibroblast", "stromal"),
    ("stromal", "stromal"),
    ("smooth muscle", "stromal"),
    ("pericyte", "stromal"),
    ("endothelial", "vascular"),
    ("lymphatic", "vascular"),
    ("vein", "vascular"),
    ("artery", "vascular"),
    ("mesothelial", "mesothelial"),
]

GENE_EVIDENCE = {
    "CD274": [
        ("malignant cell", "context-dependent", "PD-L1 can be expressed by tumor cells under interferon-rich immune pressure."),
        ("macrophage", "moderate", "Myeloid cells are common PD-L1-positive compartments in tumor microenvironments."),
        ("dendritic cell", "moderate", "Antigen-presenting cells can express PD-L1 during immune regulation."),
    ],
    "PDCD1": [
        ("CD8-positive, alpha-beta T cell", "high", "PD-1 is a canonical exhausted or chronically stimulated T-cell receptor."),
        ("CD4-positive, alpha-beta T cell", "moderate", "Activated and dysfunctional CD4 T cells can express PD-1."),
        ("regulatory T cell", "moderate", "Regulatory T cells can carry inhibitory checkpoint programs."),
    ],
    "CTLA4": [
        ("regulatory T cell", "high", "CTLA4 is strongly associated with regulatory T-cell biology."),
        ("CD4-positive, alpha-beta T cell", "moderate", "Activated CD4 T cells may express CTLA4."),
    ],
    "LAG3": [
        ("CD8-positive, alpha-beta T cell", "moderate", "LAG3 is an inhibitory receptor linked to T-cell dysfunction."),
        ("CD4-positive, alpha-beta T cell", "moderate", "LAG3 can mark exhausted or regulatory-like T-cell states."),
    ],
    "TIGIT": [
        ("CD8-positive, alpha-beta T cell", "moderate", "TIGIT is a checkpoint receptor in dysfunctional T and NK states."),
        ("natural killer cell", "moderate", "TIGIT is also observed in NK-cell inhibitory programs."),
        ("regulatory T cell", "moderate", "TIGIT-positive regulatory T cells can contribute to immune suppression."),
    ],
    "HAVCR2": [
        ("CD8-positive, alpha-beta T cell", "moderate", "TIM-3 is associated with dysfunctional T-cell states."),
        ("macrophage", "moderate", "HAVCR2 can also appear in myeloid regulatory contexts."),
    ],
    "EGFR": [
        ("malignant cell", "high", "EGFR is a canonical NSCLC tumor driver, especially in LUAD subsets."),
        ("epithelial cell of lung", "moderate", "EGFR biology is epithelial-lineage linked."),
    ],
    "KRAS": [
        ("malignant cell", "context-dependent", "KRAS is a frequent LUAD driver; RNA expression does not equal mutation status."),
    ],
    "MET": [
        ("malignant cell", "context-dependent", "MET activation may occur through amplification, exon skipping, or expression programs."),
        ("epithelial cell of lung", "moderate", "MET has epithelial and invasive-growth biology."),
    ],
    "ALK": [
        ("malignant cell", "context-dependent", "ALK rearranged tumors are a molecular subset; RNA alone is not sufficient for fusion calling."),
    ],
    "MYC": [
        ("malignant cell", "moderate", "MYC supports proliferative tumor programs."),
    ],
    "EPCAM": [
        ("malignant cell", "high", "EPCAM marks epithelial tumor cells in many carcinoma datasets."),
        ("epithelial cell of lung", "high", "EPCAM is a broad epithelial marker."),
    ],
    "VIM": [
        ("fibroblast of lung", "high", "VIM is a mesenchymal and stromal marker."),
        ("stromal cell", "high", "Stromal compartments often carry VIM expression."),
        ("malignant cell", "context-dependent", "VIM in malignant cells can support EMT-like interpretation."),
    ],
    "ZEB1": [
        ("malignant cell", "context-dependent", "ZEB1 is an EMT transcription factor."),
        ("fibroblast of lung", "moderate", "Mesenchymal compartments can express EMT-associated transcriptional programs."),
    ],
    "SNAI1": [
        ("malignant cell", "context-dependent", "SNAI1 is an EMT transcription factor."),
    ],
    "MMP9": [
        ("neutrophil", "high", "MMP9 is often prominent in neutrophil and inflammatory myeloid programs."),
        ("macrophage", "moderate", "Macrophage-derived matrix remodeling can include MMP9."),
    ],
    "S100A8": [
        ("neutrophil", "high", "S100A8 is a canonical inflammatory neutrophil and myeloid marker."),
        ("classical monocyte", "high", "Classical monocytes can express S100A8 inflammatory programs."),
    ],
    "S100A9": [
        ("neutrophil", "high", "S100A9 pairs with S100A8 in inflammatory myeloid biology."),
        ("classical monocyte", "high", "Classical monocytes can express S100A9 inflammatory programs."),
    ],
    "CXCL8": [
        ("neutrophil", "moderate", "CXCL8 marks inflammatory chemokine biology."),
        ("macrophage", "moderate", "Macrophages can contribute CXCL8 in inflammatory tumors."),
        ("malignant cell", "context-dependent", "Tumor-cell CXCL8 can support inflammatory and pro-angiogenic programs."),
    ],
    "IL1B": [
        ("classical monocyte", "high", "IL1B is a canonical inflammatory monocyte/macrophage cytokine."),
        ("macrophage", "high", "Macrophage IL1B supports inflammatory tumor microenvironment interpretation."),
    ],
    "SPP1": [
        ("macrophage", "high", "SPP1-positive macrophage states are common tissue-remodeling tumor-associated myeloid programs."),
        ("malignant cell", "context-dependent", "SPP1 can also be tumor-cell associated in some epithelial cancers."),
    ],
    "MKI67": [
        ("malignant cell", "high", "MKI67 marks cycling tumor cells when present in malignant compartments."),
        ("CD8-positive, alpha-beta T cell", "context-dependent", "Cycling lymphocytes can also express proliferation markers."),
    ],
    "TOP2A": [
        ("malignant cell", "high", "TOP2A marks proliferating tumor cells and cell-cycle activity."),
        ("CD8-positive, alpha-beta T cell", "context-dependent", "Expanding lymphocyte populations may express cell-cycle genes."),
    ],
    "VEGFA": [
        ("malignant cell", "context-dependent", "Tumor VEGFA can indicate hypoxia and angiogenic signaling."),
        ("macrophage", "moderate", "Myeloid cells can contribute angiogenic factors in tumors."),
    ],
    "HIF1A": [
        ("malignant cell", "context-dependent", "HIF1A supports hypoxia-associated interpretation."),
        ("macrophage", "context-dependent", "Hypoxic tumor niches can shape myeloid HIF programs."),
    ],
    "HLA-A": [
        ("malignant cell", "moderate", "MHC-I expression on malignant cells affects antigen presentation."),
        ("B cell", "high", "Immune cells broadly express antigen-presentation machinery."),
        ("macrophage", "high", "Myeloid cells are professional antigen-presenting compartments."),
    ],
    "HLA-B": [
        ("malignant cell", "moderate", "MHC-I expression on malignant cells affects immune recognition."),
        ("B cell", "high", "Immune cells broadly express antigen-presentation machinery."),
        ("macrophage", "high", "Myeloid cells are professional antigen-presenting compartments."),
    ],
    "B2M": [
        ("malignant cell", "moderate", "B2M supports MHC-I stability and tumor immune recognition."),
        ("B cell", "high", "B2M is broadly expressed with MHC-I in nucleated immune cells."),
        ("macrophage", "high", "Myeloid antigen-presentation context commonly includes B2M."),
    ],
    "JAK1": [
        ("malignant cell", "context-dependent", "JAK1 supports interferon response and immune-selection interpretation."),
        ("T cell", "moderate", "JAK signaling is relevant to cytokine response in immune cells."),
    ],
    "JAK2": [
        ("malignant cell", "context-dependent", "JAK2 supports interferon response and immune-selection interpretation."),
        ("macrophage", "moderate", "JAK signaling is relevant to inflammatory myeloid response."),
    ],
}


def request_json(url: str) -> dict:
    request = Request(url, headers={"Accept": "application/json"})
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def read_gene_panel() -> dict[str, dict[str, str]]:
    with (ROOT / "configs" / "gene_panel.csv").open(newline="") as handle:
        return {row["symbol"]: row for row in csv.DictReader(handle)}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        if not rows:
            return
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def compartment_for(label: str) -> str:
    lower = label.lower()
    exact = {
        "b cell": "lymphoid immune",
        "club cell": "epithelial",
        "mast cell": "myeloid immune",
        "plasma cell": "lymphoid immune",
        "plasmacytoid dendritic cell": "myeloid immune",
    }
    if lower in exact:
        return exact[lower]
    for token, compartment in COMPARTMENT_RULES:
        if token in lower:
            return compartment
    return "other"


def labels(values: list[dict[str, str]]) -> str:
    return ";".join(item["label"] for item in values)


def main() -> int:
    collection = request_json(API_URL)
    gene_panel = read_gene_panel()
    curated = ROOT / "data" / "curated"
    results = ROOT / "results" / "tables"

    dataset_rows = []
    cell_type_by_name = {}
    for dataset in collection["datasets"]:
        assets = dataset.get("assets", [])
        h5ad = next((asset for asset in assets if asset.get("filetype") == "H5AD"), {})
        dataset_rows.append(
            {
                "luca_dataset_id": dataset["dataset_id"],
                "title": dataset.get("title", ""),
                "collection_id": COLLECTION_ID,
                "collection_url": COLLECTION_URL,
                "cell_count": dataset.get("cell_count", 0),
                "disease_labels": labels(dataset.get("disease", [])),
                "tissue_labels": labels(dataset.get("tissue", [])),
                "assay_labels": labels(dataset.get("assay", [])),
                "h5ad_url": h5ad.get("url", ""),
                "h5ad_filesize_gb": round((h5ad.get("filesize", 0) or 0) / 1_000_000_000, 3),
                "citation": dataset.get("citation", ""),
            }
        )
        for cell_type in dataset.get("cell_type", []):
            name = cell_type["label"]
            cell_type_by_name[name] = {
                "cell_type_id": slug(name),
                "cell_type_name": name,
                "ontology_term_id": cell_type.get("ontology_term_id", ""),
                "compartment": compartment_for(name),
                "primer_link": "docs/biology-primer.md#the-biological-setting",
            }

    evidence_rows = []
    known_cell_types = set(cell_type_by_name)
    for symbol, entries in GENE_EVIDENCE.items():
        if symbol not in gene_panel:
            continue
        gene_id = gene_panel[symbol]["entrez_gene_id"]
        for cell_type_name, expected, rationale in entries:
            if cell_type_name not in known_cell_types:
                continue
            evidence_rows.append(
                {
                    "evidence_id": f"{symbol}_{cell_type_by_name[cell_type_name]['cell_type_id']}",
                    "gene_id": gene_id,
                    "symbol": symbol,
                    "cell_type_id": cell_type_by_name[cell_type_name]["cell_type_id"],
                    "cell_type_name": cell_type_name,
                    "compartment": cell_type_by_name[cell_type_name]["compartment"],
                    "expected_expression": expected,
                    "evidence_basis": "curated_literature_and_marker_context",
                    "biological_rationale": rationale,
                    "quantitative_status": "not_matrix_quantified_in_v1",
                }
            )

    cell_type_rows = sorted(cell_type_by_name.values(), key=lambda row: row["cell_type_name"])
    write_csv(curated / "luca_datasets.csv", dataset_rows)
    write_csv(curated / "cell_types.csv", cell_type_rows)
    write_csv(curated / "luca_cell_type_gene_evidence.csv", evidence_rows)
    write_csv(results / "luca_datasets.csv", dataset_rows)
    write_csv(results / "cell_types.csv", cell_type_rows)
    write_csv(results / "luca_cell_type_gene_evidence.csv", evidence_rows)
    print(f"Wrote LuCA metadata and cell-type evidence tables to {curated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
