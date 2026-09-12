# Reproduction Guide

Step-by-step instructions to reproduce all results in the Hercules audit
analysis. Scripts must be run from the project root directory.

---

## Prerequisites

- **Python 3.14** (or a compatible version; 3.10 or later should work)
- **pip** (included with Python)

### Create a virtual environment

```bash
python -m venv .venv

# Activate (Windows):
.venv\Scripts\activate

# Activate (macOS / Linux):
source .venv/bin/activate
```

### Install dependencies

```bash
pip install openpyxl matplotlib numpy scipy requests
```

The only formal requirements file is `src/hercules_verifier/requirements.txt`
(`openpyxl>=3.1,<4`). The full set of third-party packages used across all
scripts is:

| Package | Used by |
|---|---|
| `openpyxl` | `build_citation_summary.py`, `prefill_holding_grounding.py`, `hercules_verifier.py`, `compare_input_groups.py` |
| `matplotlib` | `build_results_figures.py`, `build_normalized_citation_figure.py`, `build_holding_grounding_figures.py` |
| `numpy` | `build_holding_grounding_figures.py` |
| `scipy` | `compare_input_groups.py` (optional, for statistical tests) |
| `requests` | `prefill_holding_grounding.py` (for fetching judgment text from BAILII) |

Scripts 1-4 use only the Python standard library.

---

## Pipeline execution order

### Phase 1: Citation extraction and retrieval analysis

These steps are fully automated and require no manual intervention.

**Step 1. Extract citations from draft judgments**

```bash
python src/extract_judgment_citations.py
```

- **Input:** `data/raw/database-exports/draft_decisions_59_2026-08-14.json`
- **Output:** `data/processed/judgment_citations_59.csv` (115 rows),
  `data/processed/judgment_citations_59.json`
- **What it does:** Parses the `legalFramework.precedentCitations` field from
  each of the 59 draft judgments. Classifies each citation as `case_law`,
  `legislation_or_rule`, or `other_reference`. Tags each judgment as `real` or
  `synthetic` based on the `case_doc_id` prefix.

**Step 2. Build retrieval linkage**

```bash
python src/build_retrieval_analysis.py
```

- **Input:** `data/raw/database-exports/draft_decisions_59_2026-08-14.json`,
  `data/raw/database-exports/semantic_searches_66_2026-08-14.json`
- **Output:** `data/processed/retrieval_linkage_59.csv` (59 rows),
  `data/processed/retrieval_linkage_59.json`
- **What it does:** For each draft, finds the best-matching semantic search by
  timestamp (the latest search executed before the draft was generated).
  Extracts retrieved case IDs, titles, and cosine similarity scores.

**Step 3. Verify citation retrieval**

```bash
python src/verify_citation_retrieval.py
```

- **Input:** `data/processed/judgment_citations_59.csv` (from step 1),
  `data/processed/retrieval_linkage_59.csv` (from step 2),
  `data/raw/system-exports/qdrant/qdrant_corpus_registry_2026-08-14.csv`
- **Output:** `data/processed/citation_retrieval_verification_115.csv` (115
  rows), `data/processed/citation_retrieval_verification_115.json`
- **What it does:** For each citation, checks whether the cited authority was
  (a) retrieved for the linked search event, (b) present in the Qdrant corpus
  registry, or (c) neither. Uses fuzzy matching on case names, neutral
  citations, and normalised identifiers.

**Step 4. Build unique citation review sheet**

```bash
python src/build_unique_citation_review.py
```

- **Input:** `data/processed/citation_retrieval_verification_115.csv` (from
  step 3)
- **Output:** `data/processed/unique_citation_review.csv` (35 rows),
  `data/processed/unique_citation_review.json`
- **What it does:** Deduplicates the 115 citation occurrences into 35 unique
  authority groups and prepares a review sheet with empty columns for manual
  external verification.

---

### Phase 2: Manual citation correctness review

> **Manual intervention required.**

After step 4, the reviewer must:

1. Open `data/processed/unique_citation_review.csv` in Excel and save as
   `data/processed/unique_citation_review.xlsx`.
