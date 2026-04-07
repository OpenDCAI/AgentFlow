---
name: schema-item-grounding-data-synthesis
description: Use this skill when the user wants examples where the SQL agent already has the right database, but still has to pick the right tables, columns, or join fields. Trigger it for requests like “make the schema confusing”, “lots of similar columns should exist”, “the model should choose the right field not just the right DB”, or “I want table-and-column grounding tasks.” Example trigger: “The database is correct, but the hard part should be picking the right columns.” Example trigger: “I want tasks with many lookalike fields and missing join hints.” Example trigger: “Make the schema noisy so the agent has to ground precisely.”
---

# Skill: Schema Item Grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to map a natural-language question onto the correct tables, columns, and join keys inside a known relational schema, even when schemas are large, redundant, or semantically overlapping.
* **Dimension Hierarchy**: Environment Grounding->Retrieval and Alignment->Schema Item Grounding

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is given a relational schema where multiple tables contain superficially similar name fields. The target database has already been retrieved.
* **Real Question**: The first name of students who have both cats and dogs
* **Real Trajectory**: Inspect the student, pet, and ownership-related tables; reject unrelated name-bearing tables; identify the correct entity and relation path; and compose the SQL with the correct grounding.
* **Real Answer**: The correct SQL must use the student name field rather than a semantically tempting but irrelevant person-name field from another schema area.
* **Why this demonstrates the capability**: This case isolates table-and-column grounding from source retrieval. The database is available, but the agent still fails if it maps the question to a semantically similar yet wrong table. It therefore tests exact schema attachment rather than coarse topical retrieval.

---
**[Case 2]**
* **Initial Environment**: A correct table has already been selected, but the join path depends on specific foreign-key style columns. The agent must inspect relation fields instead of guessing them.
* **Real Question**: Return the rows that connect pets to owners through the ownership bridge table.
* **Real Trajectory**: Read the bridge table, identify the correct join columns such as pet identifiers on both sides, and write the join with those exact fields.
* **Real Answer**: A valid answer requires using the correct bridge-key columns rather than omitting or hallucinating the join keys.
* **Why this demonstrates the capability**: This demonstrates that grounding errors occur even after the correct table family is known. The failure is specifically column-level: the SQL breaks if the agent misses the key fields needed to connect the relations. That makes it an archetypal schema item grounding case.

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
