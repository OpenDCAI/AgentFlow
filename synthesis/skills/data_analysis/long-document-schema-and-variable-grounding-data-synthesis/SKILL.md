---
name: long-document-schema-and-variable-grounding-data-synthesis
description: Use this skill when the user wants questions where the hard part is reading long documentation before writing code. Trigger it for requests such as “make it dig through a codebook,” “make the agent figure out what the columns mean,” “make it use survey docs first,” or “make it connect the question to the right variables from a giant manual.” Plain-language examples: “Ask something where the data is easy but the documentation is the bottleneck,” “make it find the right field definitions,” “make it read the user guide before calculating.”
---

# Skill: Long-Document Schema And Variable Grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to navigate long codebooks, survey guides, manuals, and schema documents in order to determine which variables, populations, weights, and definitions are required for analysis. It focuses on document-grounded variable interpretation rather than raw numerical computation alone.
* **Dimension Hierarchy**: Data Grounding->Data Retrieval & Semantic Grounding->long-document schema and variable grounding

### Real Case
**[Case 1]**
* **Initial Environment**: One or more large survey data files are provided together with long codebooks, survey design reports, and user guides. The documentation is much longer than the raw query and contains the key definitions needed for correct variable selection.
* **Real Question**: What’s the median household income in the US in 2024?
* **Why this demonstrates the capability**: The numerical statistic is familiar, but solving it correctly requires grounding terms like household, pretax income, year, sample weights, and population filters in the documentation. The challenge therefore lies in aligning the question with variable definitions and survey conventions. This is exactly the kind of documentation-intensive grounding that real analysts perform before writing code.

---
**[Case 2]**
* **Initial Environment**: A government-finance survey directory contains raw data files plus official documentation that defines revenue categories, units, and reporting structure. The analyst must read documentation before computing any total.
* **Real Question**: What was the total state government revenue in 2021?
* **Why this demonstrates the capability**: The question sounds simple, but the answer depends on identifying the correct revenue field, unit convention, and population scope from documentation. Without those definitions, a model can easily sum the wrong fields or mix derived and raw variables. The case therefore demonstrates variable grounding through long-form documentation.

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
