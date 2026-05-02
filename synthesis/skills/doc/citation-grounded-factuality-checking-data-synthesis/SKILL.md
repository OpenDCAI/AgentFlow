---
name: citation-grounded-factuality-checking-data-synthesis
description: Use this skill when the user wants the agent to judge whether an answer is really backed by the document, not just whether it sounds correct. Trigger it for requests like "check if the citation really supports the claim," "make examples of sneaky hallucinations," "verify grounded answers sentence by sentence," or "test whether the model invents support from the source." It is ideal for legal research outputs, RAG answers, summaries, and any document-grounded generation setting where false support is as dangerous as an outright fabrication.
---

# Skill: Citation-grounded factuality checking

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to determine whether a generated statement or answer is actually supported by its grounding documents, cited passages, or linked authorities, and to distinguish true support from misgrounding, partial support, contradiction, or unsupported elaboration. The core difficulty is not merely detecting obvious falsehoods, but spotting subtle cases where a citation is real yet does not support the claim being made.
* **Dimension Hierarchy**: Document Validation & Structuring->Verification->Citation-grounded factuality checking

### Real Case
**[Case 1]**
* **Initial Environment**: A legal research system is asked a constitutional-law question and returns an answer with linked authorities that appear polished and professional.
* **Real Question**: "What standard of review applies to abortion regulations under the U.S. Constitution?"
* **Why this demonstrates the capability**: The cited authority can look legitimate while still failing to support the specific proposition claimed in the answer. That is precisely the misgrounded-citation failure mode this capability targets. The task therefore measures support verification, not mere fluency judgment.

---
**[Case 2]**
* **Initial Environment**: A legal research or grounded-generation system answers a doctrinal question and produces a confident rationale linked to source documents.
* **Real Question**: "Why did Justice Ginsburg dissent in Obergefell?"
* **Why this demonstrates the capability**: This kind of example is dangerous because the response may combine real legal terms, real authorities, and a polished explanation into a coherent but unsupported answer. A proper checker must verify every substantive claim against the cited or retrieved documents rather than trusting stylistic plausibility. This demonstrates sentence-level grounding validation under high stakes.

---
**[Case 3]**
* **Initial Environment**: A fact-checking benchmark pairs a grounding document or document chunk with a claim sentence and asks whether the claim is supported.
* **Real Question**: "Given the grounding document, determine whether the claim is supported or unsupported."
* **Real Answer**: A binary or graded support label such as supported, partially supported, contradictory, or unsupported.
* **Why this demonstrates the capability**: This is the primitive operation behind grounded QA, RAG verification, and summary faithfulness checking. The evaluator must attend to synthesis across sentences, missing conditions, and citation mismatch, not just keyword overlap. That makes it the correct building block for hallucination-resistant document agents.

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
