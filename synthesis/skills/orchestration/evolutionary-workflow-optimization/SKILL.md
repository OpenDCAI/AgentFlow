---
name: evolutionary-workflow-optimization
description: Use this skill when the user wants to automatically improve how an agent works over several tries, such as “make the agent learn from its mistakes,” “let the system figure out the best prompt for this task,” “find the bottleneck in my current workflow,” or “give me examples where the agent restructures its own workflow to get better results.” Trigger it for requests about self-evolving agents, automated prompt engineering (TextGrad), structural workflow updates (AFlow), system self-red-teaming, or attributing performance gaps to specific models/components to optimize resource allocation. Example triggers include: “tune the instructions automatically,” “evolve the agent’s logic,” “figure out which model is best for the action part versus reasoning,” and “I want to see the system improve its prompt based on feedback.”
---

# Skill: evolutionary-workflow-optimization

## 1. Capability Definition & Real Case
* **Professional Definition**: Evolutionary workflow optimization is the meta-capability of an orchestration system to autonomously refine its own execution logic, prompt templates, interaction topologies, global safety constraints, and component assignments based on live performance signals and post-event outcome data. It involves integrating closed-loop optimization cycles to perform gradient-like updates to natural language instructions, search for optimal directed-graph (DAG) structures connecting agents, or conduct coalitional analysis (e.g., Shapley value attribution) to identify functional bottlenecks. Crucially, it includes an integrated learning and audit layer that performs reinforcement-based adaptation of decision policies and operational thresholds—effectively transitioning the system from static analytical prediction to adaptive decision intelligence.
* **Dimension Hierarchy**: Workflow Orchestration->Iterative Planning and Refinement->evolutionary-workflow-optimization

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-agent e-commerce workspace is configured with a four-stage workflow: Planning, Reasoning, Action, and Reflection. The system utilizes uniform baseline LLMs across all nodes but possesses an attribution analysis framework to optimize heterogeneous scaling.
* **Real Question**: Analyze the shopping workflow systematically. Quantify which component is the primary bottleneck for complex attribute matching, and reassign the optimal high-tier model only to that component to maximize success.
* **Real Trajectory**: The orchestrator executes a sequence of trial runs, systematically swapping components with high-tier models. Analysis reveals the 'Action' component (tool execution syntax) yields the highest marginal performance improvement, while upgrading 'Planning' offers negligible gains. The orchestrator structurally reconfigures the multi-agent pipeline, assigning the expensive high-tier model strictly to the 'Action' node and maintaining baseline models elsewhere.
* **Real Answer**: Optimal Configuration Applied: High-tier model assigned to the 'Action' component, which contributed 6x more to the success rate than other nodes during attribution analysis.
* **Why this demonstrates the capability**: This case exhibits attribution-informed resource scaling, extending evolutionary optimization beyond text and topology to heterogeneous resource allocation. By quantifying non-linear synergistic effects, the system surgically rectifies functional bottlenecks.
---
**[Case 2]**
* **Initial Environment**: A cloudburst response workspace includes specialized agents for Sensing, Forecasting, and Risk Triage. The current decision policy sets a 'Flash-Flood Warning' threshold at 100mm/h based on historical averages, and an 'Audit and Learning' agent monitors real-world outcomes.
* **Real Question**: Analyze the results of the 2025 Buner event where the system issued a 'Null' triage for a 90mm/h rainfall that subsequently caused a flash flood. Update the operational policy to prevent this gap.
* **Real Trajectory**: The Learning and Audit Agent ingests the post-event logs and real-world damage reports. It identifies that the current 100mm/h threshold resulted in a 'False Negative,' causing a delay in evacuation. It performs a Bayesian update to the decision policy, recalibrating the 'Critical Success Index' threshold to 80mm/h for mountainous regions. Finally, it reinforces the Triage Agent's prompt with this new situational constraint and validates it against the historical scenario.
* **Real Answer**: Operational policy evolved: Flash-flood triage threshold recalibrated from 100mm/h to 80mm/h for extreme orographic zones; Reliability improved from 0.86 to 0.93 through outcome-based reinforcement.
* **Why this demonstrates the capability**: This case demonstrates closed-loop reinforcement-based adaptation. The orchestrator doesn't just fix a technical error; it evolves its the internal 'Decision Policy' and operational thresholds based on physical performance signals (the outcome of a disaster) to achieve dynamic climate resilience.

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
