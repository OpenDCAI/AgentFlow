---
name: step-efficient-execution
description: Use this skill when the user wants data that tests whether the agent takes the shortest, most optimal GUI path instead of wandering, overthinking, or executing redundant actions. Trigger it for requests like 'same task but fewer clicks,' 'don't click the switch if it's already blue,' 'choose the fastest menu route,' 'only tick the box if it isn't already checked,' or 'make sure every move counts.' This skill is for GUI tasks where success alone is not enough; the trajectory must be highly compact, proving the agent avoids zero-value turns and respects state-aware 'No-Op' logic when a target is already configured correctly.
---

# Skill: step-efficient-execution

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to complete a GUI task with a near-minimal sequence of effective actions by performing dynamic process evaluation against available functional pathways. The agent must avert redundant planning loops, unnecessary reflection cycles, and superfluous verification steps. Crucially, this encompasses 'State-Aware Execution', wherein the agent perceives the current configuration of binary or multi-state widgets (e.g., toggles, checkboxes) and successfully concludes the task with zero redundant actions (a 'No-Op') if the target state already matches the user's intent, thereby preventing destructive double-toggling.
* **Dimension Hierarchy**: Reliable and Aligned Operation->Safe and Efficient Control->step-efficient-execution

### Real Case
**[Case 1]**
* **Initial Environment**: A document editor is open with two paragraphs already selected or easily reachable through a short sequence of formatting actions. The environment contains multiple nested menus and a direct-access formatting ribbon.
* **Real Question**: Change the line spacing of two paragraphs in a document to double-spaced.
* **Real Trajectory**: Navigate directly to the relevant paragraph-formatting control located immediately on the top ribbon, apply double spacing once, verify the state with a minimal visual check, and stop strictly, rather than repeatedly opening top-level 'Format' menus or re-applying the identical format command.
* **Real Answer**: Both paragraphs are double-spaced, utilizing a strictly compact trajectory containing zero unnecessary menu iteration.
* **Why this demonstrates the capability**: The benchmark value is isolating the gap between a concise, expert human minimal path and the lengthy, bloated trajectories typical of standard agents. An accurate but bloated path containing 15 formatting menu clicks indicates fundamental algorithmic inefficiency. Selecting the high-value shortcut validates step-efficient execution constraints.
---
**[Case 2]**
* **Initial Environment**: A GitLab project homepage is open. A left-hand navigation menu is visible containing several deeply nested entries including 'Project information', 'Repository', 'Issues', and 'Merge requests'.
* **Real Question**: Create a milestone for the upcoming task of merging all branches to main.
* **Real Trajectory**: Scan the navigation sidebar identifying candidate routes. Reject the procedurally common habit of clicking 'Project information' first, and directly select the 'Issues' tab which contains the explicit milestone management sub-module, taking the shortest functional leap.
* **Real Answer**: The 'Issues' section is entered immediately to begin milestone creation.
* **Why this demonstrates the capability**: This rejects a 'procedurally typical' but inefficient habit-loop. Instead of mindlessly opening project metadata panels first to 'orient' itself, the agent utilizes principle-guided UI analysis to deduce the 'Issues' section represents fundamentally higher task-progress value, actively reducing the navigation depth.
---
**[Case 3]**
* **Initial Environment**: A mobile device's detailed system settings page is open, displaying the 'Network & Internet' section. A toggle switch for 'WiFi' is visually present, and the track is visibly colored blue with the knob set to the right, dictating it is currently 'On'.
* **Real Question**: Turn on the WiFi connection.
* **Real Trajectory**: Inspect the 'WiFi' row visually identifying the switch coordinate. Perceive the switch is presently configured to the 'On' state. Analytically compare the current blue state to the user's requested 'Turn on' objective, recognize perfect alignment, and immediately terminate the task without issuing any physical click commands.
* **Real Answer**: Task finalized: WiFi is successfully observed as already active, requiring zero execution steps.
* **Why this demonstrates the capability**: This illustrates 'State-Aware Execution' serving step-efficiency. A naive agent blindly clicking the target matching the keyword 'WiFi' would incur a 'false positive' action, disastrously disabling the connection. Deriving efficiency necessitates avoiding the zero-value or destructive action entirely, exhibiting prime 'No-Op' trajectory precision.

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
