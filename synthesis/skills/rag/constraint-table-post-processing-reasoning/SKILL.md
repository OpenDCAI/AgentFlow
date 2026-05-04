---
name: constraint / table / post-processing reasoning
description: Use this skill when the user wants table-heavy questions, specific API/formatting constraints, multi-conditional sorting, trade-off optimization, or forced use of official glossaries. Trigger it for requests like 'list items that strictly meet all these criteria', 'optimize the settings for X while staying under budget Y', 'use the official dictionary provided', 'convert the retrieved date', or 'balance accuracy with cost'.
---

# Skill: constraint / table / post-processing reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to retrieve structured evidence or candidate pools, and apply rigorous operations including multi-faceted filtering, Pareto optimization (trade-offs), and post-retrieval transformations (e.g., format conversions, explicit glossary mapping, and strict actor-role verification). This prevents dropping minor negative constraints and ensures strict obedience to authoritative formatting rules.
* **Dimension Hierarchy**: Multi-Source Evidence Composition->Cross-Document Synthesis->constraint / table / post-processing reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A RAG context containing biographical textual data for dozens of historical figures, including detailed records of their birthplaces, nationalities, and exploration routes.
* **Real Question**: List three European explorers who circumnavigated the globe before the 18th century and were not born in England or Portugal.
* **Real Trajectory**: The agent decomposes the query into constraints: [Circumnavigated globe], [Before 18th century], [Not born in England], [Not born in Portugal], [Quantity: 3]. It retrieves Magellan (Portugal) and Drake (England), rigorously rejects them due to the birth constraints, and intersects the requirements to find three French/Spanish candidates.
* **Real Answer**: 1. Juan Sebastián Elcano, 2. Jacques Hermite, 3. Louis-Antoine de Bougainville.
* **Why this demonstrates the capability**: This illustrates rigid multi-constraint text filtering. It proves the agent resolves negative textual constraints and chronological limits simultaneously without overshadowing the logic with more famous, but invalid, entities.
---
**[Case 2]**
* **Initial Environment**: A RAG context containing a structured design-space table for TPU configurations. The table lists entries with unique IDs and reported PPA (Power-Performance-Area) metrics.
* **Real Question**: Generate a TPU architecture for ResNet56 inference on CIFAR-10. The design must be optimized to stay under a power budget of 150mW and an area of 0.45mm², while staying as close as possible to a reference latency of 50ms.
* **Real Trajectory**: The agent filters configurations compatible with ResNet56. It applies the 'Power < 150' and 'Area < 0.45' hard constraints to narrow the pool. It calculates the absolute difference between each remaining candidate's latency and the 50ms target, selecting the variant which satisfies both budgets while exhibiting the minimal latency deviation.
* **Real Answer**: The optimal TPU configuration uses a 16x16 systolic array with BAM units.
* **Why this demonstrates the capability**: This case demonstrates multi-objective optimization under numeric budgets. The agent must perform a relative comparison between valid candidates to minimize the deviation from a target latency, effectively balancing overlapping distinct numeric constraints.
---
**[Case 3]**
* **Initial Environment**: A RAG context containing a judicial judgment and a specialized 'Combined DOJ Glossary' that defines 'Appellant' as '上訴人' and 'Respondent' as '答辯人', and provides 'HKSAR v. LAI' formatting which lists LAI precisely under the role of 'Respondent'.
* **Real Question**: Based on the official glossary, what is the official Chinese role and name of the individual defending against the appeal?
* **Real Trajectory**: The agent retrieves the glossary to identify the official term ('Respondent' -> '答辯人'). It scans the header to locate the precise Subject-Object relational mapping. It enforces this relational constraint during synthesis to prevent swapping actor identities.
* **Real Answer**: 答辯人：黎智英（LAI CHEE YING）
* **Why this demonstrates the capability**: This demonstrates authoritative lexical alignment and relational filtering. The agent applies an explicit text-transformation constraint (using an official glossary lookup) and verifies a strict structural relationship (Subject-Object role) prior to final text generation, preventing lexical dilution and role-flipping.

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
