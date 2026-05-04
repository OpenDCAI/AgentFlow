---
name: parallel-multi-tool-dag-orchestration
description: Use this when the user wants to optimize planning latency by running multiple independent tool calls at once, and dynamically fixing or reorganizing the plan if a part fails. Trigger it for requests like 'find information on several things simultaneously', 'build this project by coordinating parts in parallel', 'create a dependency graph for these tasks', or 'speed up the workflow and adjust if tasks fail.'
---

# Skill: parallel-multi-tool-dag-orchestration

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to decompose a high-level objective into a Directed Acyclic Graph (DAG) of executable tasks, identify parallelizable tool operations, and dynamically restructure the graph (adding or removing subtasks) based on real-time execution feedback to resolve bottlenecks or failures.
* **Dimension Hierarchy**: Open-World Real-World Planning->Information-Grounded Plan Construction->parallel-multi-tool-dag-orchestration

### Real Case
**[Case 1]**
* **Initial Environment**: An agent equipped with a web search tool and a symbolic math engine. The environment allows for asynchronous execution of multiple independent tool calls simultaneously.
* **Real Question**: How much does Microsoft's market cap need to increase to exceed Apple's market cap?
* **Real Trajectory**: The agent identifies that the market caps for Microsoft and Apple are independent data points. It generates a plan with two parallel search tasks: $1 = search('Microsoft market cap') and $2 = search('Apple market cap'). It then creates a third dependent task: $3 = math('$2 - $1'), using placeholder variables to wait for the search results. Finally, it uses $4 = finish() to aggregate the result.
* **Real Answer**: A plan structure equivalent to: [Task 1: Search(MSFT), Task 2: Search(AAPL)] -> Task 3: Math(Sub($2, $1)).
* **Why this demonstrates the capability**: This demonstrates DAG orchestration because the agent recognizes that the first two searches can happen simultaneously (forking), while the final calculation must wait for both outcomes (joining). It uses variables as futures to handle the data flow across parallel branches rather than blocking synchronously.
---
**[Case 2]**
* **Initial Environment**: A complex fact-checking environment where multiple search results must be filtered and then summarized. The agent has API access to massive state and private sector healthcare spending registries connecting over 200 candidates.
* **Real Question**: Which has higher total healthcare expenses, Florida or New York, considering both public and private sectors?
* **Real Trajectory**: The agent decomposes the query into four search tasks: $1 (FL Public), $2 (FL Private), $3 (NY Public), and $4 (NY Private), assigning them to run concurrently. It then plans two multi-variable join tasks: $5 = math('$1 + $2') and $6 = math('$3 + $4'). Finally, it performs an evaluation step $7 = math('$5 vs $6') upon all branch completions.
* **Real Answer**: It builds a fork-join-fork-join structure resulting in the mathematically verified state outcome contrasting Florida against New York total expenditures.
* **Why this demonstrates the capability**: This exhibits multi-level dependency orchestration where parallel operations serve nested sequential calculation gates. The planner orchestrates partial reductions of concurrent search branches into parallel sum sums before finalizing a singular logic block.
---
**[Case 3]**
* **Initial Environment**: A multi-agent coding environment building a complex software repository. The project has decoupled software requirements like UI mockups versus backend AI modeling that can logically be separated, but failures are common.
* **Real Question**: Create a Python Gobang game complete with a user interface rendering loop and a basic AI opponent engine.
* **Real Trajectory**: The agent initiates subtasks for UI design and AI implementation in parallel. After the first parallel execution round, the 'Implement AI' subtask yields empty or corrupted logs due to an unhandled logic error, while the UI succeeds. Instead of ignorantly retrying the failed code block sequentially, the agent restructures the DAG by inserting a new 'Redesign AI constraints' subtask and a downstream 'Refined integration' buffer node.
* **Real Answer**: A running Python game where the AI logic was autonomously repaired and re-integrated into the concurrently built UI via a dynamic structural node injection.
* **Why this demonstrates the capability**: This demonstrates dynamic workflow refinement wrapped into execution scaling. The agent identifies a mid-execution branch failure and structurally re-engineers its active DAG map on the fly to bypass the issue, proving robust adaptive orchestration.

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
