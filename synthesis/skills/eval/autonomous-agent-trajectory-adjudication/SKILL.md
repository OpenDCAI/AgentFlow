---
name: autonomous-agent-trajectory-adjudication
description: Use this skill when evaluating an autonomous agent's or multi-agent system's full multi-step trajectory in any environment (CLI, Web, GUI, or team-based role pipelines), focusing on terminal outcomes, step-level correctness, and environmental grounding. Trigger it when users say things like 'check if the server repair worked', 'trace where the error started in the pipeline', 'assign blame for the team failure', 'verify the GUI agent's clicks', or 'score the step-by-step progress of the browser bot'. It covers verifying system states (metrics, status codes, screenshots), detecting harmful side effects, penalizing inefficient reasoning loops, and tracing 'Error Origins' or 'Repair' events across sequential multi-agent or environment handoffs.
---

# Skill: autonomous-agent-trajectory-adjudication

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability involves the holistic adjudication of autonomous and multi-agent trajectories by evaluating terminal outcome success (ORM) and step-level process correctness (PRM). It assesses whether single agents or multi-agent pipelines successfully transition software environments (OS, Cloud, Web) or discrete deductive states into a target goal safely. The evaluator must ground judgments in external evidence (telemetry, bash logs, system screenshots) or verifiable text handoffs, quantifying 'Repair Rates' and 'Harm Rates' across stages to identify the precise 'Error Origin' (t*) where a task diverged from the optimal path.
* **Dimension Hierarchy**: Agentic Process & Outcome Evaluation->Autonomous Interaction Adjudication->autonomous-agent-trajectory-adjudication

### Real Case
**[Case 1]**
* **Initial Environment**: A distributed microservice environment (Online-Boutique) where a 'CPU Saturation' failure has been injected into the 'cartservice' component, causing high load and performance degradation.
* **Real Question**: Does the agent's proposed remediation successfully restore the system to a healthy state?
* **Real Trajectory**: The agent first attempts to scale replicas (kubectl scale), which fails to provide relief. It then reflects on 'CPU limits' vs 'CPU requests' metrics. It issues a new command: 'kubectl set resources deployment/cartservice --limits=cpu=1000m'. The evaluator validates the CPU metrics of 'cartservice' post-execution and observes utilization has returned to a safe range (<80%).
* **Real Answer**: SUCCESSFUL REMEDIATION. The agent successfully reflected on metrics to execute a target root-cause fix.
* **Why this demonstrates the capability**: This case demonstrates terminal outcome-based adjudication (ORM) in a CLI ecosystem. The judge ignores the agent's initial failed attempt but identifies that the second, reflective step targeted the root cause revealed by the metric probe, proving outcome success over blind instruction following.
---
**[Case 2]**
* **Initial Environment**: An Ubuntu desktop environment with LibreOffice Writer open. A document is present with several lines of text. The user instruction is: 'Apply a strike-through effect to the first sentence of the second paragraph.'
* **Real Question**: Evaluate the success of the agent's trajectory based on the final terminal screenshot.
* **Real Trajectory**: The agent scrolls to the second paragraph, uses the mouse to highlight the text, and clicks the 'Strike-through' icon. However, the visual log reveals the highlight missed the final punctuation mark and the last word of the sentence. The agent reports 'Task completed.'
* **Real Answer**: FAILED (Instruction Inconsistency). The visual bounding box missed the targeted text constraint.
* **Why this demonstrates the capability**: This case illustrates 'Visual Understanding' limits for GUI adjudication. The evaluator must detect that while the correct tool was selected, the exact visual state transition was incomplete (missing boundary characters), proving that superficial tool usage tracking does not equate to task success.
---
**[Case 3]**
* **Initial Environment**: A multi-agent system solving a complex logic pipeline across dedicated conversational roles (Planner -> Executor -> Critic).
* **Real Question**: Trace the execution and assign accountability for the trajectory's outcome.
* **Real Trajectory**: The evaluator tracks the output through the stages against the ground-truth goal. It notes the Planner and Executor both derived the correct intermediate answer initially. However, the Critic role reviewed the work and incorrectly altered the answer based on a flawed heuristic. The evaluator marks this as a 'Harm' event.
* **Real Answer**: Final Result: Incorrect. Error Origin: CRITIC. Event Detected: Critic Harm. The Critic corrupted a previously correct state established by upstream agents.
* **Why this demonstrates the capability**: This demonstrates step-level Process Reward Modeling (PRM) applied to pipeline handoffs. The evaluator accurately attributes blame by tracking correctness transitions across state handoffs, pinpointing exactly where the trajectory diverged from the ground-truth optimal path.

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
