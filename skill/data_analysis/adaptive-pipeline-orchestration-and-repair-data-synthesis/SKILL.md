---
name: adaptive-pipeline-orchestration-and-repair-data-synthesis
description: Use this skill when the user wants the agent to behave like a persistent analyst that plans, checks, and fixes its own pipeline. Trigger it for requests such as “make it reason in steps and recover from mistakes,” “make it plan and repair,” “make it debug the analysis path,” or “give me a task where the first attempt is usually not enough.” Plain-language examples: “Ask something that needs several rounds of trying,” “make it notice errors and fix them,” “make it orchestrate the full pipeline end to end.”
---

# Skill: Adaptive Pipeline Orchestration And Repair

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to plan a multi-step analytical workflow, execute it iteratively, detect failures or insufficiencies, and revise the plan or code until a coherent end-to-end result is produced. It centers on workflow management, decomposition, self-correction, and recovery rather than any single analytical primitive.
* **Dimension Hierarchy**: Agentic Execution & Communication->Workflow Control->adaptive pipeline orchestration and repair

### Real Case
**[Case 1]**
* **Initial Environment**: A heterogeneous data lake contains many raw files, and the agent must design and execute an end-to-end pipeline that discovers relevant data, cleans it, and computes the final answer. The task is evaluated in a no-human-in-the-loop setting.
* **Real Question**: According to the Consumer Sentinel Network, what is the total amount of money defrauded in 2024, summing over all payment methods? Give an integer in millions of dollars.
* **Real Trajectory**: Search the data lake for relevant files; draft an initial pipeline that extracts fraud-loss records; run the code and inspect intermediate results; revise file choices or column mappings if the totals are inconsistent; normalize values and units; compute the final total; output the answer.
* **Real Answer**: 5435 million
* **Why this demonstrates the capability**: The example requires more than isolated analytics because the agent must orchestrate discovery, extraction, cleaning, and aggregation as one coherent workflow. It also benefits from iterative repair if the first file or column choice is wrong. That makes it an archetypal pipeline-orchestration task.

---
**[Case 2]**
* **Initial Environment**: An empty Jupyter notebook, heterogeneous biological data files, and a prebuilt execution environment are provided. The agent has free reign to inspect the workspace, edit notebook cells, rerun analysis, and submit answers.
* **Real Question**: What percentage of genes differentially expressed in strain 97 are also differentially expressed in strain 99?
* **Real Trajectory**: List the workspace; load the candidate files into the notebook; attempt the overlap analysis; inspect outputs or tracebacks; revise the notebook code if the wrong files or thresholds were used; rerun the cells; submit the final percentage.
* **Why this demonstrates the capability**: The capability here is the agent’s ability to manage and repair a live analysis process rather than to perform one static computation. The notebook environment creates natural opportunities for iterative planning, execution, observation, and correction. That is exactly what adaptive orchestration means in a data-analysis sandbox.

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
