# Hercules Holding-Accuracy and Reasoning-Grounding Codebook

Version: 1.1  
Project: Auditing AI-Generated Draft Judgments: Citation Provenance, Holding Accuracy, and Reasoning Grounding  
Module: COM748 Masters Research Project  
Student: Roopa Raj (B00871016)

## 1. Purpose

This codebook defines the manual annotation procedure for evaluating two risks in Hercules-generated draft judgments:

1. **Holding accuracy:** whether the legal rule, holding, or principle attributed to an authority is an accurate representation of that authority.
2. **Reasoning grounding:** whether the generated application or reasoning is supported by the passages and cases retrieved for that judgment.

The citation-existence and citation-format review is recorded separately in `unique_citation_review.xlsx`. This codebook does not replace that review.

## 2. Evaluation units

### 2.1 Primary unit

The primary annotation unit is one **citation occurrence** within one generated judgment. If the same authority appears in multiple judgments, each occurrence is assessed separately because the attributed principle and application may differ.

### 2.2 Secondary unit

Citation-level labels are aggregated to produce one result for each generated judgment.

### 2.3 Human-validation sample

To follow the proposal, select approximately 50 generated judgments and label every citation occurrence within those judgments. Use a reproducible, stratified sample containing both real and synthetic inputs.

Recommended random seed: `748`.

If fewer than 50 judgments are independently assessed by two reviewers, record the actual number and explain the deviation in the paper.

## 3. Evidence sources

Use evidence in the following order:

1. An official judgment source, such as the UK Supreme Court, Judicial Committee of the Privy Council, National Archives, legislation.gov.uk, or another official court source.
2. BAILII or another reliable full-text judgment database.
3. The corresponding full judgment or case chunks in the frozen Hercules/Qdrant corpus.
4. The retrieved passages stored in the linked `semantic_searches` record.

Do not decide holding accuracy from a case summary, search-result snippet, generated description, or case title alone.

For grounding, examine only the retrieval event linked to the generated judgment. The existence of relevant material elsewhere in the corpus does not mean Hercules retrieved it for that judgment.

## 4. Holding-accuracy labels

Record the label in the `holding_accuracy` field.

| Label | Definition | Decision rule |
|---|---|---|
| `yes` | The generated principle is materially faithful to the authority. | The wording may be paraphrased, but the legal meaning, scope, conditions and procedural context are preserved. |
| `partial` | The authority provides some support, but the generated principle is incomplete, overstated, decontextualised or imprecise. | Use when a correct general idea is present but an important limitation, test, jurisdictional condition, procedural context, or distinction between ratio and obiter is omitted. |
| `no` | The generated principle is unsupported, contradicted or attributed to the wrong authority. | Use when the authority concerns a different doctrine, reaches the opposite position, or does not establish the proposition attributed to it. |
| `unclear` | The evidence is insufficient to make a reliable decision. | Use only when the authoritative judgment cannot be obtained, the generated proposition is too vague, or the source text is incomplete. Explain why. |
| `n/a` | Holding accuracy is not applicable. | Use for a procedural rule, statutory provision or other non-case reference when no case holding is being attributed. The reference may still require a grounding assessment. |

### 4.1 Holding-accuracy examples

- `yes`: The draft states that *English v Emery Reimbold & Strick Ltd* requires judges to provide adequate reasons, and the source judgment supports that proposition.
- `partial`: The draft cites *Armitage v Nurse* as establishing a general duty of prudence but omits that the principal issue concerned trustee exemption clauses.
- `no`: The draft attributes a public-safety principle concerning cyclists to a clinical-negligence judgment.
- `unclear`: Only a citation is available and the full judgment cannot be located.

### 4.2 Ratio and obiter

An obiter observation is not automatically inaccurate. Label it `partial` if Hercules presents a materially relevant observation as a binding holding without qualification. Label it `no` if the supposed rule cannot reasonably be supported by the judgment.

## 5. Reasoning-grounding labels

Record the label in the `reasoning_grounding` field.

| Label | Definition | Decision rule |
|---|---|---|
| `yes` | The linked retrieval provides clear support for the generated application or reasoning. | At least one retrieved passage supplies the factual or legal premise used, and the inference does not materially exceed the evidence. |
| `partial` | The retrieval supports part of the reasoning, but Hercules adds an unsupported step, condition or conclusion. | Use when the retrieved material is relevant but insufficient for the full proposition or application. |
| `no` | The reasoning is not supported by the linked retrieval or is contradicted by it. | Use when the relied-upon authority was not retrieved, the relevant proposition is absent, the retrieved case is unrelated, or the generated reasoning contradicts the passage. |
| `unclear` | The linked retrieval evidence is missing, truncated or too ambiguous to assess. | Explain which retrieval data are unavailable. Do not convert missing evidence into `no` automatically. |
| `n/a` | No substantive application or reasoning claim is attached to the occurrence. | Use sparingly and explain why no grounding assessment was possible or required. |

### 5.1 Important distinction

These are different questions:

- **Corpus presence:** Is the authority somewhere in Qdrant?
- **Retrieval:** Was it retrieved for this generated judgment?
- **Holding accuracy:** Did Hercules describe the authority correctly?
- **Reasoning grounding:** Did the retrieved material support the way Hercules applied the proposition?

An authority may exist in the corpus and be correctly described but still receive `reasoning_grounding = no` if it was not retrieved for that judgment.

## 6. Annotation procedure

For every citation occurrence:

