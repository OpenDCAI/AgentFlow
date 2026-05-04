---
name: data sufficiency evaluation and unanswerability detection
description: Use this skill when the user wants tasks that test if the agent can refuse to answer when the data is missing or structurally inadequate. Trigger it for requests like "make it recognize when data is missing," "ask a trick question that cannot be solved with the given tables," or "make the agent say 'insufficient data' instead of guessing." Plain-language examples: "Ask something that the spreadsheet doesn't actually have," "make it catch unanswerable questions," "test if it will hallucinate or correctly give up."
---

# Skill: data sufficiency evaluation and unanswerability detection

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability involves the systematic evaluation of data environments to determine if they contain the necessary variables, cohorts, and granularity to support a specific analytical request. It emphasizes non-verifiability detection, where the agent must critically identify structural data absences and confidently declare the task unanswerable, thereby avoiding hallucinations or proxy-based guessing.
* **Dimension Hierarchy**: Data Grounding->Data Retrieval & Semantic Grounding->data sufficiency evaluation and unanswerability detection

### Real Case
**[Case 1]**
* **Initial Environment**: A data sandbox contains clinical archives for cancer patients but lacks mutational burden records or labels mapping the exact locations of distant metastases.
* **Real Question**: Do patients with brain metastases have a significantly higher mutational burden compared to those with non-brain metastases?
* **Real Trajectory**: Inspect the clinical tables for columns related to 'brain_metastasis' or 'mutational_burden'; identify that while the patient cohort exists, there is no column defining the location of metastases or the mutational burden metric; instead of attempting a guess, state that the dataset is missing the critical grouping and outcome variables; conclude the request is unanswerable.
* **Real Answer**: Unanswerable. The dataset lacks mutational burden records and brain metastasis location labels.
* **Why this demonstrates the capability**: The agent avoids the common error of misidentifying nearest-neighbor columns or hallucinating a result, correctly identifying that the specific comparative evidence required for the analytical request is physically absent from the environment.
---
**[Case 2]**
* **Initial Environment**: An e-commerce dataset containing product names, categories, and review scores, but entirely missing any sales volume, quantity, or revenue metrics.
* **Real Question**: Which product category generated the highest total revenue in Q3 2023?
* **Real Trajectory**: Start searching for revenue, sales, or price/quantity columns; read the headers and schemas of all available tables; observe that only review and product metadata information is present; halt the analysis and declare that revenue cannot be calculated without sales volume or unit price data.
* **Real Answer**: Unanswerable due to missing revenue and sales data.
* **Why this demonstrates the capability**: The question explicitly asks for a metric that requires data structurally unavailable in the table. The agent must successfully evaluate the schema and recognize the insufficiency before confidently refusing to compute a number, directly testing capability of unanswerability detection.

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
