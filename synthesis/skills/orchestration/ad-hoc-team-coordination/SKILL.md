---
name: ad-hoc-team-coordination
description: Use this skill when the user wants an agent to lead a project involving a mix of people and other AI assistants that it hasn't met or worked with before. It should be triggered by casual requests like “put a team together for this,” “manage the human experts and the bots,” “coordinate the tasks for the new staff,” or “see who is available to help me finish this.” This skill focuses on figuring out the strengths and availability of new team members on the fly, assigning them tasks from a complex plan, and keeping the boss updated on progress. Example triggers: “manage the consultants and the in-house AI,” “find out what the new team members are good at,” and “keep everyone in the loop while you handle this project.”
---

# Skill: ad-hoc-team-coordination

## 1. Capability Definition & Real Case
* **Professional Definition**: Ad hoc team coordination is the orchestration capability to manage collaboration within dynamic teams where human and AI worker agents have heterogeneous, unmodeled capabilities and may join or leave the workflow without prior coordination or joint training. The orchestrator must autonomously perform real-time teammate modeling to infer skills and reliability, execute dynamic task allocation across a non-linear task graph (G), and maintain stakeholder communication to optimize multi-objective outcomes (cost, speed, quality) under non-stationary preferences (U).
* **Dimension Hierarchy**: Workflow Orchestration->Dependency and Schedule Management->ad-hoc-team-coordination

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-agent workspace contains a dynamic task graph for a 'Quarterly Report' project. The team currently includes one AI writer and one generalist market analyst. The stakeholder prioritizes 'Speed' (Weight: 0.8) initially, and a new human expert for 'Client Customization' is scheduled to join the workflow at T=15.
* **Real Question**: Generate an updated quarterly report for the client. Prioritize getting the first draft ready as fast as possible, but make sure the new expert reviews it as soon as they sign on.
* **Real Trajectory**: The manager agent first decomposes the goal into a set of parallel nodes: 'Market Data Harvest', 'Drafting Section A', and 'Drafting Section B'. It assigns the harvest task to the AI analyst and the drafting tasks to the AI writer to maximize speed. At T=15, the manager observes the 'Client Customization' expert joining the registry. It immediately pauses the final 'Report Assembly' node and creates a new 'Expert Review' dependency, assigning it to the human expert and informing the stakeholder that the timeline has been adjusted for quality.
* **Real Answer**: Quarterly report draft complete; currently undergoing review by the client customization expert as requested.
* **Why this demonstrates the capability**: This demonstrates ad-hoc teamwork because the agent managed the transition of a new teammate joining mid-workflow. It successfully identified the new expert's skill, modified the task graph (G) to include a review bottleneck, and communicated the strategic adjustment to the stakeholder, balancing the original speed objective with the emergent quality capability.
---
**[Case 2]**
* **Initial Environment**: A crisis management environment for a 'Global Product Recall' includes a crisis team (T=5) and a recovery specialist (T=25). The manager has 100 timesteps to coordinate regulatory notifications, consumer safety checks, and brand recovery.
* **Real Question**: Our product has a safety flaw. Assemble a team to handle the recall immediately, notify the regulators, and start the consumer alert process. Adjust the plan whenever new specialists join.
* **Real Trajectory**: The agent starts with a skeleton task graph focused on 'Initial Notification'. At T=5, it detects the arrival of the 'Crisis Team' and immediately delegates the 'Mass Regulatory Filing' tasks. When the agent uses 'Inspect' to check progress, it finds a bottleneck in 'Consumer Messaging'. At T=25, it allocates the 'Brand Recovery' tasks to the new 'Recovery Specialist', using a 'RefineTask' action to update the instructions with specific safety compliance metadata found in the environment's legal registry.
* **Real Answer**: Recall operational. All regulatory filings submitted by the crisis team; consumer alerts are being managed by the recovery specialist.
* **Why this demonstrates the capability**: This case highlights adaptive coordination in a high-stakes team churn scenario. The agent had to dynamically adjust its task assignments and graph structure based on the arrival of specialized workers, demonstrating the ability to bridge human-AI efforts under strict procedural and consumer-safety constraints.

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
