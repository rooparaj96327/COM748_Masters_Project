# Data Dictionary

This document describes every CSV, JSON, and XLSX output file produced by the
analysis pipeline. For each file: filename, description, row count, and column
definitions.

---

## 1. Processed data files (`data/processed/`)

### 1.1 `judgment_citations_59.csv`

**Description:** Extracted citation occurrences from 59 Hercules-generated draft
judgments. Each row represents one citation mention within one draft.

**Row count:** 115  
**Companion file:** `judgment_citations_59.json` (same data in JSON format)

| Column | Type | Description |
|---|---|---|
| `draft_id` | string | Unique identifier for the generated draft judgment. |
| `skeleton_arguments_id` | string | Identifier for the skeleton argument document the draft was generated from. |
| `case_doc_id` | string | Identifier for the source case document used as Hercules input. |
| `input_type` | string | Whether the input was `real` (genuine skeleton argument) or `synthetic` (AI-generated skeleton argument). Classified by whether `case_doc_id` starts with `skeleton-args`. |
| `model_used` | string | The LLM model used by Hercules to generate the draft (e.g., `gpt-4o-mini`). |
| `generated_at` | datetime | Timestamp when the draft judgment was generated. |
| `citation_index` | integer | Ordinal position of this citation within its draft (1-based). |
| `citation` | string | Full citation text as it appears in the generated judgment. |
| `citation_normalized` | string | Lowercased, cleaned version of the citation used for deduplication and matching. |
| `citation_type` | string | Classification: `case_law`, `legislation_or_rule`, or `other_reference`. |
| `pinpoint` | string | Specific paragraph or section reference within the cited authority (e.g., `at [45]`), or empty. |
| `principle` | string | The legal principle attributed to the cited authority by Hercules. |
| `application` | string | How Hercules applies the cited principle to the case at hand. |
| `binding_authority` | string | Whether the citation is claimed as `binding` or `persuasive`. |
| `linked_source_case_count` | integer | Number of source cases from the retrieval that Hercules explicitly linked to this citation. |
| `source_case_ids` | string | Pipe-delimited (`\|\|`) UUIDs of explicitly linked source cases. |
| `source_case_titles` | string | Pipe-delimited titles of those linked source cases. |
| `source_case_citations` | string | Pipe-delimited formal citations of those linked source cases. |

---

### 1.2 `retrieval_linkage_59.csv`

**Description:** Links each of the 59 draft judgments to its closest exported
semantic-search retrieval record. Each row represents one draft-to-search
linkage.

**Row count:** 59  
**Companion file:** `retrieval_linkage_59.json`

| Column | Type | Description |
|---|---|---|
| `draft_id` | string | Unique identifier for the generated draft judgment. |
| `skeleton_arguments_id` | string | Identifier for the skeleton argument document. |
| `case_doc_id` | string | Identifier for the source case document. |
| `input_type` | string | `real` or `synthetic`. |
| `model_used` | string | LLM model used (e.g., `gpt-4o-mini`). |
| `generated_at` | datetime | Timestamp of draft generation. |
| `search_id` | string | Identifier for the vector-search retrieval run linked to this draft. |
| `searched_at` | datetime | Timestamp when the retrieval search was executed. |
| `match_method` | string | How the search was matched to the draft (e.g., `latest_search_before_draft`). |
| `search_to_draft_seconds` | float | Time in seconds between the search execution and draft generation. |
| `search_type` | string | Type of search performed (e.g., `advanced_qdrant_search`). |
| `reported_total_results` | integer | Total number of results the search reported. |
| `retrieved_cases_in_export` | integer | Number of retrieved cases actually present in the export. |
| `average_similarity` | float | Mean cosine similarity score across all retrieved cases. |
| `top_retrieved_case` | string | Title of the highest-similarity retrieved case. |
| `top_similarity_score` | float | Cosine similarity score of the top retrieved case. |
| `retrieved_case_ids` | string | Pipe-delimited UUIDs of all retrieved cases. |
| `retrieved_case_titles` | string | Pipe-delimited titles of all retrieved cases. |
| `similarity_scores` | string | Pipe-delimited similarity scores corresponding to each retrieved case. |

