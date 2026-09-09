PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS datasets (
  dataset_id TEXT PRIMARY KEY,
  source_name TEXT NOT NULL,
  source_url TEXT NOT NULL,
  organism TEXT NOT NULL,
  disease_focus TEXT NOT NULL,
  assay_scope TEXT NOT NULL,
  access_note TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_files (
  source_file_id TEXT PRIMARY KEY,
  dataset_id TEXT NOT NULL,
  file_role TEXT NOT NULL,
  source_url TEXT NOT NULL,
  retrieval_method TEXT NOT NULL,
  retrieval_date TEXT NOT NULL,
  local_path TEXT,
  checksum_sha256 TEXT,
  FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
);

CREATE TABLE IF NOT EXISTS genes (
  gene_id INTEGER PRIMARY KEY,
  symbol TEXT NOT NULL UNIQUE,
  theme TEXT NOT NULL,
  reason TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS samples (
  sample_id TEXT PRIMARY KEY,
  patient_id TEXT NOT NULL,
  dataset_id TEXT NOT NULL,
  cancer_type TEXT NOT NULL,
  histology TEXT NOT NULL,
  sample_type TEXT,
  FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
);

CREATE TABLE IF NOT EXISTS molecular_profiles (
  molecular_profile_id TEXT PRIMARY KEY,
  dataset_id TEXT NOT NULL,
  alteration_type TEXT NOT NULL,
  datatype TEXT NOT NULL,
  name TEXT NOT NULL,
  patient_level INTEGER NOT NULL,
  FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
);

CREATE TABLE IF NOT EXISTS expression_observations (
  dataset_id TEXT NOT NULL,
  sample_id TEXT NOT NULL,
  gene_id INTEGER NOT NULL,
  expression_zscore REAL NOT NULL,
  PRIMARY KEY (dataset_id, sample_id, gene_id),
  FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id),
  FOREIGN KEY (sample_id) REFERENCES samples(sample_id),
  FOREIGN KEY (gene_id) REFERENCES genes(gene_id)
);

CREATE TABLE IF NOT EXISTS gene_expression_summary (
  dataset_id TEXT NOT NULL,
  cancer_type TEXT NOT NULL,
  histology TEXT NOT NULL,
  gene_id INTEGER NOT NULL,
  n_samples INTEGER NOT NULL,
  mean_zscore REAL NOT NULL,
  median_zscore REAL NOT NULL,
  fraction_high_zscore REAL NOT NULL,
  PRIMARY KEY (dataset_id, gene_id),
  FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id),
  FOREIGN KEY (gene_id) REFERENCES genes(gene_id)
);

CREATE TABLE IF NOT EXISTS mutation_observations (
  mutation_id TEXT PRIMARY KEY,
  dataset_id TEXT NOT NULL,
  sample_id TEXT NOT NULL,
  patient_id TEXT NOT NULL,
  gene_id INTEGER NOT NULL,
  protein_change TEXT,
  mutation_type TEXT,
  chromosome TEXT,
  start_position INTEGER,
  variant_type TEXT,
  keyword TEXT,
  FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id),
  FOREIGN KEY (sample_id) REFERENCES samples(sample_id),
  FOREIGN KEY (gene_id) REFERENCES genes(gene_id)
);

CREATE TABLE IF NOT EXISTS mutation_summary (
  dataset_id TEXT NOT NULL,
  cancer_type TEXT NOT NULL,
  histology TEXT NOT NULL,
  gene_id INTEGER NOT NULL,
  mutated_samples INTEGER NOT NULL,
  sequenced_samples INTEGER NOT NULL,
  mutation_frequency REAL NOT NULL,
  recurrent_protein_changes TEXT,
  PRIMARY KEY (dataset_id, gene_id),
  FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id),
  FOREIGN KEY (gene_id) REFERENCES genes(gene_id)
);

CREATE TABLE IF NOT EXISTS cna_observations (
  dataset_id TEXT NOT NULL,
  sample_id TEXT NOT NULL,
  gene_id INTEGER NOT NULL,
  discrete_cna INTEGER NOT NULL,
  PRIMARY KEY (dataset_id, sample_id, gene_id),
  FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id),
  FOREIGN KEY (sample_id) REFERENCES samples(sample_id),
  FOREIGN KEY (gene_id) REFERENCES genes(gene_id)
);

CREATE TABLE IF NOT EXISTS cna_summary (
  dataset_id TEXT NOT NULL,
  cancer_type TEXT NOT NULL,
  histology TEXT NOT NULL,
  gene_id INTEGER NOT NULL,
  n_samples INTEGER NOT NULL,
  deep_deletion_fraction REAL NOT NULL,
  gain_fraction REAL NOT NULL,
  amplification_fraction REAL NOT NULL,
  altered_fraction REAL NOT NULL,
  PRIMARY KEY (dataset_id, gene_id),
  FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id),
  FOREIGN KEY (gene_id) REFERENCES genes(gene_id)
);

CREATE TABLE IF NOT EXISTS atlas_source_summaries (
  dataset_id TEXT PRIMARY KEY,
  atlas_name TEXT NOT NULL,
  disease_focus TEXT NOT NULL,
  assay_scope TEXT NOT NULL,
  reported_cells TEXT NOT NULL,
  reported_patients TEXT NOT NULL,
  public_access TEXT NOT NULL,
  v1_use TEXT NOT NULL,
  source_url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS canned_questions (
  question_id TEXT PRIMARY KEY,
  question TEXT NOT NULL,
  sql_text TEXT NOT NULL,
  interpretation_note TEXT NOT NULL
);
