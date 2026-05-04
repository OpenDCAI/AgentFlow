---
name: temporal-causal-dialogue-reasoning
description: Use this skill when the user asks something that depends on time, order, sequence, elapsed duration, or event cause-and-effect across earlier conversations. Trigger it for requests like 'how long since', 'what happened after', 'which came later', or 'summarize the chain of events'. Everyday examples include: 'how many months has it been since that museum visit?', 'what changed after the campaign season?', 'what caused the later plan to shift?', and 'summarize what happened in that period.'
---

# Skill: temporal-causal-dialogue-reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to reason over time, order, intervals, and causal relations embedded in dialogue histories, including timestamp metadata and event chains distributed across sessions.
* **Dimension Hierarchy**: Conversational Memory->Cross-session Synthesis->temporal-causal-dialogue-reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A long interaction history contains museum visits mentioned in separate sessions, each associated with explicit or implicit dates. The sessions are not adjacent, and the question asks about the elapsed time between a past event and a reference point.
* **Real Question**: How many months have passed since my last museum visit with a friend?
* **Real Trajectory**: 1. Retrieve all museum-visit mentions across sessions. 2. Identify which one involved a friend rather than a parent or solo visit. 3. Compare the dated session against the question timestamp. 4. Compute the elapsed interval and answer using the benchmark’s accepted time granularity.
* **Real Answer**: 5 months
* **Why this demonstrates the capability**: The assistant must combine semantic filtering with temporal computation. It is not enough to remember museum visits; it must also identify the right relation, place the event on the timeline, and compute the interval correctly.

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
