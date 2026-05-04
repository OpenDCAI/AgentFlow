---
name: hierarchical-symbolic-subgoal-decomposition
description: Use this when the user wants to solve a large, multi-faceted project by breaking a distal goal into a sequence of abstract middle-states, sub-goals, or typed nodes like research versus writing. Trigger it for requests like 'break this big project into different types of steps', 'recursively decompose this goal until you have simple steps', 'give me a high-level strategy and then the moves to do it', or 'organize a plan where composition steps wait for reasoning steps.'
---

# Skill: hierarchical-symbolic-subgoal-decomposition

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to decompose complex, long-horizon objectives into an abstract transition graph or Directed Acyclic Graph (DAG) of sub-tasks. The agent bridges disparate levels of abstraction by treating nodes as specific cognitive types (e.g., Retrieval, Reasoning, Composition), structuring state-based dependencies (e.g., ACTIVE, SUSPENDED, SILENT), and subsequently implementing those intermediate goals as precise, grounded action sequences within the environment.
* **Dimension Hierarchy**: Closed-World Symbolic Planning->Goal Abstraction and Multi-Level Planning->hierarchical-symbolic-subgoal-decomposition

### Real Case
**[Case 1]**
* **Initial Environment**: A complex 2D platformer environment with a player character, a key located on a high ledge, several intermediate platforms, ladders, and moving hazards. The low-level action space is large and requires over 100 precise movements to reach the key.
* **Real Question**: Develop a plan for the player character to successfully collect the key while avoiding all hazards.
* **Real Trajectory**: 1. [High-Level Plan]: Decompose distal goal 'Collect Key' into abstract contact states: {Touch Platform A, Touch Ladder B, Touch Key}. 2. [Sub-goal]: Plan sequence bridging Platform A to Ladder B. 3. [Execution]: Output atomic movements (LEFT, RIGHT, JUMP).
* **Real Answer**: A hierarchical sequence of atomic actions that satisfies each intermediate contact sub-goal until the key is acquired.
* **Why this demonstrates the capability**: The task requires hierarchical decomposition because direct search is intractable. By first building a graph of 'object contacts' and finding a path through these nodes, the planner reduces the distal problem into manageable sub-tasks.
---
**[Case 2]**
* **Initial Environment**: A technical research agent has access to a live search API and an internal document workspace. The goal is to produce a comprehensive viability report for DeFi protocols by combining disjoint data sources.
* **Real Question**: Analyze investment trends in climate technology, merging public financing data and patent applications into a final document.
* **Real Trajectory**: 1. Determine root task is non-atomic and decompose into Task 1 (Retrieval: Search trends), Task 2 (Reasoning: Design outline), and Task 3 (Composition: Write sections). 2. Set Task 3 to SUSPENDED until Task 1 and 2 are SILENT. 3. Execute Retrieval, outputting exact facts. 4. Recursively update the Writing task's goal based on Retrieved data.
* **Real Answer**: A DAG-based execution plan where 'Search' results inform a 'Thinking' outline, spawning specific 'Writing' nodes executed only when prerequisites resolve.
* **Why this demonstrates the capability**: This illustrates typed, recursive task decomposition. The agent treats the project as a state-based dependency graph, breaking tasks down by cognitive type (Retrieval vs Composition) and dynamically unblocking downstream nodes as data is gathered.

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