---

### 1.3 `citation_retrieval_verification_115.csv`

**Description:** Cross-references each of the 115 extracted citations against
the linked retrieval record and the frozen Qdrant corpus registry. Assigns a
verification status to each citation.

**Row count:** 115  
**Companion file:** `citation_retrieval_verification_115.json`

| Column | Type | Description |
|---|---|---|
| `draft_id` | string | Unique identifier for the generated draft judgment. |
| `skeleton_arguments_id` | string | Identifier for the skeleton argument document. |
| `case_doc_id` | string | Identifier for the source case document. |
| `input_type` | string | `real` or `synthetic`. |
| `model_used` | string | LLM model used. |
| `generated_at` | datetime | Timestamp of draft generation. |
| `citation_index` | integer | Ordinal position of this citation within its draft. |
| `citation` | string | Full citation text as generated. |
| `citation_normalized` | string | Lowercased/cleaned citation for matching. |
| `citation_type` | string | `case_law`, `legislation_or_rule`, or `other_reference`. |
| `pinpoint` | string | Specific paragraph or section reference within the authority. |
| `principle` | string | Legal principle attributed to the authority. |
| `application` | string | How the principle is applied. |
| `binding_authority` | string | `binding` or `persuasive`. |
| `linked_source_case_count` | integer | Number of source cases explicitly linked from retrieval. |
| `source_case_ids` | string | Pipe-delimited IDs of linked source cases. |
| `source_case_titles` | string | Pipe-delimited titles of linked source cases. |
| `source_case_citations` | string | Pipe-delimited formal citations of linked source cases. |
| `citation_used_for_matching` | string | The citation string used to match against corpus and retrieval records. |
| `search_id` | string | The retrieval search run linked to this draft. |
| `verification_status` | string | Outcome of verification: `retrieved_and_cited`, `in_corpus_not_retrieved`, `not_found_in_corpus_registry`, `retrieved_id_citation_mismatch`, or `not_applicable_non_case_reference`. |
| `citation_in_linked_retrieval` | string | Whether the citation was found in the linked retrieval results (`yes` / `no`). |
| `citation_in_corpus_registry` | string | Whether the citation was found in the full corpus registry (`yes` / `no`). |
| `match_method` | string | How the match was established: `exact_case_name`, `citation_identifier`, `explicit_source_id+citation_identifier`, or `no_match`. |
| `match_score` | float | Numeric match quality score (0.0 or 1.0). |
| `matched_retrieved_case_id` | string | UUID of the matching case in the retrieval results (if any). |
| `matched_retrieved_case_title` | string | Title of that matching retrieved case. |
| `explicit_source_case_id` | string | UUID of the explicit source case linked by Hercules. |
| `explicit_source_case_title` | string | Title of that explicit source case. |
| `matched_corpus_case_id` | string | UUID of the matching case in the corpus registry. |
| `matched_corpus_case_title` | string | Title of that corpus registry case. |
| `invalid_source_case_ids` | string | Any source case IDs that were found to be invalid. |
| `citation_identifier_conflict` | string | Whether a conflict exists between the citation text and its identifier (`yes` / `no`). |
| `manual_review_required` | string | Whether manual review is flagged (`yes` / `no`). |
| `review_reason` | string | Free-text explanation of the verification outcome. |

---

### 1.4 `unique_citation_review.csv`

**Description:** Deduplicated authority-group view of all citations, grouping
the 115 citation occurrences into 35 unique authority groups for manual
correctness review.

**Row count:** 35  
**Companion files:** `unique_citation_review.json`, `unique_citation_review.xlsx`
(the XLSX version contains additional manually completed review columns),
`unique_citation_review_V1.xlsx` (earlier version)

