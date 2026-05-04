---
name: exploration-aware-evidence-collection
description: Trigger this skill when the user wants questions where the agent must actually look around before answering, where a lucky guess should not count, or where the question should depend on a good exploration path. Plain-language triggers include: 'make it gather evidence first,' 'don't let it answer from common sense,' 'force it to inspect the right place,' 'questions where exploration quality matters,' and 'make the path part of the evaluation.'
---

# Skill: exploration-aware-evidence-collection

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability measures whether an embodied agent can plan and execute an exploration trajectory that collects sufficient task-relevant evidence before answering an open-ended question. It emphasizes grounding, evidence sufficiency, and the alignment between what the agent observed and what it claims in the final answer.
* **Dimension Hierarchy**: Goal-Directed Exploration->Question-Conditioned Exploration->exploration-aware-evidence-collection

### Real Case
**[Case 1]**
* **Initial Environment**: The agent starts in a home corridor outside the kitchen with only a partial view of cabinets and the sink area. The faucet itself is not visible from the start position.
* **Real Question**: Did I leave the faucet running in the kitchen?
* **Real Trajectory**: The agent walks from the corridor into the kitchen, turns toward the sink, inspects the faucet directly, and stops once the water state is visible.
* **Real Answer**: No, the faucet is turned off.
* **Why this demonstrates the capability**: The answer cannot be grounded from the starting observation. The agent must move to a location where the target state becomes directly observable. This tests exploration quality and evidence gathering rather than prior knowledge.
---
**[Case 2]**
* **Initial Environment**: The embodied agent begins near the entryway of an apartment. The living room and TV corner are not fully visible, and the floor lamp is hidden behind a partial wall until the agent enters deeper into the room.
* **Real Question**: Where is the floor lamp in the living room?
* **Real Trajectory**: The agent explores the living room, checks the TV side of the room, identifies the lamp, and records a grounded spatial answer tied to a visible landmark.
* **Real Answer**: It is in the corner of the living room, next to the TV.
* **Why this demonstrates the capability**: The correct answer depends on reaching a vantage point with clear evidence. A generic guess like 'near the couch' would be plausible but ungrounded. The capability is therefore about collecting the right visual proof before responding.
---
**[Case 3]**
* **Initial Environment**: The agent starts in a laundry-adjacent hallway and has not yet observed the utility area. Several rooms are reachable from the initial location, including a bathroom and a bedroom.
* **Real Question**: How many washing machines do I have?
* **Real Trajectory**: The agent first identifies the laundry region, enters it, inspects the appliance area, and counts distinct washing machine units before answering.
* **Real Answer**: Only one.
* **Why this demonstrates the capability**: The task is not answerable from commonsense priors because the home could plausibly contain zero, one, or multiple machines. The agent must collect counting evidence from a relevant region. This makes the exploration path itself part of the competence being tested.

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
