---
name: sql-debugging-and-repair-data-synthesis
description: Use this skill when the user wants data where the agent does not start from scratch, but must fix broken SQL. Trigger it for requests like “make debugging tasks”, “start from a wrong query”, “the model should repair existing SQL”, or “I want issue-resolution examples rather than plain text-to-SQL.” Example trigger: “I want SQL repair tasks, not blank-slate generation.” Example trigger: “Give the agent a buggy query and make it fix it.” Example trigger: “The challenge should be diagnosis plus correction.”
---

# Skill: SQL Debugging and Repair

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to inspect an existing but incorrect SQL query, diagnose why it fails or behaves undesirably, interact with the schema or execution environment, and produce a corrected SQL solution.
* **Dimension Hierarchy**: Robustness and Adaptation->Corrective Reasoning->SQL Debugging and Repair

### Real Case
**[Case 1]**
* **Initial Environment**: A relational database contains a hierarchical card_type table with parent-child references. The user already has a recursive query that executes, but its output structure does not match the desired grouped tree representation.
* **Real Question**: I have a certain hierarchy of data in the card_type table ... I would prefer to have a structured output where each parent card includes a list of its child cards ... Can you guide me on how to achieve this transformation using SQL?
* **Real Trajectory**: Read the issue description, inspect the existing recursive SQL, identify that it aggregates parent paths rather than child groups, revise the recursion and aggregation logic, and validate the repaired query.
* **Real Answer**: The correct solution rewrites the recursive logic so the output groups child-card identifiers under the intended parent structure.
* **Why this demonstrates the capability**: The problem is not natural-language-to-SQL from scratch. The agent must first understand the user’s intended output format, then diagnose how the current recursive query deviates from that intent, and only then repair it. That makes debugging and repair the primary capability under test.

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
