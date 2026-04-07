---
name: source-retrieval-data-synthesis
description: Use this skill when the user wants SQL training data where the hard part is first finding the right database or table collection before writing the query. Trigger it for requests like “make examples where the agent has to figure out which dataset matters”, “the data should not already be handed to the model”, “it should need to look through many tables first”, or “make open-domain SQL questions.” Example trigger: “The question should not tell the model which database to use.” Example trigger: “Make examples where the agent has to search several candidate tables first.” Example trigger: “I want SQL tasks that feel like finding the right data source is half the job.”
---

# Skill: Source Retrieval

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to identify which database, table bundle, or evidence-bearing source should be queried before any SQL is written, especially when the user question is asked in an open-domain or multi-database setting.
* **Dimension Hierarchy**: Environment Grounding->Retrieval and Alignment->Source Retrieval

### Real Case
**[Case 1]**
* **Initial Environment**: A large open collection of tabular sources is available, but the relevant table is not preselected. The agent starts only with the natural-language question and a retrieval interface over many candidate tables.
* **Real Question**: What is the highest eligible free rate for K-12 students in the schools in Alameda County?
* **Real Answer**: The agent must first retrieve the correct school-related table for Alameda County before the final SQL can be written and executed.
* **Why this demonstrates the capability**: This task is not hard because of exotic SQL syntax alone. It tests whether the agent can localize the correct source table from a larger corpus, avoid semantically nearby but irrelevant tables, and only then translate the question into executable SQL. A SQL agent that skips this retrieval step will often produce syntactically plausible but evidentially ungrounded queries.

---
**[Case 2]**
* **Initial Environment**: A multi-database environment contains several semantically similar schemas. The agent receives a user request but the target database is not explicitly named.
* **Real Question**: which semester the master and the bachelor both got enrolled in
* **Real Trajectory**: Retrieve candidate databases, inspect returned schema fragments, notice that a required degree_program relation is missing from the current candidate set, expand retrieval, and only then write the final SQL.
* **Real Answer**: A correct answer requires bringing the missing target database schema into context before composing SQL.
* **Why this demonstrates the capability**: The question is deceptively short and underspecified. It demonstrates source retrieval because the key failure mode is not merely choosing the wrong column but failing to recall the correct database at all. The successful trajectory therefore begins with retrieval repair rather than immediate SQL drafting.

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
