---
name: temporal-tabular-reasoning-data-synthesis
description: Use this skill when the user wants SQL tasks where time is the main source of difficulty. Trigger it for requests like “make it about first vs last”, “use date windows or age at event time”, “test recency and ordering”, or “the answer should change if the timeline is read incorrectly.” Example trigger: “I want first/last/most recent style SQL questions.” Example trigger: “Make time order and date arithmetic central.” Example trigger: “The model should fail if it misreads the timeline.”
---

# Skill: Temporal Tabular Reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to interpret and execute time-sensitive reasoning over relational data, including temporal ordering, recency, age calculation, interval comparisons, and counterfactual or shifted-time conditions.
* **Dimension Hierarchy**: Query Reasoning->Relational and Logical Composition->Temporal Tabular Reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A medal-history database stores athlete names, years, tournaments, medal outcomes, and event timestamps. The schema supports grouping and temporal filtering.
* **Real Question**: In which year did Áron Szilágyi achieve his personal highest number of gold medal wins?
* **Real Answer**: 2022.
* **Why this demonstrates the capability**: The question requires more than retrieving all rows for one athlete. The agent must filter to gold medals, group by year, count wins per year, and then rank those yearly counts to identify the peak year. Because the key logic is temporal grouping and comparison, it directly tests temporal tabular reasoning.

---
**[Case 2]**
* **Initial Environment**: The same sports-results environment stores athlete birth information and dated medal events. The answer depends on aligning event time to athlete age.
* **Real Question**: At what age did Michael Phelps win his most recent Olympic Gold Medal?
* **Real Answer**: The SQL must identify the most recent qualifying gold-medal event first and only then compute age at that event date.
* **Why this demonstrates the capability**: This task is easy to get wrong if the order of temporal operations is reversed. A model that computes age on the wrong event or ignores the recency constraint will still produce fluent SQL but the wrong answer. That makes it a strong temporal reasoning probe for SQL agents.

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