1. Record the `draft_id`, `case_doc_id`, `input_type`, `citation_index` and citation text.
2. Copy the generated `principle` and `application` fields without rewriting them.
3. Identify the authoritative source and record its citation, URL or corpus case ID.
4. Read the relevant paragraphs in the authoritative judgment.
5. Assign `holding_accuracy` using Section 4.
6. Record a short evidence note and paragraph or section reference. Paraphrase where possible; do not copy long passages.
7. Locate the `semantic_searches` event linked to the judgment through `retrieval_linkage_59.csv`.
8. Inspect the retrieved case IDs, titles, matching chunks and passages.
9. Assign `reasoning_grounding` using Section 5.
10. Record the supporting or conflicting retrieval evidence.
11. Record reviewer confidence on a scale of `1` (very low) to `5` (very high).
12. Do not revise a label merely to make the aggregate results look more consistent.

## 7. Required annotation fields

The annotation table should contain the following columns:

| Field | Description |
|---|---|
| `draft_id` | Unique generated-judgment identifier. |
| `case_doc_id` | Hercules input document identifier. |
| `input_type` | `real` or `synthetic`, based on the frozen manual classification. |
| `citation_index` | Citation order within the judgment. |
| `citation` | Citation text extracted from the generated judgment. |
| `generated_principle` | Principle attributed to the authority by Hercules. |
| `generated_application` | Hercules's application of the principle. |
| `authoritative_source` | Official source URL, citation or corpus identifier. |
| `source_paragraphs` | Paragraphs or sections used to verify the holding. |
| `holding_accuracy` | `yes`, `partial`, `no`, `unclear` or `n/a`. |
| `holding_evidence` | Concise explanation supporting the label. |
| `search_id` | Linked semantic-search identifier. |
| `retrieved_case_ids` | Case IDs actually returned in the linked search. |
| `retrieved_evidence` | Relevant retrieved passage or concise paraphrase. |
| `reasoning_grounding` | `yes`, `partial`, `no`, `unclear` or `n/a`. |
| `grounding_evidence` | Concise explanation supporting the grounding label. |
| `reviewer_id` | Anonymous reviewer code, for example `R1` or `R2`. |
| `reviewer_confidence` | Integer from `1` (very low) to `5` (very high). |
| `review_timestamp` | Date and time of the assessment. |
| `adjudication_notes` | Resolution of any disagreement between reviewers. |

## 8. Judgment-level aggregation

Calculate two forms of failure rate so that borderline cases are transparent.

### 8.1 Confirmed holding failure

A judgment has a confirmed holding failure if at least one citation occurrence has:

`holding_accuracy = no`

### 8.2 Strict holding defect

A judgment has a strict holding defect if at least one citation occurrence has:

`holding_accuracy in {partial, no}`

### 8.3 Confirmed grounding failure

A judgment has a confirmed grounding failure if at least one substantive occurrence has:

`reasoning_grounding = no`

### 8.4 Strict grounding defect

A judgment has a strict grounding defect if at least one substantive occurrence has:

`reasoning_grounding in {partial, no}`

Report `unclear` results separately. Do not silently count them as success or failure.

## 9. Inter-rater validation and Cohen's Kappa

1. Two reviewers must independently label the same validation sample without seeing each other's labels.
2. Use the same evidence package and this codebook.
3. Calculate raw percentage agreement and Cohen's Kappa separately for:
   - `holding_accuracy`
   - `reasoning_grounding`
4. Exclude `n/a` only when both reviewers marked the item `n/a`. Treat other disagreements normally.
5. Calculate Kappa on the original categories rather than converting all labels to binary labels after reviewing.
6. Discuss disagreements and produce an adjudicated final label in a separate column. Never overwrite either reviewer's original label.

Suggested interpretation, used cautiously:

| Kappa | Description |
|---:|---|
| `< 0.00` | Less than chance agreement |
| `0.00-0.20` | Slight agreement |
| `0.21-0.40` | Fair agreement |
| `0.41-0.60` | Moderate agreement |
| `0.61-0.80` | Substantial agreement |
| `0.81-1.00` | Near-perfect agreement |

Always report the sample size, category frequencies and raw agreement alongside Kappa. A high Kappa is not proof that the underlying legal classifications are correct.

If a second independent reviewer is unavailable, do not report Cohen's Kappa. Report the work as a single-reviewer manual audit and identify the absence of inter-rater validation as a limitation.

## 10. Quality-control rules

- Complete a pilot of at least five judgments before the full annotation run.
- Revisit the codebook only if the pilot exposes a genuine ambiguity.
- Record every codebook change with a new version number and explanation.
- Do not modify labels after viewing real-versus-synthetic aggregate results unless correcting a documented error.
- Keep the raw reviewer sheets unchanged after adjudication.
- Preserve the frozen draft, retrieval and corpus files used to make each decision.
- Record missing or malformed source IDs rather than silently substituting a different case.

## 11. Reporting language

Use precise language:

- Say **"not found as a standalone corpus record"**, not **"fabricated"**, when a real external authority is absent from the Qdrant registry.
- Say **"not retrieved for the linked generation"**, not **"not in Hercules"**, when an authority exists in the corpus but was absent from the linked retrieval.
- Say **"partially supported"** when the authority supports only part of a proposition.
- Reserve **"hallucinated holding"** for a proposition labelled `holding_accuracy = no` after authoritative verification.
- Reserve **"ungrounded reasoning"** for a reasoning occurrence labelled `reasoning_grounding = no` against the linked retrieval evidence.

## 12. Limitations to record

- Legal interpretation involves expert judgment, particularly when distinguishing a holding from obiter commentary.
- The study uses a convenience sample of Hercules outputs rather than a representative sample of all UK litigation.
- Several generated judgments arise from repeated generations or re-uploaded versions of related inputs.
- External legal sources and the Hercules corpus may use different case titles or citation variants.
- A retrieved source may support a proposition indirectly even when exact wording is absent.
- Citation-level labels do not by themselves establish whether the overall outcome of a draft judgment is legally correct.