| Column | Type | Description |
|---|---|---|
| `authority_key` | string | Normalised deduplication key for the authority (e.g., `case:english v emery reimbold and strick ltd`). |
| `authority` | string | Representative citation string for the authority group. |
| `citation_type` | string | `case_law` or `legislation_or_rule`. |
| `mention_count` | integer | Total number of times this authority was cited across all 59 drafts. |
| `judgment_count` | integer | Number of distinct draft judgments that cited this authority. |
| `real_mentions` | integer | Number of mentions from real-input drafts. |
| `real_judgment_count` | integer | Number of real-input judgments citing this authority. |
| `synthetic_mentions` | integer | Number of mentions from synthetic-input drafts. |
| `synthetic_judgment_count` | integer | Number of synthetic-input judgments citing this authority. |
| `retrieved_and_cited_mentions` | integer | Mentions where the authority was found in the retrieval results and cited. |
| `corpus_not_retrieved_mentions` | integer | Mentions where the authority exists in the corpus but was not retrieved. |
| `not_found_in_registry_mentions` | integer | Mentions where the authority was not found in the corpus registry. |
| `source_id_mismatch_mentions` | integer | Mentions where the source ID pointed to a different case than the citation. |
| `citation_conflict_mentions` | integer | Mentions with a conflict between citation text and matched record. |
| `invalid_source_id_mentions` | integer | Mentions with an invalid source case ID. |
| `statuses_observed` | string | Summary of verification statuses and their counts for this authority. |
| `citation_variants` | string | Pipe-delimited list of all textual variants of this citation observed across drafts. |
| `matched_retrieved_cases` | string | Case titles matched from retrieval results. |
| `matched_corpus_cases` | string | Case titles matched from the corpus registry. |
| `invalid_source_ids` | string | Any invalid source case IDs associated with this authority. |
| `review_priority` | string | Priority level for manual review: `high`, `medium`, or `low`. |
| `manual_review_needed` | string | Whether manual review is needed (`yes` / `no`). |
| `case_exists_external` | string | Whether the case was confirmed to exist via BAILII or other external source. Populated during manual review. |
| `citation_correct_external` | string | Whether the citation was confirmed correct externally: `yes`, `incomplete`, or `no`. Populated during manual review. |
| `authoritative_source_url` | string | URL to the authoritative source for the citation. Populated during manual review. |
| `review_notes` | string | Free-text notes from the manual review process. |

---

### 1.5 `citation_review_summary.csv`

**Description:** Summary metrics from the manual citation correctness review.

**Row count:** 15  
**Companion file:** `citation_review_summary.json`

| Column | Type | Description |
|---|---|---|
| `metric` | string | Name of the summary metric. |
| `value` | integer | Numeric value. |

**Metric rows:**

| Metric | Description |
|---|---|
| `reviewed_authority_groups` | Total authority groups reviewed (35). |
| `citation_mentions` | Total citation mentions (115). |
| `real_case_mentions` | Mentions from real-input drafts (63). |
| `synthetic_case_mentions` | Mentions from synthetic-input drafts (52). |
| `case_law_authority_groups` | Authority groups classified as case law (33). |
| `non_case_reference_groups` | Authority groups classified as legislation or rule (2). |
| `externally_confirmed_cases` | Cases confirmed to exist via external sources (32). |
| `ambiguous_case_references` | Cases with ambiguous external verification (1). |
| `non_case_references` | Non-case reference groups (2). |
| `correct_citations` | Authority groups with correct citations (23). |
| `incomplete_citations` | Authority groups with incomplete citations (8). |
| `incorrect_citations` | Authority groups with incorrect citations (4). |
| `high_priority_reviews` | Authority groups flagged as high priority (8). |
| `medium_priority_reviews` | Authority groups flagged as medium priority (20). |
| `low_priority_reviews` | Authority groups flagged as low priority (7). |

---

### 1.6 `citation_correctness_breakdown.csv`

**Description:** Citation correctness aggregated by external verification
status. Shows how many authority groups and total mentions fall into each
correctness category.

**Row count:** 3

| Column | Type | Description |
|---|---|---|
| `citation_status` | string | Overall correctness verdict: `yes` (correct), `incomplete`, or `no` (incorrect). |
| `authority_groups` | integer | Number of unique authority groups with this status. |
| `mentions` | integer | Total citation mentions with this status. |
| `real_mentions` | integer | Mentions from real-input drafts with this status. |
| `synthetic_mentions` | integer | Mentions from synthetic-input drafts with this status. |

---

