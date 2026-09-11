# Auditing AI-Generated Draft Judgments: Citation Provenance, Holding Accuracy, and Reasoning Grounding

**COM748 Masters Research Project**  
**Student:** Roopa Raj (B00871016)  
**Supervisor:** Professor Jun Liu  
**Module:** COM748, School of Computing, Ulster University  
**Submission:** 14 September 2026

## Project Overview

This project carries out a structured empirical audit of Hercules, a proof-of-concept legal AI system developed at Ulster University's Centre for Legal Technology. Hercules generates draft judgments for the Court of Appeal (Civil Division) using retrieval-augmented generation. The audit measures three failure types: invented citations, misrepresented holdings, and ungrounded reasoning.

## Dataset Summary

| Metric | Count |
|---|---|
| Draft judgments analysed | 59 |
| Citation occurrences | 115 (110 case law, 5 statutory/rule) |
| Distinct authority groups | 35 (33 case law, 2 non-case) |
| Validation sample | 98 citation occurrences |
| Real-input judgments | 34 |
| Synthetic-input judgments | 25 |

Data frozen: 2026-08-31. No controlled experiments (retrieval depth, prompt design, model choice) were run; scope was revised to focus on auditing the frozen Hercules output corpus.

## Project Structure

```
COM748_Hercules_Audit/
  paper/                          Research paper (IEEE LaTeX)
    main.tex                      Complete paper source
  src/                            Analysis pipeline
    extract_judgment_citations.py   Step 1: citation extraction
    build_retrieval_analysis.py     Step 2: draft-to-search linkage
    verify_citation_retrieval.py    Step 3: citation-retrieval verification
    build_unique_citation_review.py Step 4: authority group deduplication
    build_citation_summary.py       Step 5: summary metrics
    prefill_holding_grounding.py    Step 6: LLM-assisted annotation prefill
    export-corpus-registry.ts       Qdrant corpus registry export
    hercules_verifier/              Automated screening verifier
  analysis/                       Figure and statistics generation
    build_results_figures.py        Figures 1-3 (citation analysis)
    build_normalized_citation_figure.py  Figure 2b (normalized)
    compare_input_groups.py         Real vs synthetic comparison
    build_holding_grounding_figures.py   Figures 4-7 (annotations)
  data/
    raw/                          Frozen source data
      database-exports/             Hercules database exports
      system-exports/qdrant/        Qdrant corpus registry
      input-documents/              Skeleton argument PDFs and XMLs
    processed/                    Pipeline outputs (CSVs, JSONs)
  annotations/                    Human annotation workbook and codebook
    holding_grounding_annotation.xlsx
    holding_grounding_codebook.md
  outputs/
    baseline/                     Audit workbooks
    experiments/
      citation-analysis/            Figures 1-3 + metrics CSVs
      annotation-analysis/          Figures 4-7 + annotation metrics
    verifier_predictions_v1.csv   Verifier predictions + human labels
    verifier_metrics_v1.json      Validation metrics (Cohen's Kappa)
  supporting-material/            Submission supporting materials
    README.md                       Package overview
    data-dictionary.md              Column-level data documentation
    reproduction-guide.md           Step-by-step reproduction instructions
    figures-index.md                Index of all report figures
  documentation/                  Project documentation
    ethics/                         Ethics approval documents
  baseline_manifest.txt           Freeze summary and methodological notes
  project_inventory.csv           File-level inventory with SHA-256 hashes
```

## Key Results

- **0 fabricated cases** out of 33 distinct case-law authorities verified against BAILII
- **53.6%** of case-law citations absent from the system's corpus
- **50.0%** of attributed holdings partially or fully inaccurate (human annotation)
- **85.7%** of reasoning steps ungrounded in retrieved passages
- **Citation verifier validated:** Cohen's Kappa = 0.80 (substantial agreement)

## Reproduction

See `supporting-material/reproduction-guide.md` for full instructions. Requires Python 3.14+ with openpyxl, matplotlib, and numpy.

## Methodological Notes

- The verifier is an automated screening tool. Without authoritative judgment text, it returns `unclear` for holding accuracy. Human annotation provides the substantive holding-accuracy labels.
- The real-versus-synthetic comparison is exploratory. The sample is a convenience sample and should not be presented as representative of all Hercules use cases.
- Controlled experiments (retrieval depth, prompt design, model choice) were planned but not executed; they are discussed as future work in the paper.
