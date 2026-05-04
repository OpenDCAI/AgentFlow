---
name: global-dag-topology-planning
description: Use this skill when the user wants the agent to create a complete map, blueprint, or flowchart of actions before doing anything. It should be triggered by layman phrases like 'plan the whole process at once,' 'show me the arrows between the tools,' 'don't just guess step-by-step,' 'make a flowchart of the dependencies,' or 'give me a global plan for this complex request.' This is specifically for situations where tasks have nested logic or multiple parallel paths that need to be understood as a Directed Acyclic Graph (DAG) to avoid getting stuck in local loops or missing the big picture.
---

# Skill: global-dag-topology-planning

## 1. Capability Definition & Real Case
* **Professional Definition**: Global DAG topology planning is the capability to architect a complete, non-linear execution plan for complex queries by representing tools as nodes and data dependencies as edges within a Directed Acyclic Graph (DAG). Unlike reactive, incremental frameworks that make decisions one step at a time, this capability generates a holistic map of the entire problem space in a single pass, enabling optimized parallelism and resolving 'local optimization traps.' It focuses on the structural accuracy of both tool selection (node prediction) and the causal relationships between them (edge prediction) to ensure the final workflow is logically consistent, acyclic, and globally efficient.
* **Dimension Hierarchy**: Workflow Orchestration->Dependency and Schedule Management->global-dag-topology-planning

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-tool workspace including academic search engines, biographical databases, astronomical data tools, and date-calculators. Each tool has a clear input/output schema, and some tools can run in parallel while others have strict prerequisites.
* **Real Question**: Find the director of the 1969 film 'The Blue Marble', find out what major space-themed award they won, and then for every year that award was given to anyone between 1970 and 1975, check if the celestial alignment of Mars was visible from London.
* **Real Trajectory**: The planner first identifies the 'Director Lookup' tool as the root node. It then establishes a dependency edge from the director's identity to a 'Biographical Award Search' tool. Next, it generates a parallel set of nodes for the years 1970-1975, each calling a 'Celestial Visibility' tool. It links the award-recipient list output to the input parameters of the visibility checkers, ensuring all nodes are connected in a multi-level DAG without any circular loops. This global topology is output before any API tool is actually invoked.
* **Real Answer**: Director found: [Name]. Award: [Award]. Visibility check for 1970-1975: [Results per year].
* **Why this demonstrates the capability**: This case demonstrates global DAG planning because the complexity of nested logic (finding the award first) combined with parallel logic (checking visibility for multiple years separately) cannot be solved effectively via step-by-step guessing. It requires the agent to model the entire flow of data—from the film to the director to the awards and finally to the separate visibility checks—as a single coherent graph where the 'edges' represent the necessary information hand-offs.
---
**[Case 2]**
* **Initial Environment**: A workspace containing financial market tools, news aggregators, and email clients. The user wants to perform a multi-target analysis that involves both sequential and parallel operations across different servers.
* **Real Question**: Analyze the quarterly earnings of NVDA, AMD, and Intel, search for any concurrent geopolitical news that affected the semiconductor industry on those specific earnings dates, and then create three separate folders in my drive named after the company and move the corresponding summaries there.
* **Real Trajectory**: The orchestrator generates a DAG with three parallel branches: one for each company. Each branch begins with an 'Earnings Retrieval' node, followed by a 'News Search' node that depends on the retrieved earnings date. Finally, the three branches merge into a 'Folder Creator' and 'File Mover' set of nodes. The orchestrator ensures that the News Search node does not execute until the specific Earnings Date artifact is available, preserving the dependency topology.
* **Real Answer**: Analysis complete for NVDA, AMD, and Intel. Folders created and files moved according to the global schedule.
* **Why this demonstrates the capability**: This demonstrates the capability by creating a multi-level execution structure where parallel data gathering (the three companies) and serial dependency (Date -> News) coexist. The agent must successfully predict the edges (links between Date and News) for all three branches simultaneously to ensure the system doesn't waste time or miss geopolitical context.

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
