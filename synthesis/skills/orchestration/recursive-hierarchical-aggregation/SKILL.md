---
name: recursive-hierarchical-aggregation
description: Use this skill when the user provides a request involving a massive amount of data, logs, or dense, high-resolution artifacts (like a giant technical diagram) that are far too large or complex for a single context window. It is triggered by layman requests like "summarize all these hundreds of logs," "break this complex map down into bits," "make a summary of summaries," or "digitize this entire layout piece by piece." Trigger it for phrases such as "it's too much data to read," "get a bird's-eye view," "scan all the elements across the whole project," or "chunk everything up and tell me the main points."
---

# Skill: recursive-hierarchical-aggregation

## 1. Capability Definition & Real Case
* **Professional Definition**: Recursive hierarchical aggregation is the orchestration capability to manage high-volume, distributed context or structurally dense artifacts by decomposing the global workspace into manageable semantic chunks or spatial regions. It delegates specialized extraction to a first tier of sub-workers (leaf nodes) and recursively synthesizes their localized findings into higher levels of abstraction (root nodes). This 'divide-and-conquer' topology strictly addresses technical context-window and perceptual limitations, ensuring data completeness across heterogeneous sources without suffering from context loss, omission of localized details, or information decay.
* **Dimension Hierarchy**: Workflow Orchestration->Dependency and Schedule Management->recursive-hierarchical-aggregation

### Real Case
**[Case 1]**
* **Initial Environment**: A CloudOps multi-agent workspace contains 2,000 unread system notifications and 500 performance logs distributed across multiple cloud accounts, far exceeding the token limit of the standard LLM.
* **Real Question**: I am overspending this month. Give me a comprehensive summary of all happenings and overspending triggers across my entire account over the past 30 days.
* **Real Trajectory**: The orchestrator splits the 2,000+ notifications and logs into 10 manageable chunks. It dispatches parallel requests to 10 sub-agents to summarize each chunk for 'Cost Anomalies'. Once the 10 sub-summaries are returned, the orchestrator triggers a 'Summary of Summaries' step, feeding the 10 results into a primary synthesis agent, which identifies underutilized EC2 instances as the global issue.
* **Real Answer**: Overspending is detected primarily in EC2 usage (Total: $450); underutilized instances in the US-West-2 region are the main trigger. Recommendation: Stop the 5 instances with <5% CPU usage identified in the detailed logs.
* **Why this demonstrates the capability**: This case demonstrates recursive hierarchical aggregation because the massive data volume made a single-call analysis technically impossible. The orchestrator managed a tree-like reduction—moving from many raw logs to chunk-summaries, and finally to a single top-level insight.
---
**[Case 2]**
* **Initial Environment**: An industrial automation workspace features a high-resolution motherboard PCB (Printed Circuit Board) layout file that is too optically dense for a single vision model pass, alongside a suite of visual component diagnostic tools.
* **Real Question**: Scan the power management sector of this PCB, tell me the total count of capacitors, and identify if any show signs of thermal degradation based on surface markings.
* **Real Trajectory**: The orchestrator treats the PCB image as a root node and segments the board into distinct spatial zones. It isolates the 'Power Management' quadrant and recursively breaks it down into individual component clusters, dispatching a specialized vision expert to each sub-region. The local findings from each cluster (capacitor counts and defect flags) are then passed up the hierarchy, summed, and reviewed by a root agent to produce the final integrity report.
* **Real Answer**: Power management sector identified: contains 24 electrolytic capacitors. Visual analysis across all localized clusters confirms no thermal scorching or bulging in this quadrant.
* **Why this demonstrates the capability**: This extends the divide-and-conquer topology to modal boundaries, illustrating component-aware context management in a dense visual environment. By traversing down into localized sub-hierarchies (Power sector -> leaf clusters) and aggregating the outputs, the orchestrator successfully bypasses perceptual resolution limits.

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
