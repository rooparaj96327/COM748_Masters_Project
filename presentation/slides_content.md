# Presentation Slides Content
# Copy each slide into PowerPoint

---

## SLIDE 1: Title Slide

**Auditing AI-Generated Draft Judgments:**
**Citation Provenance, Holding Accuracy, and Reasoning Grounding**

Roopa Raj (B00871016)
Supervisor: Professor Jun Liu

COM748 Masters Research Project
School of Computing, Ulster University
September 2026

---

## SLIDE 2: Agenda

- Project Background and Motivation
- Research Question and Objectives
- The Hercules System
- Methodology: Three-Layer Audit Framework
- Results
  - Layer 1: Citation Provenance
  - Layer 2: Holding Accuracy
  - Layer 3: Reasoning Grounding
- Automated Verifier Validation
- Discussion and Key Findings
- Conclusions and Future Work
- Questions?

---

## SLIDE 3: Project Background and Related Work

**The problem:**
- Large language models are increasingly proposed for judicial decision support
- These systems can fabricate legal authorities, misstate case holdings, or produce ungrounded reasoning
- In a judicial context, such failures threaten fairness and the rule of law

**Related work:**
| Author | Contribution |
|---|---|
| Magesh et al. (2024) | Found leading AI legal research tools hallucinate 17-33% of the time |
| Maynez et al. (2020) | Showed abstractive summarisation produces intrinsic and extrinsic hallucinations |
| Ji et al. (2023) | Comprehensive survey of hallucination in natural language generation |
| UK Judicial Office (2023) | Permits AI for summarisation but warns against reliance without verification |

**Gap:** No structured citation-level audit of a legal-AI system generating full draft judgments.

---

## SLIDE 4: Research Question and Objectives

**Research question:**
*When Hercules generates a draft judgment, can you trust what it says?*

**Objectives:**
1. Extract and classify citations from AI-generated draft judgments
2. Verify citation existence against an external legal corpus (BAILII)
3. Assess holding accuracy through dual-reviewer human annotation
4. Assess reasoning grounding against retrieved passages
5. Build and validate an automated screening verifier

**Scope change:** Controlled experiments (Phase 4) were dropped due to time constraints. Focus revised to auditing the frozen output corpus.

---

## SLIDE 5: The Hercules System

**Hercules** is a proof-of-concept legal AI system developed at Ulster University's Centre for Legal Technology, funded by the UK AI Security Institute.

**Architecture:**
- **Input:** Skeleton arguments (PDF/XML) from Court of Appeal cases
- **Retrieval:** Qdrant vector database (3,654 historical cases, 29,232 chunks)
- **Structured data:** Neon/PostgreSQL (2,541 case records)
- **Generation:** OpenAI GPT-4o-mini
- **Output:** Full draft judgments with citations and legal reasoning

**Dataset:**
| Metric | Count |
|---|---|
| Draft judgments analysed | 59 |
| Citation occurrences | 115 (110 case-law, 5 statutory) |
| Distinct authority groups | 35 |
| Real-input judgments | 34 |
| Synthetic-input judgments | 25 |

---

## SLIDE 6: Methodology - Three-Layer Audit Framework

**Layer 1: Citation Provenance**
- Can each citation be traced to the system's corpus registry and retrieval records?
- Deterministic lookup against frozen Neon registry + linked Qdrant retrieval

**Layer 2: Holding Accuracy**
- When the system cites a real case, does it describe the holding correctly?
- Dual-reviewer annotation (R1 human, R2 AI-assisted) with adjudication
- Labels: yes, partial, no, n/a

**Layer 3: Reasoning Grounding**
- Is the reasoning supported by the passages the system actually retrieved?
- Dual-reviewer annotation against linked retrieval chunks
- Labels: yes, partial, no

**Validation sample:** 50 judgments, 98 citation occurrences

---

## SLIDE 7: Results - Layer 1: Citation Provenance

**Zero fabricated cases** out of 33 distinct case-law authorities verified against BAILII.

**But 53.6% of citations had no provenance trail:**

| Retrieval Status | Count | % (of 110 case-law) |
|---|---|---|
| Not found in corpus registry | 59 | 53.6% |
| In corpus, not retrieved | 34 | 30.9% |
| Retrieved and cited | 7 | 6.4% |
| Retrieval mismatch | 9 | 8.2% |
| Case-name conflict | 1 | 0.9% |

**Citation correctness (35 authority groups):**
- 23 correct (65.7%)
- 8 incomplete (22.9%)
- 4 incorrect (11.4%)

[FIGURE: Include figure_3_retrieval_outcomes.png]

---

## SLIDE 8: Results - Layer 2: Holding Accuracy

**50% of holdings were partially or fully inaccurate**

