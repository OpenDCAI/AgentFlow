---
name: multi-session-synthesis
description: Use this skill when the answer is not written in one place and the agent has to connect several earlier conversations to solve the question. Trigger it for requests that sound like counting, comparing, reconciling, or combining old information. Everyday examples include: 'how many instruments do I own now?', 'which trip was the most recent?', 'what do all my earlier notes imply together?', and 'put the pieces from different chats together.'
---

# Skill: multi-session-synthesis

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to combine evidence from multiple distinct dialogue sessions in order to answer a single question that requires aggregation, comparison, or composition across sessions.
* **Dimension Hierarchy**: Conversational Memory->Cross-session Synthesis->multi-session-synthesis

### Real Case
**[Case 1]**
* **Initial Environment**: The user and assistant have discussed hobbies, purchases, and selling plans across many sessions spread over weeks. No single session states the final count directly, and several related possessions appear in different contexts.
* **Real Question**: How many musical instruments do I currently own?
* **Real Trajectory**: 1. Retrieve all sessions mentioning currently owned instruments and all sessions mentioning disposals. 2. Normalize each mention into owned, sold, or discussed categories. 3. Aggregate the remaining owned instruments across sessions. 4. Return the total count only after reconciling all cross-session evidence.
* **Real Answer**: 4
* **Why this demonstrates the capability**: The answer is distributed rather than locally stated. The assistant must synthesize ownership information across multiple sessions, distinguish current possessions from items being sold, and avoid counting outdated or hypothetical mentions.

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
