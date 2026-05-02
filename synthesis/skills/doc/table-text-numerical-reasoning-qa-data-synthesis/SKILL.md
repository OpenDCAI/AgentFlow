---
name: table-text-numerical-reasoning-qa-data-synthesis
description: Use this skill when the user wants the agent to do document-grounded math instead of plain extraction. Trigger it for requests like "make it read the table and calculate," "ask for a percentage or trend from the report," "force the model to use both the note text and the numbers," or "use financial or chart data, not just prose." This skill fits annual reports, earnings calls, scientific tables, slide charts, and any document where the hard part is binding numbers to the right labels and then reasoning correctly.
---

# Skill: Table-text numerical reasoning QA

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to answer quantitatively grounded questions by jointly reading prose, tables, and numerical fields in documents, then performing the arithmetic, normalization, or ratio reasoning implied by the question. The agent must keep numbers tied to the right entities, periods, and units while resisting the common failure mode of copying a plausible but wrong value.
* **Dimension Hierarchy**: Document Grounding & Reasoning->Evidence Use->Table-text numerical reasoning QA

### Real Case
**[Case 1]**
* **Initial Environment**: A public-company filing is open, with financial statements, note text, and page-specific evidence strings available for verification.
* **Real Question**: "What is Boeing’s FY2022 cost of goods sold (in USD millions)?"
* **Real Answer**: "$63,078 million"
* **Why this demonstrates the capability**: The question is numerically grounded and expects the model to recover the correct metric, year, and unit from the filing rather than answer from vague financial knowledge. It also exemplifies open-book QA where answerability depends on precise binding between the requested field and the evidence page. This is a canonical table-text numeric retrieval case.

---
**[Case 2]**
* **Initial Environment**: A quarterly-report slide collection contains product sales information in a visually rich layout that mixes tables, labels, and charted figures.
* **Real Question**: "What is the profit difference between the highest and lowest selling products in Apple's 2024 quarterly reports?"
* **Real Answer**: "$24.7 Billion"
* **Why this demonstrates the capability**: The answer is not present as a single copied number; it requires locating the relevant product values, identifying the extreme pair, and computing the difference. The document layout is multimodal, so simple OCR-like extraction is insufficient unless the agent also reasons over structure. This makes the case a strong test of visual-document numeric reasoning.

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
