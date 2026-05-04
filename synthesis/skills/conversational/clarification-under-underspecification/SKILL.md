---
name: clarification-under-underspecification
description: Use this skill when the user reveals the task bit by bit and the agent should pause, ask, and clarify instead of guessing too early. Trigger it for fragmented requests, drip-fed requirements, or conversations where the first turn is only a partial specification. Everyday examples include: 'I need a playlist… also add this… actually use this ratio', 'write a function… I’ll tell you the edge cases next', 'help me summarize these docs as I send them', and 'I have more constraints, don’t answer yet.'
---

# Skill: clarification-under-underspecification

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to notice that the user has not yet provided enough information, resist premature full-solution attempts, and ask focused clarification questions before committing to an answer.
* **Dimension Hierarchy**: Conversational Robustness->Underspecification Resilience->clarification-under-underspecification

### Real Case
**[Case 1]**
* **Initial Environment**: A user reveals a task in fragments over multiple turns. The assistant has enough partial context to guess a likely solution path, but not enough information to complete the task correctly yet.
* **Real Question**: Let’s make a 35-minute playlist. Let’s add Taylor Swift songs. Let’s also put some Maroon 5. I prefer Taylor Swift, let’s do 20 minutes of that. So that leaves 15 minutes for Maroon 5.
* **Real Trajectory**: 1. Treat the early turns as incomplete shards rather than final specifications. 2. Ask whether the user wants actual songs, a plan, or API actions if the platform context is still unclear. 3. Wait to formulate a final action until all necessary structure is present. 4. Once clarified, generate the final constrained solution cleanly without inheriting earlier mistaken assumptions.
* **Real Answer**: A short clarification-first response that requests the missing operational detail needed to turn the fragmented preference stream into a correct final action.
* **Why this demonstrates the capability**: Weak assistants often interpret early fragments as license to answer the entire problem immediately. This capability measures whether the model can detect underspecification, hold back from premature commitment, and steer the conversation toward the minimum missing detail.

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
