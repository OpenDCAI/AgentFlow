---
name: analytic-dataset-construction-data-synthesis
description: Use this skill when the user wants the agent to *set up the right analysis table* before doing any statistics. Trigger it for requests such as “make it build the dataset first,” “make it pick variables, weights, and filters,” “make it define the right cohort,” or “make the real work be dataset setup.” Plain-language examples: “Ask something where the agent must prepare the analysis frame,” “make it decide who is in scope,” “make it choose the right columns and units before computing.”
---

# Skill: Analytic Dataset Construction

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to build the correct analysis-ready dataset from raw sources by selecting variables, defining the population, applying weights or filters, and deriving the exact table needed for downstream analysis. It is broader than one-off cleaning and focuses on constructing the right analytic view of the data.
* **Dimension Hierarchy**: Analytical Transformation->Data Preparation->analytic dataset construction

### Real Case
**[Case 1]**
* **Initial Environment**: Large survey data files are accompanied by codebooks, survey-design documents, and expert analytical publications. The agent must determine the relevant variables, population, and any weighting rules before computation.
* **Real Question**: What’s the median household income in the US in 2024?
* **Why this demonstrates the capability**: The answer depends on constructing the correct analysis-ready table, not on reading a single precomputed statistic. The agent must determine the right income variable, the unit of analysis, and any population or weighting conventions before calculating the median. This is analytic dataset construction in a realistic survey setting.

---
**[Case 2]**
* **Initial Environment**: A state-finance survey directory includes raw files and documentation describing revenue categories and units. Multiple revenue-related fields are present, so the analyst must build the exact analysis frame needed for the requested summary.
* **Real Question**: What percentage of total 2021 revenue came from intergovernmental revenue and insurance trust revenue?
* **Why this demonstrates the capability**: This task requires the agent to define total revenue and the relevant component fields consistently before the percentage can be computed. That means selecting the correct columns, unit conventions, and year-specific scope. The central difficulty is therefore constructing the right analysis dataset rather than applying a complex formula.

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
