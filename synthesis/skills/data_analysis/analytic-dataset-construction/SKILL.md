---
name: analytic dataset construction
description: Use this skill when the user wants the agent to *set up the right analysis table* before doing any statistics. Trigger it for requests such as “make it build the dataset first,” “make it pick variables, weights, and filters,” “calculate rolling aggregates/windows,” “find streaks of behavior,” or “make the real work be dataset setup.” Plain-language examples: “Ask something where the agent must prepare the analysis frame,” “make it decide who is in scope,” “analyze the data in batches of time,” or “make it choose the right columns and units before computing.”
---

# Skill: analytic dataset construction

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to build the correct analysis-ready dataset from raw sources by selecting variables, defining the population, applying weights or filters (including temporal bounds, rolling windows, and sequence states), and deriving the exact table needed for downstream analysis. It is broader than one-off cleaning and focuses on constructing the right analytic view of the data.
* **Dimension Hierarchy**: Analytical Transformation->Data Preparation->analytic dataset construction

### Real Case
**[Case 1]**
* **Initial Environment**: Large survey data files are accompanied by codebooks, survey-design documents, and expert analytical publications. The agent must determine the relevant variables, population, and any weighting rules before computation.
* **Real Question**: What’s the median household income in the US in 2024?
* **Real Trajectory**: Read codebooks to identify the correct income variable and weight definition; load dataset; filter for household-level entities in 2024; apply survey weights; compute the median.
* **Real Answer**: Ignore specific value, output median.
* **Why this demonstrates the capability**: The answer depends on constructing the correct analysis-ready table, not on reading a single precomputed statistic. The agent must determine the right income variable, the unit of analysis, and any population or weighting conventions before calculating the median. This is analytic dataset construction in a realistic survey setting.
---
**[Case 2]**
* **Initial Environment**: A state-finance survey directory includes raw files and documentation describing revenue categories and units. Multiple revenue-related fields are present, so the analyst must build the exact analysis frame needed for the requested summary.
* **Real Question**: What percentage of total 2021 revenue came from intergovernmental revenue and insurance trust revenue?
* **Real Trajectory**: Filter for 2021 records; align component columns based on definitions; sum components; divide by the derived total revenue field; return ratio.
* **Real Answer**: Ignore specific value, return ratio.
* **Why this demonstrates the capability**: This task requires the agent to define total revenue and the relevant component fields consistently before the percentage can be computed. That means selecting the correct columns, unit conventions, and year-specific scope. The central difficulty is therefore constructing the right analysis dataset rather than applying a complex formula.
---
**[Case 3]**
* **Initial Environment**: A CSV log file containing server access events with columns for 'timestamp', 'user_id', and 'action_status'. The environment allows for standard python-based data manipulation including state tracking.
* **Real Question**: Identify all users who had three or more consecutive 'failed' login attempts within any five-minute window.
* **Real Trajectory**: Load logs; parse datetime format; sort by user and time; apply a 5-minute rolling time window per user constraint; build a stateful sequence accumulator tracking consecutive failures; derive the streak-flag column; extract the final user list.
* **Real Answer**: ['user_882', 'user_104', 'user_991']
* **Why this demonstrates the capability**: This task requires more than simple static filtering. Constructing the correct tabular analysis frame mandates tracking temporal sliding windows and evaluating sequential states (streaks) over time indices to expose the precise cohort demanded by the question.

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
