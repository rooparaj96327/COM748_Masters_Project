# Supporting Material Report

**Project:** Auditing AI-Generated Draft Judgments: Citation Provenance, Holding Accuracy, and Reasoning Grounding  
**Student:** Roopa Raj (B00871016)  
**Supervisor:** Professor Jun Liu  
**Module:** COM748 Masters Research Project, Ulster University  
**Date:** September 2026

---

## 1. Extended Literature Review

The research paper surveys hallucination, legal AI evaluation, and RAG faithfulness within its page limit. This section extends the literature review to situate the project within broader research on trustworthy AI in high-stakes domains.

### 1.1 Hallucination Taxonomies

Huang et al. (2023) provide a comprehensive survey of hallucination in large language models, distinguishing between factuality hallucination (generating content contradicting established facts) and faithfulness hallucination (deviating from the provided context or instructions). This taxonomy directly informed the three-layer verifier design: Layer 1 targets factuality (do cited cases exist?), while Layers 2 and 3 target faithfulness (does the output align with source material?). Zhang et al. (2023) further categorise hallucination by granularity (sentence-level, passage-level, and document-level) and find that longer outputs exhibit compounding error rates. This observation is relevant to Hercules, which generates multi-page draft judgments where errors in early citations can propagate through subsequent reasoning.

### 1.2 Legal AI and Judgment Prediction

Legal judgment prediction has been studied extensively in computational law. Zhong et al. (2020) developed LEGAL-BERT for Chinese legal text, while Chalkidis et al. (2020) benchmarked transformer models on European Court of Human Rights case prediction. These systems predict outcomes rather than generating full judgments, making their evaluation simpler: a predicted outcome is either correct or incorrect. Hercules occupies a fundamentally different position: it generates extended prose that must be evaluated at multiple levels of granularity, from citation accuracy to reasoning coherence.

Dahl et al. (2024) evaluated GPT-4 on the Uniform Bar Examination and found it performed above the passing threshold, prompting interest in deploying LLMs for legal tasks. However, passing a multiple-choice examination does not establish reliability in generative tasks where the system must construct, not select, legal reasoning. Cui et al. (2023) developed ChatLaw, a Chinese legal AI system, and found that domain-specific fine-tuning reduced but did not eliminate hallucination in legal contexts.

### 1.3 RAG Evaluation and Attribution

Gao et al. (2024) survey the RAG landscape and identify a gap between retrieval quality and generation faithfulness: a system can retrieve relevant documents yet still produce unfaithful output. This gap is precisely what the Hercules audit quantifies: several misdescribed authorities were present in the corpus, confirming that retrieval success does not guarantee generation accuracy.

Bohnet et al. (2023) introduce Attributed Question Answering, where every generated claim must be traceable to a specific source passage. Rashkin et al. (2023) propose the Attributable to Identified Sources (AIS) framework, which evaluates whether each generated statement is supported by cited evidence. The three-layer verifier in this project implements a domain-specific version of AIS: Layer 1 checks source identification, Layer 2 checks claim accuracy, and Layer 3 checks evidential support. Min et al. (2023) further demonstrate that automatic faithfulness metrics correlate poorly with human judgments in complex domains, consistent with the finding that automated holding-accuracy verification achieved near-zero agreement with expert labels.

### 1.4 AI Regulation and Judicial Use

The EU AI Act (2024) classifies AI systems used in the administration of justice as high-risk, requiring conformity assessments, human oversight, and transparency obligations. The UK Judicial Office published guidance in December 2023 permitting judges to use AI tools for summarisation but warning against reliance on AI-generated legal research without independent verification. The UK AI Security Institute, which funded the Hercules project, has emphasised the need for structured evaluation of AI systems before deployment in public-sector contexts. These regulatory and institutional developments provide direct policy relevance for the audit methodology developed in this project.

### References (Supporting Material)

- Bohnet, B. et al. (2023). Attributed Question Answering. *EMNLP 2023*.
- Chalkidis, I. et al. (2020). LEGAL-BERT. *Findings of EMNLP 2020*.
- Cui, J. et al. (2023). ChatLaw: Open-Source Legal Large Language Model. *arXiv:2306.16092*.
- Dahl, M. et al. (2024). Large Legal Fictions: Profiling Legal Hallucinations in LLMs. *Journal of Legal Analysis*, 16(1).
- European Parliament (2024). Regulation (EU) 2024/1689 (AI Act).
- Gao, Y. et al. (2024). Retrieval-Augmented Generation for Large Language Models: A Survey. *arXiv:2312.10997*.
- Huang, L. et al. (2023). A Survey on Hallucination in LLMs. *arXiv:2311.05232*.
- Min, S. et al. (2023). FActScore: Fine-grained Atomic Evaluation of Factual Precision. *EMNLP 2023*.
- Rashkin, H. et al. (2023). Measuring Attribution in Natural Language Generation Models. *Computational Linguistics*, 49(4).
- UK Judicial Office (2023). AI: Judicial Guidance. December 2023.
- Zhang, Y. et al. (2023). Siren's Song in the AI Ocean: A Survey on Hallucination in LLMs. *arXiv:2309.01219*.
- Zhong, H. et al. (2020). How Does NLP Benefit Legal System? *ACL 2020*.

