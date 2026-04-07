---
name: nested-aggregation-filter-reasoning-data-synthesis
description: Use this skill when the user wants SQL questions that are hard because of layered logic, rankings, counts, HAVING clauses, nested conditions, or “top / most / per group” style analytics. Trigger it for requests like “make it analytically tricky”, “it should need grouping and filtering together”, “use ranking or nested logic”, or “I want SQL that breaks if the order of reasoning is wrong.” Example trigger: “Make the SQL analytically tricky, not just join-heavy.” Example trigger: “I want tasks with group-by plus conditions plus ranking.” Example trigger: “Use nested logic so the wrong order gives the wrong answer.”
---

# Skill: Nested Aggregation and Filter Reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to combine grouping, aggregation, nested subqueries, ranking, and compound filters into a logically coherent SQL program that matches the exact analytical intent of the question.
* **Dimension Hierarchy**: Query Reasoning->Relational and Logical Composition->Nested Aggregation and Filter Reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: An enterprise analytics environment contains session, geography, weather, and transaction-style data. The task descriptions may be rewritten into more analytical forms than the original SQL examples.
* **Real Question**: Change page view order to page conversion rate.
* **Real Answer**: The correct SQL must aggregate session or page-level events, compute a rate rather than a simple ordered list, and preserve the intended denominator.
* **Why this demonstrates the capability**: This example moves the task from direct retrieval to derived analytics. The agent must reason about what constitutes the numerator, what constitutes the denominator, and where aggregation should occur. It therefore tests nested aggregation and filter reasoning rather than only lexical translation.

---
**[Case 2]**
* **Initial Environment**: A sports-results table contains athletes, years, medal outcomes, and event metadata. The user asks a question whose answer depends on correctly aligning time windows, grouping, and ranking.
* **Real Question**: Which athlete had the most consistent medal wins over the last decade?
* **Real Answer**: A correct answer requires a grouped temporal aggregate over a bounded time window and a consistency definition that must be operationalized in SQL.
* **Why this demonstrates the capability**: This question cannot be answered with a simple max over raw rows. The agent has to decide the grouping unit, compute an aggregation over time, and then rank by the intended notion of consistency. That combination is exactly what this capability targets.

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
