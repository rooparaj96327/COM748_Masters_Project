# Proposal and Completed Work

**Project:** Auditing AI-Generated Draft Judgments: Citation Provenance, Holding Accuracy, and Reasoning Grounding
**Student:** Roopa Raj (B00871016)
**Supervisor:** Professor Jun Liu
**Module:** COM748 Masters Research Project, Ulster University

---

## The Proposal

The proposal set out to audit Hercules, a proof-of-concept legal AI system built at Ulster University's Centre for Legal Technology, funded by the UK AI Security Institute. Hercules takes skeleton arguments from Court of Appeal cases, retrieves similar cases from a vector database (Qdrant), and uses GPT-4o-mini to generate full draft judgments.

The core research question: When Hercules generates a draft judgment, can you trust what it says?

The proposal identified three specific failure types to measure:

1. Invented citations: Does the system cite cases that don't exist?
2. Misrepresented holdings: When it cites a real case, does it describe the case correctly?
3. Ungrounded reasoning: Is the reasoning actually based on the passages the system retrieved?

The proposal planned four phases of work:

- Phase 1-2: Extract citations from Hercules outputs, verify them against the corpus and BAILII.
- Phase 3: Human annotation of holding accuracy and reasoning grounding with two reviewers.
- Phase 4: Controlled experiments, varying retrieval depth, prompt design, and model choice to see what affects output quality.
- Phase 5: Build an automated verifier and validate it against human labels.

Phase 4 was dropped due to time constraints and limited API access. The scope was revised to focus on auditing the frozen output corpus.

---

## The Work Completed

### Data Collection and Extraction (Phase 1)

- Exported 59 draft judgments from the Hercules database (34 from real UK Court of Appeal cases, 25 from synthetic test cases).
- Exported the Qdrant corpus registry (3,654 cases) and semantic search records.
- Extracted 115 citation occurrences (110 case-law, 5 statutory/rule) using regex-based citation extraction.
- Built a pipeline that links each draft judgment to its closest semantic search record.

### Citation Verification (Phase 2)

- Verified all 35 distinct authority groups by hand against BAILII.
- Found zero fabricated cases. Every case the system cited was real.
- Found 8 incomplete and 4 incorrect citations out of 35.
- Classified all 110 case-law occurrences by retrieval status:
  - 59 not found in frozen registry (53.6%)
  - 34 in registry but not retrieved (30.9%)
  - 7 retrieved and cited (6.4%)
  - 9 mismatches (8.2%)
  - 1 conflict (0.9%)
  - The remaining 5 non-case references were tracked separately.

### Human Annotation (Phase 3)

- Developed a 223-line annotation codebook defining labels, evidence sources, and procedures.
- Two reviewers (R1: human, R2: AI-assisted via GPT-4o-mini with human correction) annotated 98 citation occurrences from 50 judgments.
- Each occurrence was assessed on two dimensions:
  - Holding accuracy: Is the legal principle attributed to the case correct?
  - Reasoning grounding: Is the reasoning supported by the retrieved passages?
- Disagreements were resolved through adjudication.

Results:

- Holding accuracy: 47 accurate (48.0%), 30 partial (30.6%), 17 inaccurate (17.3%), 4 n/a (4.1%).
- Reasoning grounding: 3 grounded (3.1%), 11 partial (11.2%), 84 ungrounded (85.7%).

### Automated Verifier (Phase 5)

- Built a 957-line Python verifier that screens all three layers:
  - Layer 1 (citation status): deterministic lookup against the corpus registry.
  - Layer 2 (holding accuracy): TF-IDF cosine similarity against source text.
  - Layer 3 (reasoning grounding): passage similarity against retrieved chunks.
- Validated against human-adjudicated labels using Cohen's Kappa:
  - Citation status: kappa = 0.80 (substantial agreement, 87.8% accuracy). Automation works for this layer.
  - Holding accuracy: kappa = 0.04 (near-zero agreement). Automation fails; human review is essential.
  - Reasoning grounding: kappa = 0.24 (fair agreement, 85.7% accuracy). Accuracy is dominated by the "ungrounded" majority class.

### Analysis and Figures

- Generated 8 figures covering all three layers, input-type comparisons, and verifier validation.
- Ran exploratory real-vs-synthetic comparison with bootstrap confidence intervals, permutation tests, and Hedges' g effect sizes.
- All numbers verified consistent across the annotation workbook, verifier CSV, metrics JSON, and figures.

### Write-Up

- Complete IEEE LaTeX paper (approximately 8 pages) with abstract, introduction, background, methodology, results, discussion, and conclusion.
- Supporting material report (2,400 words) covering extended literature, lifecycle and tools, ethics, and critical appraisal.
- Technical documentation: data dictionary, reproduction guide, figures index.
- Frozen dataset with SHA-256 checksums and baseline manifest.

---

## The Key Finding

The system does not invent cases. Zero fabrications were found out of 33 case-law authorities. But that makes it more dangerous, not less. Half the holdings were wrong, and 85.7% of reasoning was ungrounded. Because the citations are real, the output looks credible while being substantively unreliable. A citation existence check (the easiest thing to automate) would give it a clean bill of health. The deeper problems, such as a real case cited for a reversed holding or a medical case cited in a highways dispute, require human legal expertise to catch.

That is the thesis: citation existence is necessary but insufficient for legal AI reliability.