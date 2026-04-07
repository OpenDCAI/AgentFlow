---
name: long-horizon-web-task-execution-data-synthesis
description: Use this skill when the user wants a long browser task with many clicks, filters, forms, or step-by-step operations rather than a short answer lookup. Trigger it for requests like “make it take a bunch of steps,” “test whether the agent can finish a whole web workflow,” or “include multiple filters and page changes.” It is especially appropriate when the challenge is completing the entire task correctly under long-horizon control pressure.
---

# Skill: Long-Horizon Web Task Execution

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to execute extended web task sequences that require maintaining task state, satisfying multiple constraints, navigating across page transitions, and completing all required steps without omission.
* **Dimension Hierarchy**: Web Interaction Execution->Web Control->Long-Horizon Web Task Execution

### Real Case
**[Case 1]**
* **Initial Environment**: A shopping website opened to a product-search or category page where sorting and filtering controls are available but not yet configured.
* **Real Question**: Look for the newest refrigerator that is 34-36 inches wide, priced between $1,000 and $2,000, and have a customer review rating of 4 stars or higher.
* **Why this demonstrates the capability**: The task is not solved by reading one page or applying one filter. The agent must preserve all four constraints across multiple interactions, avoid forgetting earlier requirements, and verify that the selected result still satisfies the full conjunction. This directly tests long-horizon execution because failure often comes from omitting one step, applying the wrong range, or prematurely stopping after a partially matching result.

---
**[Case 2]**
* **Initial Environment**: An email client or browser UI where the relevant item must first be found, then a secondary workflow must be executed in a new state.
* **Real Question**: Find Gisele’s email and forward it to Siana, please.
* **Real Trajectory**: Locate the correct message in the inbox, open it, activate the forward workflow, type the recipient, and confirm the action in the new interface state.
* **Why this demonstrates the capability**: Even though the interface is small, the task spans multiple dependent actions with no single-step shortcut. The agent must maintain the user goal across state transitions and complete the workflow all the way to the end. This illustrates the long-horizon property that partial progress is worthless if the final action is omitted or misdirected.

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
