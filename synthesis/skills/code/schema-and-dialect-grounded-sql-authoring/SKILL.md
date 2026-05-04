---
name: schema-and-dialect-grounded-sql-authoring
description: Use this skill when the user wants SQL-generation data where the agent must read schema information, consult dialect docs, and produce correct queries for real databases. Trigger it for requests like 'generate enterprise SQL tasks', 'make BigQuery or Snowflake coding questions', 'create SQL problems that need schema lookup and docs', or 'give me text-to-SQL data for code agents'. Do not use it for broader multi-step analytics pipelines with many intermediate artifacts; use the orchestration skill for those.
---

# Skill: schema-and-dialect-grounded-sql-authoring

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to author correct SQL for enterprise data tasks by grounding decisions in large schemas, dialect-specific functions, auxiliary documentation, and execution feedback rather than in generic SQL pattern completion.
* **Dimension Hierarchy**: Data and ML Workflow Engineering->Enterprise Data Workflow Coding->schema-and-dialect-grounded-sql-authoring

### Real Case
**[Case 1]**
* **Initial Environment**: A workflow environment includes a large sales database, project documentation, and SQL dialect references. The task asks for a daily report covering completed tasks, events held, leads generated, and opportunity status counts.
* **Real Question**: Write the SQL needed to produce the requested daily sales activity report from the available warehouse tables.
* **Real Trajectory**: Inspect schema metadata and table descriptions, identify date and status fields, consult dialect documentation for required date truncation or aggregation behavior, draft the query, run it, correct column and join assumptions from execution feedback, and save the final SQL.
* **Real Answer**: A dialect-correct SQL query returns the required daily aggregates with the expected grouping and status logic.
* **Why this demonstrates the capability**: This demonstrates the capability because the challenge is not generic SQL syntax alone. The agent must ground joins, date functions, and field usage in a large schema and the correct SQL dialect, then verify the query by execution.
---
**[Case 2]**
* **Initial Environment**: A cloud warehouse task asks for no-tip percentages by borough for a constrained taxi subset. The environment includes schema docs, dialect docs, and a query interface.
* **Real Question**: Produce the query that computes no-tip percentage for each borough under the specified trip-validity constraints.
* **Real Trajectory**: Read the task carefully, inspect available tables and geographic fields, confirm dialect-specific safe division and date handling choices, execute candidate queries, and refine them until the result matches the expected shape.
* **Real Answer**: The final SQL correctly applies trip filters, computes the no-tip percentage, and groups results by borough in the target dialect.
* **Why this demonstrates the capability**: The capability is tested because correct output requires schema linking, constraint translation, and dialect-aware expression design. It is easy to write plausible SQL here; it is much harder to write warehouse-specific SQL that executes and answers the right question.

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