| Holding Label | Count | % |
|---|---|---|
| Accurate (yes) | 47 | 48.0% |
| Partially accurate | 30 | 30.6% |
| Inaccurate (no) | 17 | 17.3% |
| Not applicable | 4 | 4.1% |

**Example of misrepresented holding:**
- *Chapman v Mid & South Essex NHS Foundation Trust* [2023]: System cited it for "statutory control over public safety for cyclists and pedestrians"
- Actual case: a clinical-negligence case about delayed diagnosis of a spinal condition, completely unrelated to highway safety
- Error type: wrong area of law entirely

**Key insight:** The cases are real, but the attributed legal principles are wrong. This is harder to detect than a fabricated citation.

---

## SLIDE 9: Results - Layer 3: Reasoning Grounding

**85.7% of reasoning was ungrounded**

| Grounding Label | Count | % |
|---|---|---|
| Grounded (yes) | 3 | 3.1% |
| Partially grounded | 11 | 11.2% |
| Ungrounded (no) | 84 | 85.7% |

**What this means:**
- The system generates confident legal reasoning that reads like conventional judicial writing
- But in 85.7% of cases, the reasoning is not supported by the passages the system actually retrieved
- The system appears to be constructing plausible-sounding reasoning rather than reasoning from its sources

[FIGURE: Include annotation analysis figures]

---

## SLIDE 10: Automated Verifier Validation

**Built a 957-line Python verifier** screening all three layers:
- Layer 1: Deterministic corpus registry lookup
- Layer 2: TF-IDF cosine similarity against source text
- Layer 3: Passage similarity against retrieved chunks

**Validation results (Cohen's Kappa):**

| Layer | Accuracy | Kappa | Interpretation |
|---|---|---|---|
| Citation status | 87.8% | 0.80 | Substantial agreement - automation works |
| Holding accuracy | 4.1% | 0.04 | Near-zero - automation fails |
| Reasoning grounding | 85.7% | 0.24 | Fair - dominated by majority class |

**Key finding:** Citation existence is automatable. Holding accuracy requires human legal expertise. There is no shortcut.

---

## SLIDE 11: Discussion - The Key Finding

**The system does not invent cases. That makes it more dangerous, not less.**

- Zero fabrications out of 33 case-law authorities
- A citation existence check would give it a clean bill of health
- But 50% of holdings are wrong and 85.7% of reasoning is ungrounded

**Why this matters:**
- The output looks credible: real cases, confident language, conventional legal writing
- A reader may accept a proposition without noticing the cited authority does not support it
- Checking that a case exists is necessary but **not sufficient** for legal-AI reliability

**Practical safeguards recommended:**
1. Explicit passage-level attribution for every legal proposition
2. Abstention when authoritative text is unavailable
3. Retrieval provenance logging for post-hoc audit
4. Continued human oversight for holding accuracy

---

## SLIDE 12: Conclusions and Future Work

**Conclusions:**
- Hercules cites only real cases but misrepresents their holdings in 50% of attributions
- 85.7% of reasoning is not grounded in retrieved passages
- Automated verification works for citation existence (kappa = 0.80) but fails for semantic accuracy (kappa = 0.04)
- Citation existence alone is an inadequate measure of legal-AI reliability

**Limitations:**
- 59-judgment convenience sample from a single system configuration
- Phase 4 controlled experiments not conducted
- R2 pass was AI-assisted, not an independent human annotator

**Future work:**
1. Controlled experiments varying retrieval depth, prompt design, and model choice
2. Embedding-based or LLM-as-judge approaches for automated holding verification
3. Larger, multi-domain sample for generalisability
4. Independent second human annotator for grounding labels

---

## SLIDE 13: Questions?

**Questions?**

Roopa Raj
B00871016
Raj-R@ulster.ac.uk

---

## BACKUP SLIDE: Three-Layer Framework Diagram

```
Input: Skeleton Arguments (PDF/XML)
         |
         v
  Hercules (GPT-4o-mini + Qdrant RAG)
         |
         v
  Draft Judgment with Citations
         |
    +---------+---------+
    |         |         |
    v         v         v
 Layer 1   Layer 2   Layer 3
 Citation  Holding   Reasoning
 Provenance Accuracy Grounding
    |         |         |
    v         v         v
 Automated  Human     Human
 Verifier   Annotation Annotation
 k=0.80    k=0.04    k=0.24
```

## BACKUP SLIDE: Dataset Summary

| Metric | Value |
|---|---|
| Draft judgments | 59 |
| Citation occurrences | 115 |
| Validation sample | 98 occurrences from 50 judgments |
| Real-input judgments | 34 |
| Synthetic-input judgments | 25 |
| Corpus registry | 3,654 cases, 29,232 chunks |
| Structured records | 2,541 in Neon/PostgreSQL |
| Data frozen | 31 August 2026 |