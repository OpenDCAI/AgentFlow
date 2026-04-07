---
name: open-domain-data-discovery-and-table-selection-data-synthesis
description: Use this skill when the user wants questions that make the agent first figure out *which table matters* before doing the math. Trigger it for requests such as “make it search the right sheet first,” “make it find the relevant table from a pile of files,” “make the question depend on the correct spreadsheet,” or “make it choose the right data source before answering.” Also trigger it when the task should feel like open-domain analytics over many tables, not direct computation over a table that is already handed to the agent. Plain-language examples: “Ask something where the answer is hidden in one of many datasets,” “make it pick the right table by itself,” “make it search through messy tabular data first.”
---

# Skill: Open-Domain Data Discovery And Table Selection

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to infer which table or small set of tables is relevant when the user asks an analytical question but does not provide the evidence table explicitly. It requires semantic matching between the question and candidate tables, robust use of metadata, and disciplined narrowing from a broad corpus to a minimal evidence set before analysis begins.
* **Dimension Hierarchy**: Data Grounding->Data Retrieval & Semantic Grounding->open-domain data discovery and table selection

### Real Case
**[Case 1]**
* **Initial Environment**: A corpus of tabular data and metadata is available, but no evidence table is pre-specified. The agent must work in an open-domain setting where the relevant table must be retrieved before answering.
* **Real Question**: What is the highest eligible free rate for K-12 students in the schools in Alameda County?
* **Real Trajectory**: Interpret the entities in the question; retrieve candidate education-related tables; re-rank tables by county and school-program relevance; inspect the top tables; isolate the row subset for Alameda County K-12 schools; extract the highest eligible free rate.
* **Why this demonstrates the capability**: The hard part is not the aggregation itself but discovering which table contains the needed statistic. The question therefore tests semantic alignment between the analytical request and a large structured corpus. A correct solution proves that the agent can move from a natural-language request to the right evidence table before any downstream reasoning.

---
**[Case 2]**
* **Initial Environment**: A large legal-discovery-style data lake contains many files, including agency descriptions, transaction records, and fraud-related tables. The answer cannot be produced unless the agent first discovers the correct files and joins them conceptually.
* **Real Question**: According to the Consumer Sentinel Network, what is the total amount of money defrauded in 2024, summing over all payment methods? Give an integer in millions of dollars.
* **Real Trajectory**: Search the data lake for Consumer Sentinel Network artifacts; identify files that record 2024 fraud losses and payment methods; extract or normalize the monetary field; sum over all payment methods; convert the result to integer millions; report the final number.
* **Real Answer**: 5435 million
* **Why this demonstrates the capability**: This task demonstrates that retrieval is part of the analysis pipeline itself. The agent must first discover which files are authoritative and which are merely contextual. Only then can it aggregate the correct values, so success directly reflects open-domain table and file selection ability.

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