### 1.7 `input_group_comparison_per_judgment.csv`

**Description:** Per-judgment citation metrics for the real-vs-synthetic
exploratory comparison. Each row represents one draft judgment.

**Row count:** 59

| Column | Type | Description |
|---|---|---|
| `draft_id` | string | Unique identifier for the generated draft judgment. |
| `case_doc_id` | string | Source case document identifier. |
| `input_type` | string | `real` or `synthetic`. |
| `citation_mentions` | integer | Total citation mentions in this judgment. |
| `correct_mentions` | integer | Mentions where the authority was externally verified as correct. |
| `incomplete_mentions` | integer | Mentions where the authority was externally verified as incomplete. |
| `incorrect_mentions` | integer | Mentions where the authority was externally verified as incorrect. |
| `strict_defect_mentions` | integer | Mentions that are either incomplete or incorrect. |
| `strict_defect_rate` | float | Proportion of mentions in this judgment that are incomplete or incorrect. |
| `incorrect_rate` | float | Proportion of mentions in this judgment that are incorrect. |

---

### 1.8 `input_group_comparison_per_input_record.csv`

**Description:** Per-input-record citation metrics for the real-vs-synthetic
comparison. Each row represents one unique input document (some input documents
produced multiple draft judgments).

**Row count:** 34

| Column | Type | Description |
|---|---|---|
| `case_doc_id` | string | Source case document identifier. |
| `input_type` | string | `real` or `synthetic`. |
| `judgment_count` | integer | Number of draft judgments generated from this input. |
| `citation_mentions` | integer | Total citation mentions across all judgments from this input. |
| `mean_citations_per_judgment` | float | Average citations per judgment for this input. |
| `correct_mentions` | integer | Mentions externally verified as correct. |
| `incomplete_mentions` | integer | Mentions externally verified as incomplete. |
| `incorrect_mentions` | integer | Mentions externally verified as incorrect. |
| `strict_defect_rate` | float | Proportion of all mentions from this input that are incomplete or incorrect. |
| `incorrect_rate` | float | Proportion of all mentions from this input that are incorrect. |

---

### 1.9 `input_group_statistical_comparison.csv`

**Description:** Statistical comparison results for real-vs-synthetic input
groups. Contains bootstrap confidence intervals, permutation test p-values,
and Hedge's g effect sizes.

**Row count:** 6  
**Companion file:** `input_group_statistical_comparison.json`

| Column | Type | Description |
|---|---|---|
| `analysis_level` | string | Level of analysis: `judgment` or `input_record`. |
| `metric` | string | The metric compared: `citation_mentions`, `strict_defect_rate`, or `incorrect_rate` (judgment level); `mean_citations_per_judgment`, `strict_defect_rate`, or `incorrect_rate` (input-record level). |
| `real_n` | integer | Sample size for the real-input group. |
| `real_mean` | float | Mean value for the real-input group. |
| `real_median` | float | Median value for the real-input group. |
| `real_standard_deviation` | float | Standard deviation for the real-input group. |
| `synthetic_n` | integer | Sample size for the synthetic-input group. |
| `synthetic_mean` | float | Mean value for the synthetic-input group. |
| `synthetic_median` | float | Median value for the synthetic-input group. |
| `synthetic_standard_deviation` | float | Standard deviation for the synthetic-input group. |
| `mean_difference_synthetic_minus_real` | float | Difference in means (synthetic minus real). |
| `bootstrap_95_ci_low` | float | Lower bound of the 95% bootstrap confidence interval for the mean difference. |
| `bootstrap_95_ci_high` | float | Upper bound of the 95% bootstrap confidence interval for the mean difference. |
| `permutation_p_value_two_sided` | float | Two-sided permutation test p-value. |
| `hedges_g` | float | Hedge's g effect size (bias-corrected standardised mean difference). |

---

## 2. Output files (`outputs/`)

### 2.1 `verifier_predictions_v1.csv`

**Description:** Predictions from the automated screening verifier for all 115
citation occurrences. Each row contains the verifier's predicted labels,
numeric scores, evidence text, and (for the 98 validation-sample rows) the
human-adjudicated ground-truth labels for comparison.

