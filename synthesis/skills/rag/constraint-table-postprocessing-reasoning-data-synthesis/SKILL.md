---
name: constraint-table-postprocessing-reasoning-data-synthesis
description: Use this skill when the user wants table-heavy questions, multi-constraint questions, ranking/filtering problems, or questions that require a small operation after reading the docs. Trigger it for requests like 'make it use a table', 'ask for the one that fits several conditions', 'force some calculation or formatting', or 'make the answer require post-processing'. This skill targets retrieval-plus-operation behavior.
---

# Skill: Constraint / Table / Post-Processing Reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to answer after retrieving the right evidence and then applying filtering, intersection, ranking, light calculation, table reading, grouping, or output-format transformation. The core challenge is operational reasoning after retrieval, not retrieval alone.
* **Dimension Hierarchy**: Multi-Source Evidence Composition->Cross-Document Synthesis->Constraint / Table / Post-Processing Reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A bounded Wikipedia-derived corpus containing road-network and airport facts. The answer is the airport satisfying two simultaneous geographic constraints.
* **Real Question**: I’m thinking of an airport near the intersection of US-52 and I-95. Can you remind me which one it is?
* **Real Answer**: A unique airport determined by intersecting both constraints.
* **Why this demonstrates the capability**: The model must retrieve multiple candidate facts and then apply an intersection operation. A response based on only one constraint is not enough. This makes the task a classic constraint-satisfaction problem over retrieved knowledge.
---
**[Case 2]**
* **Initial Environment**: A bounded sports-information corpus with tables or infobox-like records for tournament statistics. The needed value is not a narrative fact but a table cell associated with a specific role and year.
* **Real Question**: How many runs did the West Indies vice-captain score in the 1983 World Cup?
* **Real Answer**: A numeric answer extracted from table-like evidence.
* **Why this demonstrates the capability**: The challenge is reading structured evidence and selecting the correct row-column combination rather than retrieving a prose sentence. The agent must bind the right team role, tournament, and statistic together. This is table reasoning embedded inside RAG.
---
**[Case 3]**
* **Initial Environment**: A bounded factual corpus about countries, founding years, and numeral systems. The answer requires finding an entity, applying a year offset, and converting the result into Roman numerals.
* **Real Question**: What is five years after the founding of the largest country in North America in Roman numerals?
* **Real Answer**: A Roman-numeral year derived after retrieval and post-processing.
* **Why this demonstrates the capability**: This case shows that retrieval can be only the first stage of the task. After the relevant fact is found, the model must perform an operation and format the answer in a prescribed representation. The capability is therefore operation-aware grounded reasoning.

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
