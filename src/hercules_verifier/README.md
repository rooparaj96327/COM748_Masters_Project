# Hercules Verifier

`hercules_verifier.py` is a reproducible screening and validation program for
the COM748 project *Auditing AI-Generated Draft Judgments: Citation Provenance,
Holding Accuracy, and Reasoning Grounding*.

It reads the existing annotation workbook and produces one prediction row for
each citation occurrence. It does **not** overwrite the workbook or use R1, R2,
or adjudicated labels to make predictions. Human labels are copied to the
output only after prediction so they can be used for validation.

## What it verifies

1. **Citation status**
   - `retrieved_and_cited`
   - `in_corpus_not_retrieved`
   - `retrieved_id_citation_mismatch`
   - `not_found_in_corpus_registry`
   - `not_applicable_non_case_reference`

2. **Holding accuracy screening**
   - Uses supplied authoritative judgment text when available.
   - Returns `unclear` when the source text is unavailable.
   - Uses lexical evidence only as a screening heuristic. Final legal labels
     should come from expert review.

3. **Reasoning grounding screening**
   - Uses only the `Retrieved Evidence` rows linked by `search_id`.
   - Checks whether the cited authority was retrieved.
   - Scores the generated application against the closest linked passage.

4. **Validation**
   - Compares predictions with adjudicated labels when present.
   - Reports exact accuracy, balanced accuracy, Cohen's Kappa, per-class
     precision/recall/F1, and confusion matrices.

## Requirements

- Python 3.10 or later
- `openpyxl`

Install the dependency:

```bash
python -m pip install -r requirements.txt
```

## Basic use

```bash
python hercules_verifier.py \
  --workbook holding_grounding_annotation.xlsx \
  --output verifier_predictions.csv \
  --metrics verifier_metrics.json
```

The workbook must contain these sheets:

- `Annotations`
- `Retrieved Evidence`

The names can be changed with `--annotations-sheet` and `--evidence-sheet`.

## Authoritative holding sources

Holding accuracy cannot be verified responsibly from a citation, title, or
retrieval score alone. To enable automated holding screening, supply a CSV:

```bash
python hercules_verifier.py \
  --workbook holding_grounding_annotation.xlsx \
  --authorities examples/authoritative_sources_template.csv \
  --output verifier_predictions.csv
```

Required/recognised columns are:

- `citation`
- `title`
- `source_url`
- `source_paragraphs`
- `authoritative_text`

Place the relevant judgment paragraphs—not merely a case summary—in
`authoritative_text`.

## Optional corpus registry

For citation-status verification independent of workbook flags, supply a
registry CSV:

```bash
python hercules_verifier.py \
  --workbook holding_grounding_annotation.xlsx \
  --registry examples/corpus_registry_template.csv \
  --ignore-workbook-registry-flags \
  --output verifier_predictions.csv
```

Recognised aliases include:

- ID: `case_id`, `id`, `retrieved_case_id`, `corpus_case_id`
- title: `title`, `case_title`, `retrieved_case_title`
- citation: `citation`, `neutral_citation`, `case_citation`
- text: `full_text`, `judgment_text`, `text`, `chunk_content`

Without a registry CSV, the program can use the workbook's prefilled
`citation_in_corpus_registry` and `citation_in_linked_retrieval` fields. These
are automated evidence fields, not R1/R2 labels. Use
`--ignore-workbook-registry-flags` for a strict independent run.

## Thresholds

The defaults are conservative lexical-screening thresholds:

```text
--holding-yes 0.55
--holding-partial 0.25
--grounding-yes 0.35
--grounding-partial 0.15
```

Thresholds should be selected before inspecting aggregate human-validation
results. If changed, record the values and reason in the methodology.

## Output files

The prediction CSV is compatible with the supplied `verifier_predictions.csv`
structure. The metrics JSON records:

- program version and parameters;
- row and judgment coverage;
- prediction distributions;
- score summaries;
- validation metrics and confusion matrices.

## Recommended reporting language

Describe the program as an **automated screening verifier**. Do not claim that
lexical similarity alone establishes whether a legal holding is accurate.
Where authoritative text is unavailable, `unclear` is the correct automated
result under the project codebook.

## Tests

Run:

```bash
python -m unittest discover -s tests -v
```