**Row count:** 115

| Column | Type | Description |
|---|---|---|
| `draft_id` | string | Unique identifier for the generated draft judgment. |
| `search_id` | string | Identifier for the retrieval search linked to the draft. |
| `citation` | string | The citation text being verified. |
| `citation_kind` | string | Classification of the citation form: `neutral` (neutral citation), `report` (law report), `unknown`, `legislation`, or `rule`. |
| `predicted_citation_status` | string | Verifier's predicted citation-retrieval status: `retrieved_and_cited`, `in_corpus_not_retrieved`, `not_found_in_corpus_registry`, `retrieved_id_citation_mismatch`, or `not_applicable_non_case_reference`. |
| `predicted_holding_accuracy` | string | Verifier's predicted holding accuracy: `unclear` or `n/a` (substantive labels require authoritative source text, which was not supplied). |
| `predicted_reasoning_grounding` | string | Verifier's predicted reasoning grounding: `no` or `partial`. |
| `holding_score` | float | Numeric lexical-similarity score for holding accuracy (0.0 throughout, as no authoritative text was supplied). |
| `grounding_score` | float | Numeric lexical-similarity score for reasoning grounding (range 0.0016 to 0.3409). |
| `holding_source` | string | Source of holding evidence (`none` throughout). |
| `cited_authority_retrieved` | boolean | Whether the cited authority was found in the linked retrieval (`True` / `False`). |
| `best_passage_rank` | integer | Rank of the best-matching passage from retrieval for this citation. |
| `best_passage_case_id` | string | UUID of the case containing the best-matching passage. |
| `best_passage_chunk_id` | string | Identifier for the specific chunk of the best-matching passage. |
| `best_passage_chunk_type` | string | Type of the best passage chunk (e.g., `case_analysis`, `legal_reasoning`, `legal_classification`, `citations_precedents`, `metadata_summary`, `outcome_holding`, `procedural_history`). |
| `holding_evidence` | string | Textual evidence supporting the holding accuracy prediction. |
| `grounding_evidence` | string | Textual evidence supporting the reasoning grounding prediction, including passage excerpts. |
| `notes` | string | Additional notes about the verification. |
| `case_doc_id` | string | Source case document identifier. |
| `input_type` | string | `real` or `synthetic`. |
| `citation_index` | integer | Ordinal position of citation within its draft. |
| `in_validation_sample` | string | Whether this row is part of the 98-row validation sample (`yes` / `no`). |
| `citation_verification_status` | string | Ground-truth citation-retrieval status from manual verification in the annotation workbook. |
| `adjudicated_holding_accuracy` | string | Adjudicated (ground-truth) holding accuracy label: `yes`, `partial`, `no`, or `n/a`. |
| `adjudicated_reasoning_grounding` | string | Adjudicated (ground-truth) reasoning grounding label: `yes`, `partial`, or `no`. |
| `holding_accuracy_R1` | string | Reviewer 1's holding accuracy annotation. |
| `holding_accuracy_R2` | string | Reviewer 2's holding accuracy annotation (may be empty if single reviewer). |
| `reasoning_grounding_R1` | string | Reviewer 1's reasoning grounding annotation. |
| `reasoning_grounding_R2` | string | Reviewer 2's reasoning grounding annotation (may be empty if single reviewer). |

---

### 2.2 `verifier_metrics_v1.json`

**Description:** Validation metrics comparing the verifier's predictions against
human-adjudicated labels. Not tabular; structured as a nested JSON object.