---

## 2. Project Lifecycle and Tools

### 2.1 Development Approach

The project followed an iterative, exploratory methodology rather than a strictly linear software-development lifecycle. Each phase produced intermediate outputs that were manually inspected before proceeding, allowing methodological decisions to be informed by emerging findings. For example, the discovery that BAILII's citation-finder tool returns false negatives prompted a revised verification protocol that combined party-name search with web-based fallback, a procedural change that emerged from Phase 2 and was documented in the annotation codebook.

### 2.2 Project Timeline

The project was conducted between May and September 2026, with the following approximate schedule:

- **May to June 2026**: Literature review, system access negotiation, data export from Hercules database.
- **June to July 2026**: Citation extraction pipeline development, retrieval linkage, corpus registry analysis.
- **July 2026**: BAILII verification of all 35 authority groups, annotation codebook development, pilot annotation.
- **July to August 2026**: Full dual-reviewer annotation of 98 validation-sample occurrences, adjudication.
- **August 2026**: Verifier development, validation metrics computation, figure generation, paper writing.

The original proposal included controlled experiments (Phase 4) varying retrieval depth, prompt design, and model choice. These were dropped in August 2026 due to time constraints and limited API access; the scope was revised to focus on auditing the frozen corpus. This decision is discussed further in Section 4.

### 2.3 Tools and Technologies

| Tool | Purpose |
|---|---|
| Python 3.14 | Primary analysis language for all pipeline scripts |
| openpyxl | Reading and writing Excel annotation workbooks |
| matplotlib, numpy, scipy | Figure generation and statistical analysis |
| Qdrant | Vector database used by Hercules for case retrieval |
| Neon/PostgreSQL | Relational database storing Hercules case metadata |
| OpenAI API (GPT-4o-mini) | Used by Hercules for generation; used in this project only for annotation prefill |
| BAILII | Authoritative external source for manual citation verification |
| Regular expressions | Citation extraction from unstructured judgment text |
| TF-IDF cosine similarity | Core similarity metric in the automated verifier |
| Cohen's Kappa | Inter-rater and verifier-vs-human agreement measurement |
| Git | Version control throughout the project |
| SHA-256 checksums | Data integrity verification for the frozen dataset |

### 2.4 Data Management and Reproducibility

All source data was frozen on 31 August 2026, with SHA-256 checksums recorded in `project_inventory.csv`. A baseline manifest documents the frozen scope, methodological boundaries, and the rationale for the scope revision. The full analysis pipeline is reproducible from the frozen data using 11 scripts executed in sequence, as documented in `reproduction-guide.md`. Manual intervention points (BAILII verification and human annotation) are clearly identified in the reproduction instructions.

---

## 3. Professional, Ethical, Social, and Sustainability Issues

### 3.1 Ethical Considerations

AI systems that generate draft judgments operate in a domain where errors have direct consequences for individuals' rights and liberties. A misrepresented holding could lead a decision-maker to apply the wrong legal principle, with real consequences for the parties involved. The ethical imperative is therefore not merely to measure accuracy but to ensure that any deployment includes safeguards against over-reliance.

This project did not involve human participants in the research-ethics sense: the data analysed consists of system-generated draft judgments, not personal data. However, the skeleton arguments used as inputs to Hercules include real case names and party names from publicly available court records. These were handled in accordance with the principle that publicly available legal documents do not require anonymisation, consistent with the open-justice principle that underpins BAILII and other legal databases.

The Cambridge Law Corpus, referenced as a comparison dataset, was published under a research licence with restrictions on redistribution. This project did not use the corpus directly but cited it as contextual background for the Hercules knowledge base.

### 3.2 Professional Standards

The project was conducted in alignment with the BCS Code of Conduct and the ACM Code of Ethics, particularly the principles of honesty in reporting results, respect for confidentiality, and commitment to public interest. The AI Tools Statement in the research paper explicitly discloses that generative AI was used for language editing and restructuring during manuscript preparation, while all data analysis, statistical decisions, and experimental design were produced by the author. This disclosure follows the IEEE policy on AI-assisted writing.

The verifier was deliberately designed to return `unclear` rather than guess at holding accuracy without authoritative source text. This reflects a professional commitment to honest reporting: a screening tool that claims confidence it does not possess is more dangerous than one that acknowledges its limitations.

