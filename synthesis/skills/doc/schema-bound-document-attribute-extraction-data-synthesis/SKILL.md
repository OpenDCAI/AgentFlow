---
name: schema-bound-document-attribute-extraction-data-synthesis
description: Use this skill when the user wants structured labels or fields extracted from messy document text. Trigger it for requests like "label the sentence under this schema," "pull the key attributes from the note," "classify the document with strict categories," or "extract fields only when the evidence truly matches the guideline." It is appropriate for clinical notes, legal clauses, financial agreements, contracts, and any document workflow that converts prose into a controlled schema.
---

# Skill: Schema-bound document attribute extraction

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to read unstructured documents and map their contents onto a predefined schema, label space, or attribute inventory, preserving the document-grounded evidence for each extracted field. The challenge is not just spotting keywords, but determining whether the source text genuinely expresses the target label, attribute, severity, or class under a consistent annotation policy.
* **Dimension Hierarchy**: Document Validation & Structuring->Extraction->Schema-bound document attribute extraction

### Real Case
**[Case 1]**
* **Initial Environment**: A clinical note sentence is reviewed under a schema of social-determinants-of-health categories and adverse-status definitions.
* **Real Question**: "Classify the sentence under the SDoH schema: Pt missed appointment because her sister couldn't drive her today."
* **Real Answer**: Transportation issue; adverse SDoH mention.
* **Why this demonstrates the capability**: The sentence does not merely mention travel in the abstract; it indicates a transportation barrier that affects care access. The correct output therefore depends on applying the schema, not on broad semantic similarity alone. This is a classic example of schema-bound sentence labeling grounded in document evidence.

---
**[Case 2]**
* **Initial Environment**: A clinical note sentence is classified under the same schema, but this time the mention is relational and non-adverse.
* **Real Question**: "Classify the sentence under the SDoH schema: Pt and her husband came into my office today."
* **Real Answer**: Relationship mention; not adverse.
* **Why this demonstrates the capability**: The sentence contains evidence for the relationship category, but it does not indicate a support need or adverse condition. The task therefore tests whether the agent can separate category detection from severity or adverse-status detection. That separation is central to reliable structured extraction.

---
**[Case 3]**
* **Initial Environment**: A financial or legal document is processed under a fixed task schema such as named-entity recognition, key-information extraction, or categorical classification.
* **Real Question**: "Extract the target field or label only if the document evidence satisfies the schema definition."
* **Why this demonstrates the capability**: This class of benchmark evaluates whether the model can obey annotation guidelines and output normalized fields rather than loose free-form descriptions. The important capability is consistency of evidence-to-label mapping across many documents. That makes it directly relevant to document agents that annotate, review, or populate structured forms.

## Pipeline Execution Instructions
To synthesize data for this capability, you must strictly follow a 3-phase pipeline. **Do not hallucinate steps.** Read the corresponding reference file for each phase sequentially:

1. **Phase 1: Environment Exploration**
   Read the exploration guidelines to discover raw knowledge seeds:
   `references/EXPLORATION.md`

2. **Phase 2: Trajectory Selection**
   Once Phase 1 is complete, read the selection criteria to evaluate the trajectory:
   `references/SELECTION.md`

3. **Phase 3: Data Synthesis**
   Once a trajectory passes Phase 2, read the synthesis instructions to generate the final data:
   `references/SYNTHESIS.md`
