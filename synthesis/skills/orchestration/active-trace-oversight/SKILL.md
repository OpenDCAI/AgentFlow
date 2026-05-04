---
name: active-trace-oversight
description: Use this skill when the user wants to test if the agent can be monitored and corrected by an independent process during execution. It should be triggered by casual requests like “stop the agent if it starts looping,” “kill the task if it spends too much money,” “make sure it doesn't get stuck in a rabbit hole,” or “I want an overseer to watch the logs and intervene if the goal changes.” This capability handles concurrent monitoring using trajectory/call-graph analysis to detect stalls, infinite loops, objective-drift, or utilizing quantitative heuristics (e.g., free-energy/entropy signals tracking exploration decay) to dynamically override stuck agents. Example triggers: “detect if the agent is repeating itself,” “cancel the run if it's wasting time,” “provide steering hints if it gets lost,” and “use active inference to force the team out of local minima traps.”
---

# Skill: active-trace-oversight

## 1. Capability Definition & Real Case
* **Professional Definition**: Active trace oversight is the orchestration capability to utilize an independent, asynchronous monitoring process (Overseer) that analyzes real-time execution artifacts—including the callgraph, tool-call event streams, token entropy, and exploration heuristics—to identify pathological behaviors such as infinite loops, execution stalls, or semantic goal-drift. This allows the system to intervene in an ongoing execution by utilizing dynamic trajectory evaluations to inject policy updates or steering notifications into the context window, shifting the agent away from local minima (oscillations/dead-ends) and preserving goal integrity without hard timeouts.
* **Dimension Hierarchy**: Trustworthy Execution->Verification and Resilience->active-trace-oversight

### Real Case
**[Case 1]**
* **Initial Environment**: A self-improving agent environment contains a Main Agent managing a 'software_developer' sub-agent. A concurrent 'Overseer' process is configured to poll the execution trace every 30 seconds, with the ability to inject messages into the sub-agent's role or terminate its session.
* **Real Question**: Optimize the agent's internal 'SmartEditor' tool to reduce token consumption during file overrides.
* **Real Trajectory**: The software_developer agent attempts to install a new dependency but enters an infinite loop because the environment has a locked version conflict, causing it to repeat 'pip install' four times. The Overseer process analyzes the event stream, detects the repetitive tool-calling pattern, and issues a 'force_cancel_agent' command, notifying the Main Agent that the installation failed due to a loop.
* **Real Answer**: The looping sub-agent is successfully terminated; the Main Agent pivots and tries a non-installation-based optimization.
* **Why this demonstrates the capability**: This demonstrates trace oversight as the intervention was driven by a concurrent process observing a 'pathological behavior' that the primary agent was unable to self-detect. It grounds oversight on trace-stream redundancy.
---
**[Case 2]**
* **Initial Environment**: A multi-agent RAG system includes a 'Searcher' worker and a 'Supervisor' process. The environment monitors API costs and token usage globally in real-time.
* **Real Question**: Search for all existing legal precedents regarding AI-generated copyright in every jurisdiction available.
* **Real Trajectory**: The Searcher agent begins spawning hundreds of parallel sub-queries, exhausting the token budget rapidly. The Supervisor agent observes the Global Trace Progress and identifies that the cost-per-minute has exceeded safety thresholds. It injects a <STEERING_HINT> into the Searcher's context, ordering it to narrow the scope to G7 countries. The Searcher acknowledges and halts auxiliary searches.
* **Real Answer**: Execution continues with a refined, cost-efficient scope as dictated by the supervisor.
* **Why this demonstrates the capability**: This highlights 'steering notifications'. The supervisor evaluates global artifact progression against structural considerations preventing a total execution crash, proving active course-correction capability.
---
**[Case 3]**
* **Initial Environment**: A large-scale multi-database environment where an exploration agent evaluates diverse tables. An overseer logs the exploration paths and calculates algorithmic efficiency tracking 'repeat vs novel' actions.
* **Real Question**: Perform a deep search across the system to find the fragmented financial reports hidden across various sub-directories.
* **Real Trajectory**: The primary agent enters a structural loop in a highly nested irrelevant folder, making moves with 0 information gain (revisiting the same sub-folder levels repeatedly). The Overseer actively monitors this loss of 'exploration velocity', diagnoses a local minima stall, and intervenes by injecting a command to 'abandon the current branch and backtrack to root'.
* **Real Answer**: Target data discovered after the overseer broke the structural exploration loop and forced the agent down a novel directory path.
* **Why this demonstrates the capability**: Shows active trace oversight using quantitative/algorithmic heuristics (such as exploration decay, entropy stalls, or active-inference scores) to actively pull an agent out of an endless execution cycle.

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