### 3.3 Social Implications

Public trust in the justice system depends on the perception and reality that judicial decisions are reasoned, evidence-based, and fair. If AI-generated drafts are adopted without adequate verification, there is a risk that errors, particularly the kind identified in this study, where real cases are cited for false principles, could undermine confidence in judicial reasoning. The finding that 50% of holdings were partially or fully inaccurate underscores the gap between current system capabilities and the standard required for judicial use.

Access to justice is a further consideration. Proponents of legal AI argue that it could reduce costs and increase access to legal services. However, if such systems produce unreliable outputs, they risk creating a two-tier system where well-resourced parties verify AI outputs while others rely on them uncritically. The audit methodology developed in this project provides a template for the kind of structured evaluation that should precede any deployment.

### 3.4 Sustainability

The environmental cost of large language model inference is a recognised concern. Each Hercules draft judgment requires multiple API calls to GPT-4o-mini for retrieval, chunking, and generation. The annotation prefill step in this project also used GPT-4o-mini. While the per-query cost is modest, scaled deployment for judicial use would involve substantial cumulative computation. The project did not measure energy consumption directly, but acknowledges that any deployment decision should weigh the environmental cost of continuous LLM inference against the administrative savings achieved.

---

## 4. Critical Appraisal

### 4.1 Scope Change

The most significant deviation from the original proposal was the decision to drop Phase 4 (controlled experiments). The proposal envisaged varying retrieval depth, prompt design, and model choice to isolate which factors most affect output quality. In practice, limited API access and the time required for manual annotation made these experiments infeasible within the project timeline. The scope was revised to focus on auditing the frozen Hercules output corpus.

This was the right decision. The audit of the existing system yielded substantive findings (the holding-accuracy and grounding-gap results) that would not have been possible if time had been divided between annotation and experimentation. However, the absence of controlled experiments means the study cannot identify which system component is most responsible for the failures observed. This is the primary limitation discussed in the paper.

### 4.2 What Worked Well

The three-layer verification framework proved effective as an organising structure. By separating citation existence, holding accuracy, and reasoning grounding, each failure mode could be measured independently and the results converged on a consistent picture. The framework is also generalisable: it could be applied to any RAG system that produces citation-bearing text.

The dual-reviewer annotation protocol with adjudication produced reliable ground-truth labels. Having two independent reviewers exposed genuine disagreements, particularly on the boundary between "partial" and "no" for reasoning grounding, that a single reviewer would have resolved silently. The adjudication step produced defensible final labels while preserving the original disagreements for analysis.

The automated verifier's honest abstention (returning `unclear` for holding accuracy without source text) turned out to be one of the project's strongest findings. It demonstrated, concretely, that certain dimensions of legal-AI evaluation resist automation.

### 4.3 What Did Not Work

The automated holding-accuracy verifier achieved near-zero agreement with human labels ($\kappa = 0.04$ without source text; $\kappa = 0.002$ with partial source text in v3). TF-IDF cosine similarity is fundamentally unsuitable for assessing whether a legal principle has been correctly attributed, because legal interpretation depends on semantic nuance that bag-of-words methods cannot capture. A future approach might use embedding-based similarity or an LLM-as-judge framework, though both introduce their own reliability concerns.

The corpus registry coverage was limited. Of 33 distinct case-law authorities, only 7 were both present in the corpus and retrieved for the relevant judgment. This constrained the holding-accuracy analysis: for most citations, there was no authoritative text within the system to compare against, making the evaluation dependent on external BAILII verification.

### 4.4 What I Would Do Differently

With more time, three changes would strengthen the project:

1. **Run the controlled experiments.** Varying retrieval depth (top-5 vs top-20 chunks) and model choice (GPT-4o vs GPT-4o-mini) would isolate whether the failures are retrieval-driven or generation-driven.
2. **Compute inter-rater agreement before adjudication.** Cohen's Kappa between R1 and R2 should have been computed and reported as a measure of annotation reliability, independent of the verifier validation.
3. **Use a larger and more diverse sample.** The 59-judgment dataset is a convenience sample from a single system configuration. A larger sample, including judgments from different legal domains, would improve generalisability.

### 4.5 Lessons Learned

The most important lesson was that surface-level metrics are misleading in high-stakes domains. A system that cites only real cases and achieves plausible-sounding reasoning can appear reliable by conventional measures while being substantively wrong in half its attributions. This reinforces the need for multi-layered evaluation that goes beyond existence checks to assess semantic accuracy.

A second lesson was the value of freezing the dataset early. By committing to a fixed corpus on 31 August 2026 and recording SHA-256 checksums, the analysis became fully reproducible and the temptation to re-run the system for better results was removed.

---

*Word count: approximately 2,400 words*
