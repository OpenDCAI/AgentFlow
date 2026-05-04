---
name: state-verified-task-completion
description: Use this skill when the user wants tasks that only count as solved if the underlying state really changed, not if the screen merely looks right for a moment. Trigger it for requests like “make sure it is actually saved,” “verify the result from the real app state,” “don’t trust a temporary popup,” or “judge success from the system record, not a screenshot alone.” This skill is for GUI tasks where durable completion must be grounded in application state, database state, filesystem state, or verified internal signals.
---

# Skill: state-verified-task-completion

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to complete GUI tasks in a way that produces a durable, verifiable change in the underlying application or system state, rather than only transient visual evidence. The agent must perform actions that survive beyond the immediate screen and can be checked via persistent state, reliable internal execution signals, or enterprise database record verification.
* **Dimension Hierarchy**: Goal-Directed GUI Workflow Execution->Verified Task Completion->state-verified-task-completion

### Real Case
**[Case 1]**
* **Initial Environment**: A mobile calendar application is open on a device where the benchmark can inspect the app’s stored event records after execution. The task parameters specify a date, time, title, description, and duration that must be committed to the underlying calendar state.
* **Real Question**: In Simple Calendar Pro, create a calendar event on 2014-03-16 at 14h with the title 'Project Review' and the description 'Bring the quarterly report'. The event should last for 45 mins.
* **Real Trajectory**: Open the event-creation flow, fill the date, time, title, description, and duration fields, save the entry, and verify that the event exists in the app state rather than relying only on the post-save screen.
* **Real Answer**: A calendar event with the specified fields exists in the calendar state.
* **Why this demonstrates the capability**: A transient success toast or a partially filled form is not enough here, because the benchmark checks whether the event was actually created. The agent must carry the interaction through to a committed state change that survives inspection. That is exactly what durable, state-verified completion measures.
---
**[Case 2]**
* **Initial Environment**: A desktop code editor is open on a project containing a function named `functionA`. The benchmark environment can internally observe debugging events and inspect in-memory execution data at the exact moment a breakpoint is hit.
* **Real Question**: Debug in VSCode by setting a breakpoint in `functionA`.
* **Real Trajectory**: Open the relevant source file, place a breakpoint on the intended line, launch the program in debug mode, wait for execution to reach the breakpoint, and confirm success from the actual breakpoint event and associated runtime state rather than from a guessed screenshot.
* **Real Answer**: The program halts at the breakpoint in `functionA`, and the debugger’s internal event confirms the hit.
* **Why this demonstrates the capability**: The visible editor alone cannot guarantee that the breakpoint actually fired at runtime. The true success condition is an internal execution event coupled with the correct paused state, which makes this case an example of state-grounded completion rather than superficial UI matching. It tests whether the agent produces a real backend-consistent result.
---
**[Case 3]**
* **Initial Environment**: A customer relationship management (CRM) system is open at the 'Task' imports page. The system contains a database of lead imports, some of which are marked with a 'Duplicate' status flag following a recent batch data load.
* **Real Question**: As a marketing specialist, count the entities marked as duplicates in the recent 'Task' imports to evaluate our data cleaning strategy.
* **Real Trajectory**: Scan the sidebar and click the 'Imports' menu icon to expand the navigation. Locate and click on the 'Import Results' link to view the history of data loads. Navigate to the specific row for the most recent 'Task' entity import and click the associated detail link. Filter or scan the detail list to identify records with the 'Duplicate' status tag. Perform a functional count of these specific records and verify the count against the visible summary footer ensuring it maps to the SQL persistence layer.
* **Real Answer**: There are 5 entities marked as duplicates in the recent 'Task' imports.
* **Why this demonstrates the capability**: This case demonstrates state-verified completion within an enterprise environment. The agent must navigate to a deep hierarchical menu and extract a value that is grounded in the underlying system schema, verifying that the persistent database state is correctly filtered and rendered to avoid superficial approximations.

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