2. For each of the 35 authority groups, search BAILII
   (https://www.bailii.org/) or another authoritative source.
3. Populate these columns:
   - `case_exists_external` -- whether the case exists (`yes` / `no` /
     `ambiguous`)
   - `citation_correct_external` -- whether the citation is correct (`yes` /
     `incomplete` / `no`)
   - `authoritative_source_url` -- URL of the source used for verification
   - `review_notes` -- any relevant observations
4. Save the completed workbook as
   `data/processed/unique_citation_review.xlsx`.

**Estimated time:** 3-5 hours for a reviewer with access to UK legal databases.

---

**Step 5. Build citation summary**

```bash
python src/build_citation_summary.py
```

- **Input:** `data/processed/unique_citation_review.xlsx` (from the manual
  review above)
- **Output:** `data/processed/citation_review_summary.csv` (15 rows),
  `data/processed/citation_review_summary.json`,
  `data/processed/citation_correctness_breakdown.csv` (3 rows)
- **What it does:** Reads the completed manual review workbook and produces
  aggregate correctness metrics. Raises a `ValueError` if any required review
  field is empty.

---

### Phase 3: Holding-accuracy and reasoning-grounding annotation

> **Manual intervention required. Requires an OpenAI API key.**

**Step 6. Pre-fill annotation labels (optional)**

```bash
set OPENAI_API_KEY=sk-...
python src/prefill_holding_grounding.py
```

- **Input:** `annotations/holding_grounding_annotation.xlsx`
- **Output:** Updates the annotation workbook in place with draft R1 labels
- **What it does:** Sends each citation's generated principle and retrieved
  evidence to GPT-4o-mini to produce draft holding-accuracy and
  reasoning-grounding labels. Attempts to fetch authoritative judgment text
  from BAILII; falls back to LLM knowledge if blocked.
- **Flags:** `--dry-run` (print actions without API calls), `--limit N`
  (process only N rows)
- **Cost:** Approximately $0.50-2.00 in OpenAI API usage

> After running, a human reviewer must inspect and correct every draft label.
> The pre-filled labels are starting points for review, not final annotations.
> See `annotations/holding_grounding_codebook.md` for the full annotation
> procedure.

**Manual annotation procedure:**

1. For each citation occurrence in the validation sample (50 judgments, 98
   citations):
   - Look up the authoritative judgment using the evidence-source hierarchy
     defined in the codebook (Section 3).
   - Assign `holding_accuracy`: `yes`, `partial`, `no`, `unclear`, or `n/a`.
   - Inspect the retrieval evidence linked via `search_id`.
   - Assign `reasoning_grounding`: `yes`, `partial`, `no`, `unclear`, or
     `n/a`.
   - Record evidence notes and reviewer confidence.
2. If a second reviewer is available, have them annotate independently.
3. Produce adjudicated final labels in the adjudication columns.

**Estimated time:** 15-25 hours for a single reviewer.

---

### Phase 4: Automated verifier

**Step 7. Run the screening verifier**

```bash
python src/hercules_verifier/hercules_verifier.py ^
  --workbook annotations/holding_grounding_annotation.xlsx ^
  --output outputs/verifier_predictions_v1.csv ^
  --metrics outputs/verifier_metrics_v1.json
```

- **Input:** `annotations/holding_grounding_annotation.xlsx` (with completed
  annotations from step 6)
- **Output:** `outputs/verifier_predictions_v1.csv` (115 rows),
  `outputs/verifier_metrics_v1.json`
- **What it does:** Reads the annotation workbook and produces independent
  predictions for citation status, holding accuracy, and reasoning grounding
  using lexical-similarity heuristics. Copies human-adjudicated labels to the
  output (after prediction) for validation. Computes accuracy, balanced
  accuracy, Cohen's kappa, per-class precision/recall/F1, and confusion
  matrices.
- **Optional flags:**
  - `--authorities <csv>` -- supply authoritative judgment text for
    substantive holding screening
  - `--registry <csv>` -- supply corpus registry for independent
    citation-status verification
  - `--sample-only` -- process only validation-sample rows
  - Threshold overrides: `--holding-yes`, `--holding-partial`,
    `--grounding-yes`, `--grounding-partial`

**Unit tests:**

```bash
cd src/hercules_verifier
python -m unittest discover -s tests -v
```

---

### Phase 5: Analysis and figure generation

These steps are fully automated.

**Step 8. Generate citation-analysis figures**

```bash
python analysis/build_results_figures.py
```

- **Input:** `data/processed/citation_review_summary.csv`,
  `data/processed/citation_correctness_breakdown.csv`,
  `data/processed/citation_retrieval_verification_115.csv`
- **Output:** `outputs/experiments/citation-analysis/figure_1_*.png/.pdf`,
  `figure_2_mentions_by_input_type.png/.pdf`,
  `figure_3_retrieval_outcomes.png/.pdf`,
  `paper_results_metrics.csv`

**Step 9. Generate normalised citation figure**

```bash
python analysis/build_normalized_citation_figure.py
```

- **Input:** `data/processed/judgment_citations_59.csv`
- **Output:** `outputs/experiments/citation-analysis/figure_2_citations_per_judgment.png/.pdf`,
  `input_type_normalized_metrics.csv`

**Step 10. Compute real-vs-synthetic statistical comparisons**

```bash
python analysis/compare_input_groups.py
```

- **Input:** `data/processed/judgment_citations_59.csv`,
  `data/processed/unique_citation_review.xlsx`
- **Output:** `data/processed/input_group_comparison_per_judgment.csv`,
  `data/processed/input_group_comparison_per_input_record.csv`,
  `data/processed/input_group_statistical_comparison.csv/.json`
- **Note:** Uses 20,000 bootstrap iterations and 50,000 permutation iterations.
  Runtime is approximately 30-60 seconds.

**Step 11. Generate holding-accuracy and grounding figures**

```bash
python analysis/build_holding_grounding_figures.py
```

- **Input:** `outputs/verifier_predictions_v1.csv`
- **Output:** `outputs/experiments/annotation-analysis/figure_4_*.png/.pdf`,
  `figure_5_*.png/.pdf`, `figure_6_*.png/.pdf`, `figure_7_*.png/.pdf`,
  `annotation_summary_metrics.csv`

---

## Summary of manual intervention points

| Step | Intervention | Estimated time |
|---|---|---|
| After step 4 | Manual BAILII verification of 35 authority groups | 3-5 hours |
| Step 6 | Set OpenAI API key; review and correct pre-filled labels | 15-25 hours |
| Between steps 6 and 7 | Complete manual annotation of 98 citation occurrences | (included above) |

---

## Notes

- All scripts use `Path(__file__).resolve().parent.parent` to find the project
  root, so they must be run from the project root or the correct relative
  location will be resolved automatically.
- The frozen data exports in `data/raw/` are the authoritative source. If they
  are modified, all downstream outputs will change.
- The annotation workbook in `annotations/` contains the human-adjudicated
  labels. These are the ground truth for validation.
- SHA-256 hashes for all frozen files are recorded in `project_inventory.csv`.