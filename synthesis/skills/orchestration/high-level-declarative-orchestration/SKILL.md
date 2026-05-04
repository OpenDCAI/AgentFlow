---
name: high-level-declarative-orchestration
description: Use this skill when the user needs to achieve complex, long-horizon objectives that span multiple stages, hosts, or environments where low-level execution logs would overwhelm the agent. Trigger it for requests like 'plan at a high level,' 'decouple the plan from the execution,' 'use declarative macro-tasks instead of raw commands,' 'manage major milestones,' and 'handle complex deployments without getting bogged down in terminal logs.' It ensures the orchestrator focuses on 'what' to achieve conceptually while delegating the dense technical 'how' to localized scripts, external state trackers, or sub-agents.
---

# Skill: high-level-declarative-orchestration

## 1. Capability Definition & Real Case
* **Professional Definition**: High-level declarative orchestration is the capability to resolve long-horizon, multi-node objectives by decoupling strategic planning from technical execution. It involves formulating plans in terms of abstract, declarative systems-level tasks (e.g., 'Provision Node', 'Extract Schema', 'Pivot Segment') and utilizing external auxiliary services—such as environment state trackers or high-level abstraction frameworks—to manage state and context. This architecture prevents context window saturation (context bloat) that typically occurs when an agent attempts to process massive streams of low-level tool outputs directly, enabling reliable coordination across complex topologies like enterprise networks or major distributed software environments.
* **Dimension Hierarchy**: Workflow Orchestration->Iterative Planning and Refinement->high-level-declarative-orchestration

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-segment enterprise boundary encompassing external-facing nodes and an internal protected database network with multiple servers. The agent aims to navigate through these discrete nodes using an abstract mapping service.
* **Real Question**: Retrieve summary diagnostic data from all connected databases deep in the internal network, starting your navigation from the external gateway.
* **Real Trajectory**: The orchestrator issues a high-level `Scan_Environment` declarative task. Upon discovering the active nodes, it issues a `Pivot_To_Node` task rather than calculating explicit routing tables locally. After commanding a `Verify_Access` macro, it delegates the complexity of querying the databases by dispatching a parallel `Retrieve_Diagnostics` task-set. It completely offloads the hundreds of noisy API traces to the auxiliary state, only reading the final summary result into its context.
* **Real Answer**: Successful diagnostic retrieval from the internal database network executed via declarative, macroscopic pivots.
* **Why this demonstrates the capability**: This demonstrates decoupling the overarching multi-step trajectory from the dense, noisy shell output common in multi-host navigation. By utilizing macro-tasks, the orchestrator maintained strategic coherence without suffering context collapse from iterative system logs.
---
**[Case 2]**
* **Initial Environment**: An empty cloud provider workspace (e.g., AWS/GCP) where provisioning a resilient application typically requires executing hundreds of granular CLI commands to manually configure VPCs, IAM roles, and compute clusters.
* **Real Question**: Deploy a highly available, staging-grade application network with a replicated database and isolated private subnets.
* **Real Trajectory**: The orchestrator initializes an infrastructure task graph framework. Instead of manually invoking low-level commands like `aws ec2 create-vpc` and parsing extensive JSON outputs, it emits declarative macro-tasks: `Provision_VPC`, `Configure_IAM_Roles`, and `Deploy_Cluster`. The environment's execution layer processes the dense JSON files and merely loops back completion status IDs. The orchestrator effectively links these high-level IDs sequentially to fulfill the final load-balancer dependencies without ever seeing the granular code.
* **Real Answer**: Staging environment successfully provisioned across all essential modules and validated for active deployments.
* **Why this demonstrates the capability**: Cloud APIs typically drown standard agents in immediate token exhaustion. Relying on declarative macro-actions ensures the coordinator acts strictly as a strategic planner orchestrating independent modules without losing narrative control, shifting the 'how' reliably to the execution backend.

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
