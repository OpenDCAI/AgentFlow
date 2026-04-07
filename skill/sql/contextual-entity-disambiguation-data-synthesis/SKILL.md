---
name: contextual-entity-disambiguation-data-synthesis
description: Use this skill when the user wants data where the wording is everyday, incomplete, or ambiguous, so the agent must connect the phrasing to the schema and data values. Trigger it for requests like “make the wording a bit unclear”, “use nicknames or missing context”, “force the model to disambiguate products or entities”, or “let the user talk like an operator instead of a database expert.” Example trigger: “The question should sound natural and a little under-specified.” Example trigger: “Use phrases that could map to several products or categories.” Example trigger: “Make the model infer the intended entity from context, not from exact schema wording.”
---

# Skill: Contextual Entity Disambiguation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to resolve ambiguous, under-specified, or colloquial mentions in a user question into the exact schema elements, entity values, and constraints required for SQL execution.
* **Dimension Hierarchy**: Environment Grounding->Retrieval and Alignment->Contextual Entity Disambiguation

### Real Case
**[Case 1]**
* **Initial Environment**: A localized enterprise database contains translated table names, translated enumerations, and preserved canonical identifiers. The question is natural but does not name the exact schema columns.
* **Real Question**: For each visitor, days between the first transaction and the first visit in Feb 2017; also report the device category.
* **Real Answer**: A correct SQL answer must map “device category” to the proper device-related schema fields rather than inventing a new column.
* **Why this demonstrates the capability**: The difficulty lies in converting informal analytic wording into the concrete schema vocabulary. The question contains enough intent to solve the task, but not enough literal overlap to make lexical matching sufficient. That forces the agent to use contextual disambiguation rather than surface-form copying.

---
**[Case 2]**
* **Initial Environment**: A retail-style database includes product names that overlap with descriptive language. The system also contains other products whose names partially match the same tokens.
* **Real Question**: Show me top-selling product among customers who bought YouTube Men’s Vintage Henley in July 2017 (exclude that product).
* **Real Answer**: The query must retain the canonical product name as an entity mention while excluding it from the result set.
* **Why this demonstrates the capability**: This is not merely a string filter problem. The agent must recognize that a multi-token product title is an entity value, must preserve it exactly in the predicate, and must still reason compositionally about the exclusion clause. That combination makes contextual disambiguation central to success.

---
**[Case 3]**
* **Initial Environment**: A maritime traffic database stores vessel, port, and waterway entities under operational identifiers rather than user-facing shorthand. The user speaks like a domain operator, not like a database engineer.
* **Real Question**: List all the vessels in strait, which speed higher than 1 kn and going to Singapore Port, show mmsi, name and strait name.
* **Real Trajectory**: Resolve “strait” and “Singapore Port” against known geographic entities, verify the candidate entity values against the database, then translate the resolved predicates into SQL.
* **Real Answer**: A correct answer requires binding the colloquial location phrases to the actual database entities before filtering and projection.
* **Why this demonstrates the capability**: The user utterance is operational and compact, not schema aligned. The challenge is to infer what concrete entity values and geographic references the user means, then write SQL against those exact values. This is precisely the behavior that contextual entity disambiguation is meant to test.

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
