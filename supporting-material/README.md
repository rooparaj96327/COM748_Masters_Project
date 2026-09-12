# Submission Package Overview

**Project:** Auditing AI-Generated Draft Judgments: Citation Provenance, Holding Accuracy, and Reasoning Grounding  
**Student:** Roopa Raj (B00871016)  
**Supervisor:** Professor Jun Liu  
**Module:** COM748 Masters Research Project, Ulster University  
**Date:** 14 September 2026

---

## Project summary

This project audits AI-generated draft judgments produced by Hercules, a legal
AI system that generates draft court decisions from uploaded skeleton arguments
and retrieved case law. The study extracts citations from 59 generated
judgments, verifies them against retrieval records and an external corpus
registry, conducts manual annotation of holding accuracy and reasoning
grounding, and validates an automated screening verifier against
human-adjudicated labels. An exploratory comparison between real and
synthetic input documents is also included.

---

## Submission package contents

### `data/`

| Folder | Description |
|---|---|
| `data/raw/database-exports/` | Frozen JSON and XLSX exports from the Hercules production database: 59 draft decisions and 66 semantic-search records. |
| `data/raw/system-exports/qdrant/` | Frozen Qdrant vector-database corpus registry (CSV and JSON) listing all cases available for retrieval at the time of the study. |
| `data/raw/input-documents/real-pdf/` | PDF skeleton arguments from real UK court cases used as Hercules inputs (22 files). |
| `data/raw/input-documents/synthetic-pdf/` | PDF skeleton arguments generated synthetically and used as Hercules inputs (34 files). |
| `data/processed/hercules-inputs/` | XML-formatted skeleton arguments as uploaded to Hercules, organised into `real-xml/` and `synthetic-xml/` subfolders. |
| `data/processed/` | All processed CSV, JSON, and XLSX files produced by the analysis pipeline. See `data-dictionary.md` for column-level documentation of every file. |

### `annotations/`

| File | Description |
|---|---|
| `annotations/holding_grounding_annotation.xlsx` | Manual holding-accuracy and reasoning-grounding annotation workbook. Contains `Annotations` and `Retrieved Evidence` sheets with R1, R2, and adjudicated labels for the validation sample (50 judgments, 98 citation occurrences). |
| `annotations/holding_grounding_codebook.md` | Annotation codebook defining label definitions, decision rules, evidence sources, and quality-control procedures for the manual review. |

### `src/`

| File | Description |
|---|---|
| `src/extract_judgment_citations.py` | Extracts citation occurrences from the 59 draft judgments. |
| `src/build_retrieval_analysis.py` | Links each draft judgment to its closest semantic-search retrieval record. |
| `src/verify_citation_retrieval.py` | Verifies each citation against the linked retrieval and corpus registry. |
| `src/build_unique_citation_review.py` | Groups citations into unique authority groups for manual correctness review. |
| `src/build_citation_summary.py` | Produces summary metrics after manual citation correctness review is complete. |
| `src/prefill_holding_grounding.py` | Pre-fills draft annotation labels using GPT-4o-mini (requires OpenAI API key). |
| `src/hercules_verifier/` | Automated screening verifier: reads the annotation workbook and produces predictions for citation status, holding accuracy, and reasoning grounding, then validates against adjudicated labels. |

### `analysis/`

| File | Description |
|---|---|
| `analysis/build_results_figures.py` | Generates citation-correctness, input-type comparison, and retrieval-outcome figures. |
| `analysis/build_normalized_citation_figure.py` | Generates the normalised mean-citations-per-judgment figure with 95% confidence intervals. |
| `analysis/compare_input_groups.py` | Computes permutation tests, bootstrap confidence intervals, and Hedge's g effect sizes for real-vs-synthetic comparisons. |
| `analysis/build_holding_grounding_figures.py` | Generates holding-accuracy, reasoning-grounding, grounding-gap, and verifier confusion-matrix figures. |

### `outputs/`

| Folder / File | Description |
|---|---|
| `outputs/verifier_predictions_v1.csv` | Verifier predictions for all 115 citation occurrences, with human-adjudicated labels appended for validation. |
| `outputs/verifier_metrics_v1.json` | Verifier validation metrics: accuracy, balanced accuracy, Cohen's kappa, per-class precision/recall/F1, and confusion matrices. |
| `outputs/experiments/citation-analysis/` | Report-ready figures (PNG and PDF) and summary tables for the citation-analysis results. |
| `outputs/experiments/annotation-analysis/` | Report-ready figures (PNG and PDF) and summary tables for the annotation-analysis results. |
| `outputs/baseline/` | Intermediate audit workbooks used during the BAILII verification process. |

### `supporting-material/`

| File | Description |
|---|---|
| `supporting-material/README.md` | This file. |
| `supporting-material/data-dictionary.md` | Column-level documentation for every CSV, JSON, and XLSX output file. |
| `supporting-material/reproduction-guide.md` | Step-by-step instructions to reproduce the full analysis pipeline. |
| `supporting-material/figures-index.md` | Index of all report figures with descriptions and chart types. |

### Root files

| File | Description |
|---|---|
| `README.md` | Project overview with frozen dataset summary and methodological notes. |
| `baseline_manifest.txt` | Freeze summary recording the dataset scope, methodological boundaries, and reproducibility notes. |
| `project_inventory.csv` | File-level inventory with SHA-256 hashes for all frozen project files. |

---

## How to reproduce the analysis

**Requirements:** Python 3.14, pip

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install openpyxl matplotlib numpy scipy requests

# 3. Run the pipeline scripts in order (see reproduction-guide.md for details)
python src/extract_judgment_citations.py
python src/build_retrieval_analysis.py
python src/verify_citation_retrieval.py
python src/build_unique_citation_review.py
# ... manual BAILII verification step ...
python src/build_citation_summary.py
# ... manual annotation step (requires OpenAI API key for pre-fill) ...
python src/hercules_verifier/hercules_verifier.py --workbook annotations/holding_grounding_annotation.xlsx --output outputs/verifier_predictions_v1.csv --metrics outputs/verifier_metrics_v1.json
python analysis/build_results_figures.py
python analysis/build_normalized_citation_figure.py
python analysis/compare_input_groups.py
python analysis/build_holding_grounding_figures.py
```

See `supporting-material/reproduction-guide.md` for full step-by-step instructions, including manual intervention points.

---

## Frozen dataset summary

| Metric | Value |
|---|---|
| Draft judgments analysed | 59 |
| Citation occurrences analysed | 115 |
| Validation sample | 50 judgments, 98 citation occurrences |
| Real-input draft judgments | 34 |
| Synthetic-input draft judgments | 25 |
| Unique authority groups reviewed | 35 |