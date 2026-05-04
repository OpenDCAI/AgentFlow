---
name: parallel-subtask-scheduling
description: Use this skill when the user wants examples about running several subtasks at once, such as “make it delegate independent work in parallel,” “test whether it knows what can be done simultaneously,” or “plan a response where several items are handled concurrently.” Trigger it for requests about concurrency, worker allocation, sharing a global constraint across multiple simultaneous workers, DAG-style plans, replanning after partial results, asynchronous promises, or situations where serial execution is correct but wasteful. Example triggers: “parallelize the easy parts,” “don’t make it do everything one-by-one,” “process all these independent entities together under the same budget,” and “give me realistic workloads with both parallel and dependent sync steps.”
---

# Skill: parallel-subtask-scheduling

## 1. Capability Definition & Real Case
* **Professional Definition**: Parallel subtask scheduling is the capability to detect which subtasks are semantically or functionally independent enough to be executed concurrently, dispatch them asynchronously without violating dependency constraints, and then rejoin their outputs into a coherent downstream plan. This includes the dual ability to avoid false parallelism when dependencies exist and to avoid unnecessary serialization when independence exists, leveraging 'asynchronous promises' and broadcasting shared global constraints to multiple concurrent workers to compress total completion time.
* **Dimension Hierarchy**: Workflow Orchestration->Dependency and Schedule Management->parallel-subtask-scheduling

### Real Case
**[Case 1]**
* **Initial Environment**: A question-answering environment exposes a Wikipedia-style search tool and a final aggregation channel. The user asks whether two people share the same nationality, and the answer can be reached only after independently retrieving information about both entities. Nothing in the task requires the two searches to happen in sequence.
* **Real Question**: Were Scott Derrickson and Ed Wood of the same nationality?
* **Real Trajectory**: The planner generates two independent search subtasks, dispatches them concurrently, waits for both search results, and only then runs the aggregation step that compares the returned nationalities and emits the final answer. It does not serialize the searches or repeatedly loop over the same entity once enough evidence is already available.
* **Real Answer**: Yes.
* **Why this demonstrates the capability**: This is a minimal but clean scheduling case because the orchestration challenge is to see the latent parallelism in the dependency graph. The answer is easy once both facts are available, but the benchmark differentiates agents that coordinate parallel work from agents that reason and act one step at a time. It therefore measures scheduling intelligence rather than raw factual knowledge.
---
**[Case 2]**
* **Initial Environment**: A multi-agent workspace contains geometry tools: a 'Coordinate_Extractor' (extracts x,y pairs from text) and a 'Formula_Specialist' (retrieves and explains geometric equations). The environment uses a promise-based orchestration protocol that allows for asynchronous tool dispatches combined with continuous text generation.
* **Real Question**: If the endpoints of a line segment are (2, -2) and (10, 4), what is the length of the segment?
* **Real Trajectory**: The agent identifies that 'determining the coordinates' and 'recalling the distance formula' are semantically independent sub-tasks. It issues asynchronous promises to both the Coordinate_Extractor and the Formula_Specialist simultaneously to run in parallel threads. While these agents work, the orchestrator begins drafting the solution's explanatory structure, and only issues a formal synchronization command to pause text generation when the gathered values must finally be plugged into the formula.
* **Real Answer**: 10
* **Why this demonstrates the capability**: This illustrates semantic decomposition via parallel promises, as the agent does not wait for the coordinates to be known before seeking the formula. It identifies that the 'what to do' and 'what to do it to' are independent threads of knowledge. By utilizing parallel background threads for data collection while writing unstructured text, it compresses total completion time.
---
**[Case 3]**
* **Initial Environment**: A multi-cloud deployment workspace containing specialized 'Provisioner' agents for Frontend (FE), Backend (BE), and Database (DB) modules. The environment includes a 'Budget Watcher' tool and an 'Organization Security Policy'.
* **Real Question**: Deploy my complete app stack to the production cluster. Make sure to stay within the monthly budget and apply the standard security headers to every instance.
* **Real Trajectory**: The orchestrator invokes the Budget Watcher and Security tools to retrieve the shared limits. It defines a global deployment context and dispatches a synchronous parallel request to the FE, BE, and DB provisioners, passing the budget and security requirements as shared constraints to all three threads simultaneously. It waits for all three specialists to return their configurations, ensures the aggregate cost is below the limit, and synthesizes a final manifest.
* **Real Answer**: App stack deployed to production: Instance-FE (ID: 4x21), Instance-BE (ID: 9j33), Instance-DB (ID: 2p11). Total cost: $14.50/day. Security headers applied.
* **Why this demonstrates the capability**: This proves parallel scheduling with shared global constraints. The orchestrator must broadcast a unified limitation to multiple concurrent subtasks and synchronize their varied results into a single consistent outcome, ensuring all parallel branches respect organizational policy.

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