| Key | Type | Description |
|---|---|---|
| `verifier_version` | string | Version of the verifier program (`1.0.0`). |
| `input_workbook` | string | Name of the annotation workbook used. |
| `parameters` | object | Verifier configuration: `sample_only`, `use_workbook_registry_flags`, `authoritative_sources_supplied`, `corpus_registry_supplied`, and `thresholds` (holding/grounding score thresholds). |
| `coverage` | object | `citation_occurrences` (115), `unique_drafts` (59), `validation_occurrences` (98). |
| `prediction_distributions` | object | Count distributions for `citation_status`, `holding_accuracy`, `reasoning_grounding`, and `holding_source`. |
| `score_summaries` | object | Min, median, mean, and max for `holding` scores (all 0.0) and `grounding` scores (min 0.0016, median 0.1206, mean 0.134, max 0.3409). |
| `validation` | object | Per-task validation: `citation_status` (kappa 0.80, accuracy 87.8%), `holding_accuracy` (kappa 0.04, accuracy 4.1% -- expected since no authoritative text was supplied), `reasoning_grounding` (kappa 0.24, accuracy 85.7%). Each includes `paired_rows`, `exact_accuracy`, `balanced_accuracy`, `cohens_kappa`, `macro_f1_defined_classes`, `confusion_matrix_predicted_by_truth`, and `per_class` precision/recall/F1. |

---

### 2.3 `outputs/experiments/citation-analysis/paper_results_metrics.csv`

**Description:** Summary metrics table for the citation analysis, formatted for
inclusion in the research paper.

**Row count:** 9

| Column | Type | Description |
|---|---|---|
| `metric` | string | Name of the metric (e.g., `Correct authority-group citations`, `Retrieved and cited records`). |
| `count` | integer | Raw count for that metric. |
| `denominator` | integer | Total against which the count is measured (35 for authority-group metrics, 115 for citation-mention metrics). |
| `percentage` | float | The count as a percentage of the denominator. |

---

### 2.4 `outputs/experiments/citation-analysis/input_type_normalized_metrics.csv`

**Description:** Normalised citation statistics per input type, used for the
mean-citations-per-judgment comparison figure.

**Row count:** 2

| Column | Type | Description |
|---|---|---|
| `input_type` | string | `real` or `synthetic`. |
| `judgments` | integer | Number of judgments of that input type. |
| `citation_mentions` | integer | Total citation mentions. |
| `mean_citations_per_judgment` | float | Average citations per judgment. |
| `standard_deviation` | float | Standard deviation of citations per judgment. |
| `confidence_interval_95` | float | 95% confidence interval half-width for the mean. |

---

### 2.5 `outputs/experiments/annotation-analysis/annotation_summary_metrics.csv`

**Description:** Summary metrics for the holding-accuracy and reasoning-grounding
annotation results on the 98-row validation sample.

**Row count:** 10

| Column | Type | Description |
|---|---|---|
| `metric` | string | Name of the annotation metric. |
| `count` | integer | Raw count. |
| `denominator` | integer | Total (98 for all rows). |
| `percentage` | float | Percentage of the denominator. |

**Metric rows:**

| Metric | Description |
|---|---|
| `holding_yes` | Citation occurrences with accurate holdings (47). |
| `holding_partial` | Citation occurrences with partially accurate holdings (30). |
| `holding_no` | Citation occurrences with inaccurate holdings (17). |
| `holding_n/a` | Citation occurrences where holding accuracy is not applicable (4). |
| `grounding_yes` | Citation occurrences with grounded reasoning (3). |
| `grounding_partial` | Citation occurrences with partially grounded reasoning (11). |
| `grounding_no` | Citation occurrences with ungrounded reasoning (84). |
| `validation_sample_total` | Total citation occurrences in the validation sample (98). |
| `real_in_sample` | Real-input citation occurrences in the sample (55). |
| `synthetic_in_sample` | Synthetic-input citation occurrences in the sample (43). |

---

## 3. Annotation files (`annotations/`)

### 3.1 `holding_grounding_annotation.xlsx`

**Description:** Manual annotation workbook containing human-adjudicated labels
for holding accuracy and reasoning grounding. Contains two sheets.

**Sheet: Annotations**  
Each row represents one citation occurrence in the validation sample. Contains
reviewer labels (R1, R2), adjudicated labels, evidence notes, and confidence
scores. See `holding_grounding_codebook.md` for full field definitions.

**Sheet: Retrieved Evidence**  
Contains the retrieved passages linked to each draft judgment via `search_id`,
used as evidence for reasoning-grounding assessment.

### 3.2 `holding_grounding_codebook.md`

**Description:** Annotation codebook defining all label categories, decision
rules, evidence-source hierarchy, annotation procedure, inter-rater
validation requirements, and quality-control rules.
