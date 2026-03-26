---
name: temporal-sequential-reasoning-data-synthesis
description: Use this skill when the user wants 'before or after' questions, timeline questions, year-over-year questions, trend questions, or anything involving ordering events across documents. Trigger it for requests like 'make it depend on chronology', 'test whether the model can follow a timeline', or 'ask about changes over time'. This skill is the temporal version of multi-source reasoning.
---

# Skill: Temporal-Sequential Reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to normalize, order, and compare time-sensitive evidence across documents in order to answer before/after, trend, interval, or temporal-gap questions. The key challenge is that temporal evidence is often distributed, differently formatted, and easy to mis-sequence.
* **Dimension Hierarchy**: Multi-Source Evidence Composition->Cross-Document Synthesis->Temporal-Sequential Reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A bounded product-and-release corpus containing one document about Apple’s AirTag and another about the 5th generation iPad Pro. The answer depends on correctly ordering the two launches in time.
* **Real Question**: Did Apple introduce the AirTag tracking device before or after the launch of the 5th generation iPad Pro?
* **Real Answer**: A before/after answer based on chronological ordering.
* **Why this demonstrates the capability**: The documents individually provide event information, but the question is about temporal relation rather than isolated facts. The agent must normalize the timestamps and then compare them. This tests chronological reasoning rather than pure retrieval.
---
**[Case 2]**
* **Initial Environment**: A bounded bundle of company reports across 2022, 2023, and 2024. Each report provides a year-specific cash-flow figure for the same company.
* **Real Question**: What is the trend in ARVANA INC's cash flow over the years 2022, 2023, and 2024?
* **Real Answer**: The cash flow increased from $3,340 in 2022 to $139,025 in 2023, but then significantly decreased to $(120,294) in 2024.
* **Why this demonstrates the capability**: The answer requires extracting multiple time-stamped values and then summarizing the directional pattern over time. A model that only copies the numbers without reasoning about temporal order will miss the trend. This makes the task a genuine time-series reasoning problem over documents.
---
**[Case 3]**
* **Initial Environment**: A bounded article set about film awards across years. One document provides a best-actor year, while another supports tracing back to the best-costume-design winner sixteen years earlier.
* **Real Question**: Leonardo DiCaprio once won an Oscar for best actor. Who won the award for best costume design sixteen years earlier?
* **Real Answer**: An entity answer recovered by applying a temporal offset and then locating the earlier award winner.
* **Why this demonstrates the capability**: This case combines temporal offsetting with retrieval. The agent must first anchor the reference year, subtract the specified interval, and then retrieve the correct winner for the derived year. The temporal transformation is the crucial step.

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
