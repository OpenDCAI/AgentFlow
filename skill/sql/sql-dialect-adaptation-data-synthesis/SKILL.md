---
name: sql-dialect-adaptation-data-synthesis
description: Use this skill when the user wants SQL tasks where the model must care about the target database engine and its function set. Trigger it for requests like “mix BigQuery and Snowflake style”, “test dialect-specific functions”, “make syntax portability matter”, or “the same intent should behave differently across engines.” Example trigger: “I want SQL data that tests engine-specific syntax.” Example trigger: “Make dialect differences matter.” Example trigger: “Use realistic warehouse functions, not generic classroom SQL.”
---

# Skill: SQL Dialect Adaptation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to generate correct SQL under dialect-specific syntax, functions, and execution assumptions, rather than relying on a single generic SQL style.
* **Dimension Hierarchy**: Robustness and Adaptation->Interface Adaptation->SQL Dialect Adaptation

### Real Case
**[Case 1]**
* **Initial Environment**: A real enterprise analytics project contains DBT-style SQL, warehouse-specific date functions, and multiple operational tables. The environment may be backed by BigQuery or Snowflake-like semantics.
* **Real Question**: I need a daily report on key sales activities—covering tasks completed, events held, leads generated, and the status of opportunities.
* **Real Trajectory**: Inspect the dialect documentation, preserve dialect-specific date truncation and CASE logic, then build the final query in the correct engine style.
* **Real Answer**: A correct answer must honor engine-specific function forms instead of rewriting everything into unsupported generic SQL.
* **Why this demonstrates the capability**: The task is not just a logical analytic rewrite. It is also a dialect adaptation problem because date, status, and transformation logic are expressed through warehouse- and DBT-specific constructs. The agent therefore has to couple semantic planning with dialect awareness.

---
**[Case 2]**
* **Initial Environment**: A biomedical benchmark is deployed on BigQuery and provides schema plus domain instructions. The model must generate executable SQL in a cloud-native dialect.
* **Real Question**: Are there any C9orf72 gene mutations that increase the risk of Parkinson’s disease?
* **Real Answer**: The generated SQL must use BigQuery-compatible table references and remain executable in that environment.
* **Why this demonstrates the capability**: Even when the scientific reasoning is correct, the query still fails if the dialect is wrong. This case shows that domain reasoning and dialect adaptation are separable requirements, both of which must be satisfied. It is therefore a clean example of dialect-aware SQL generation.

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
