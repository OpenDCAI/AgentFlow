---
name: resource-lifecycle-orchestration
description: Use this when the user wants data tracking procedural cycles, tool usages, or tracking task progression using history logs or videos. Trigger it for requests like 'what is the next move for this recipe', 'make maintenance tasks with strict cleaning orders', 'look at my progress video and tell me what to do now', or 'create plans where forgetting to reset a tool ruins the workflow.'
---

# Skill: resource-lifecycle-orchestration

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to track and manipulate reusable resources, process stages, and continuous workflow progress across sequential operations. It integrates environment states, visual task histories, and procedural dependency chains to ascertain precise cleanup, initialization, or next-action logic.
* **Dimension Hierarchy**: Closed-World Symbolic Planning->State and Resource Reasoning->resource-lifecycle-orchestration

### Real Case
**[Case 1]**
* **Initial Environment**: A service robot works behind a bar with one shaker, two shot glasses, a sink, and ingredients for a cocktail order. One shot glass is dirty, and the clean glass is assigned to the first drink.
* **Real Question**: Prepare one gin-and-tonic and one vodka-lime order using the available glasses. Reuse equipment only when its state allows it, and leave the bar in a finished service state.
* **Real Trajectory**: Rinse the dirty shot glass. Fill the shaker. Shake and pour the first drink. Rinse the shaker. Load the second recipe. Shake and pour into the newly cleaned glass. Return the shaker.
* **Real Answer**: Valid plan completing drink orders by resetting container availability recursively across the workflow.
* **Why this demonstrates the capability**: Extracts lifecycle orchestration natively alternating states between clean, in-use, dirty, and reset. The agent demonstrates long-horizon progress tracking, satisfying hidden reset obligations necessary for tool reuse.
---
**[Case 2]**
* **Initial Environment**: A kitchen scene processing recipes. A multimodal progress video illustrates a cook has already opened a cream cheese wrapper and added its contents explicitly to a soup pot. The observation frame isolates the cook holding the empty container.
* **Real Question**: Considering the video progress and current observation, what action should I take next in order to add cream cheese to the soup?
* **Real Trajectory**: Analyze video history confirming primary addition step is accomplished. Observe current hand-state holding depleted resource shell. Identify workflow requires transitioning into procedural clean-up phase avoiding resource deadlock. Execute immediate item discard command.
* **Real Answer**: Throw away the empty cream cheese container.
* **Why this demonstrates the capability**: Utilizes modality-agnostic process tracking comparing completed progress against active limitations. Disposing of the depleted resource cleanly bridges the operational boundary separating 'task execution' from 'workspace reset', avoiding redundant looping.
---
**[Case 3]**
* **Initial Environment**: A roadside maintenance puzzle tracking flat-tire procedures. Required tool allocations span jacks, wrenches, and pumps occupying distinct prep, physical application, and securing transition stages.
* **Real Question**: Replace the flat tire, properly secure tools, and restore the operational environment completely.
* **Real Trajectory**: Extract jack/wrench. Elevate vehicle. Swap tire geometry. Lower chassis. Sequentially return contaminated/used items matching exact storage mapping closing the tool lifecycle securely.
* **Real Answer**: A sequential array prioritizing extraction, mechanical application, safety checks, and absolute asset reorganization.
* **Why this demonstrates the capability**: Mandates rigid temporal synchronization executing linear tool obligations avoiding dangerous misordering. Securing endpoints emphasizes restoration cycles verifying closed-loop physical readiness tracking.

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
