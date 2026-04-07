---
name: multi-document-integrative-reasoning-qa-data-synthesis
description: Use this skill when the user wants questions that require connecting information across several files or several far-apart sections of a long workspace. Trigger it for requests like "make it require combining documents," "ask something that needs comparing several reports," "force the agent to connect the dots," or "the answer should depend on multiple sources, not one page." It is the right skill for benchmark-style document bundles, deep-research corpora, meeting materials, legal case collections, or paper sets where skipping one document should break the answer.
---

# Skill: Multi-document integrative reasoning QA

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to answer a question whose evidence is intentionally dispersed across multiple documents, requiring the agent to collect, reconcile, compare, group, and reason over separate pieces before producing a final answer. The core challenge is that no single document is sufficient, so the agent must leave no relevant document behind and must preserve cross-document dependencies throughout reasoning.
* **Dimension Hierarchy**: Document Grounding & Reasoning->Evidence Use->Multi-document integrative reasoning QA

### Real Case
**[Case 1]**
* **Initial Environment**: A long bundle of company filings is provided, and the relevant non-current-assets values are scattered across different company reports rather than centralized in one summary page.
* **Real Question**: "Which company has the highest non-current assets?"
* **Real Answer**: "HARTE HANKS"
* **Why this demonstrates the capability**: The agent must inspect several documents, normalize the target field, and compare the resulting values before answering. Any shortcut that reads only one report is invalid because the task is inherently comparative. This is a direct test of cross-document aggregation plus decision making.

---
**[Case 2]**
* **Initial Environment**: Multiple company reports contain accounts-payable fields, and the answer requires grouping entities rather than returning one extracted span.
* **Real Question**: "Categorize the companies above by 'Accounts Payable' into the following groups: high payable (x>100,000), medium payable (1,000<x<100,000), and low payable (x<1,000)."
* **Real Answer**: {"high payable": ["BIOETHICS"], "medium payable": ["CLEARONE"], "low payable": ["Dominari Holdings"]}
* **Why this demonstrates the capability**: The task combines extraction with grouping, so the agent must gather values from multiple documents and then apply a criterion consistently. The output is not a copied sentence but an integrated structured judgment over several sources. That makes it a strong example of multi-document clustering and synthesis.

---
**[Case 3]**
* **Initial Environment**: A sequence of yearly reports for the same company is mixed into a larger long context, with one relevant value per year appearing in different document regions.
* **Real Question**: "What is the trend in ARVANA INC's cash flow over the years 2022, 2023, and 2024?"
* **Real Answer**: "The cash flow in ARVANA INC increased from $3,340 in 2022 to $139,025 in 2023, but then significantly decreased to $(120,294) in 2024)."
* **Why this demonstrates the capability**: The model must first align values to the correct years and only then infer the temporal pattern. A one-document or one-value shortcut cannot solve the task because the answer is a relation across years, not an isolated fact. This demonstrates chain-style reasoning across multiple documents.

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
