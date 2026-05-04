---
name: state-centric-action-orchestration
description: Use this skill when the user wants an agent to handle complex projects by bridging different 'expert sub-tasks', tracking deeply nested historical logs to see what previously changed, or utilizing a shared memory blueprint. It is highly applicable when addressing a massive, unorganized environment where the agent posts a broadcast request (blackboard pattern) to asynchronously share discoveries, or needs to traverse a chronological history of prior actions. Trigger phrases include “keep track of what we've found so far,” “let the different tools see each other's work,” “tell me where you moved the items earlier,” “manage a project board for all the workers,” or “look at your action history to figure out the current status.”
---

# Skill: state-centric-action-orchestration

## 1. Capability Definition & Real Case
* **Professional Definition**: State-centric action orchestration is the capability of an orchestrator to manage complex, multi-domain workflows by maintaining an evolving, structured 'Consensus Memory', Task State, or 'Blackboard'. It delegates to specialized squads and standardizes inter-process communication exclusively through this persistent session state. This unified state additionally acts as an immutable, append-only chronological log. This dual functionality enables the orchestrator to synthesize loosely-coupled volunteer inputs dynamically, whilst resolving 'out-of-context' temporal queries by natively reviewing past interaction traces alongside present variables, preventing total context-window collapse.
* **Dimension Hierarchy**: Workflow Orchestration->Iterative Planning and Refinement->state-centric-action-orchestration

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-agent engineering workspace containing a Planner, an Optimization Squad (ACOPF), and a Reliability Squad (Contingency Analysis). The environment manages a shared session memory using schema-based templates.
* **Real Question**: Evaluate the current network case for economic efficiency, then identify the most critical assets by running a comprehensive reliability check using the exact optimal baseline.
* **Real Trajectory**: The Coordinator dispatches the Optimization Squad to identify a cost-minimized power flow state. Upon convergence, it writes the 'Solved Optimization State' to the shared session memory. The Coordinator then delegates to the Reliability Squad. Instead of blindly initializing, this squad reads the validated snapshot found in the Task State to automatically define its baseline for N-1 outages.
* **Real Answer**: System cost optimized at $42,000; the downstream reliability assessment utilizing this baseline identifies Line 10-15 as a newly critical vulnerability.
* **Why this demonstrates the capability**: This expands state-centric coordination to macro ‘Squad-to-Squad’ bridging. A deterministic output generated entirely by the first domain is immutably anchored into memory ensuring the subsequent phase does not succumb to drift.
---
**[Case 2]**
* **Initial Environment**: A multi-agent data lake spanning thousands of heterogeneous files. A central coordinator oversees the 'Blackboard' (state memory) monitored by specialized File Agents.
* **Real Question**: What is the age of the patient with the lowest APP-Z score in the UCEC CPTAC3 study?
* **Real Trajectory**: The coordinator lacks exact locations. It posts a request on the Blackboard State: 'I need APP-Z score and Age from UCEC CPTAC3'. Two File Agents monitoring the state independently push their localized discoveries (Age from mmc1, APP_Z from mmc7) back into the Shared State. The main orchestrator collects these decoupled discoveries and synthesizes a terminal script.
* **Real Answer**: Age 60, successfully derived by merging the decoupled file vectors volunteered into the shared state.
* **Why this demonstrates the capability**: This exhibits the 'Blackboard/Volunteer' pattern. By broadcasting via shared memory, it bypasses rigid master-slave routing and elegantly retrieves heterogeneous facts without bloating root context.
---
**[Case 3]**
* **Initial Environment**: A long-horizon multi-agent workspace that has completed multiple asynchronous file relocation tasks across deep directory structures. Direct polling yields a 'null' observation due to assets being shifted beyond standard view.
* **Real Question**: Where did the primary configuration payload end up after the failure you encountered earlier?
* **Real Trajectory**: The orchestrator notes it cannot 'see' the payload in the standard active directory context. Bypassing a blind global system search, it queries the Task State's chronological action log via vector retrieval. It tracks the payload's movement from 'Initial' to 'Staging', discovering it was ultimately parked via the log timestamp in an 'Overflow' cache location following a space-limit error. It provides this location straight from historical consensus memory.
* **Real Answer**: The configuration payload is residing in the Overflow cache; it was placed there historically following a space limitation event encountered during the mid-session staging phase.
* **Why this demonstrates the capability**: This demonstrates utilizing the Blackboard / Task State explicitly as a temporal anchor. Relying upon recorded execution history, the agent logically bridges an ambiguous physical present with a documented chronological past without resetting the query.

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
