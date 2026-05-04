---
name: multi-layer-progressive-validation
description: Use this skill when the user wants an agent to work efficiently on long workflows without stopping to check every single small detail, but still requires a safety net to prevent cascading errors if upstream logic goes wrong. Trigger it for layman requests like “don't hover over the process at every step,” “just check the work at key milestones,” “make sure an early mistake doesn't snowball into a wrecked final report,” or “use a tiered system to catch mistakes.” This skill focuses on setting up fixed checkpoints for validation (inner loop) to save time, while maintaining a holistic pipeline review (outer loop) to detect if upstream contamination has ruined downstream metrics, allowing global restarts when necessary. Example triggers: “validate in batches to save credits,” “ensure the data flow is solid from start to finish,” “escalate to a global review if the local fix fails,” and “use milestone-based error checking.”
---

# Skill: multi-layer-progressive-validation

## 1. Capability Definition & Real Case
* **Professional Definition**: Multi-layer progressive validation (Prog-Act) is a non-linear verification strategy that replaces redundant, step-by-step tool validation with a dual-loop error detection and correction mechanism. The 'Inner Loop' performs localized fixed-point verification at specific checkpoints to resolve transient errors without breaking execution flow. The 'Outer Loop' acts as a global safety trigger that audits cascading execution logic and data invariants. It initiates a comprehensive plan revision when localized checks 'collapse' or when hidden upstream failures (e.g., semantic contamination, missing filters) threaten to fundamentally invalidate the holistic end-to-end pipeline integrity.
* **Dimension Hierarchy**: Trustworthy Execution->Verification and Resilience->multi-layer-progressive-validation

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-step automated scientific computing environment equipped with specialized toolkits for symbolic abstraction, parameter configuration, and numerical execution. The system manages a graph memory to track the flow of non-serializable runtime artifacts across different tools.
* **Real Question**: Solve the 2D Heat Equation for a square plate with constant boundary temperatures, optimize the neural network training parameters, and verify the final residual. Do not perform step-by-step verification; instead, only check the validity of the PDE setup once and the final convergence once.
* **Real Trajectory**: The planner generates a 5-step strategy: Abstract PDE, Define boundaries, Configure geometry, Initialize solver, Execute training. The executor bypasses verification for the first three setup steps to save time. At a fixed checkpoint after 'Initialization', the orchestrator performs an inner-loop validation, identifying a minor unit mismatch in the geometry. It triggers a localized fix, re-executing only the geometry tool. At the final checkpoint, the training residual is non-convergent. Realizing a local fix cannot solve this systemic issue, the outer-loop triggers, instructing the planner to overhaul the network architecture and restart from step 4.
* **Real Answer**: PDE solved. Initial inner-loop corrected a geometry unit error; outer-loop revised the network structure after initial convergence failure to achieve a 1e-4 residual.
* **Why this demonstrates the capability**: This demonstrates multi-layer validation by separating localized resource fixes from global strategy shifts. It avoids the overhead of checking every single tool call and instead uses intentional 'fixed-point' checkpoints and a tiered escalation strategy where a total plan restart is the last resort.
---
**[Case 2]**
* **Initial Environment**: A cloud-based infrastructure deployment environment tracking complex inter-tool dependencies using a directed graph where nodes represent server states and edges represent data flows.
* **Real Question**: Provision a complex VPC with isolated database subnets and a load balancer. Only validate the plan after every three major tools are used to keep latency low.
* **Real Trajectory**: The agent identifies two validation checkpoints. It executes VPC-CIDR and Subnet-Mask generation without stopping. At the first checkpoint, the inner loop detects a conflict in the IP range. It performs a localized fix by updating the mask parameter locally. At the second checkpoint, the load balancer fails to bind because the entire region is at capacity. The inner loop fails, triggering the outer-loop global plan revision to move the entire deployment to a different availability zone.
* **Real Answer**: Infrastructure provisioned. A local subnet conflict was resolved via the inner loop; a regional capacity failure triggered a global outer-loop migration.
* **Why this demonstrates the capability**: This highlights the 'Progressive Acting' aspect where validation frequency is reduced to milestones. Simple technical hiccups are handled without a full restart, while catastrophic environmental shifts trigger high-level strategy changes.
---
**[Case 3]**
* **Initial Environment**: A multi-layered Business Intelligence pipeline environment containing staging tables (raw ingestion), intermediate tables (business logic), and mart tables (executive metrics).
* **Real Question**: Analyze our Q3 sales pipeline health. I need to identify 'zombie' opportunities with zero activity in 30 days and calculate how much they inflate the revenue forecast. Make sure upstream errors don't corrupt the final summary.
* **Real Trajectory**: The agent skips per-row integrity validation in the staging phase to minimize token queries, passing data directly into the intermediate join logic. However, during the 'Mart' checkpoint review (outer loop), the orchestrator identifies an impossibly massive revenue inflation. Utilizing the dependency graph, it traces this semantic contamination backward, discovering that duplicated keys existed in the raw staging layer. It triggers a global pipeline revision to insert an upstream de-duplication filter prior to rebuilding the downstream analytical arrays.
* **Real Answer**: Analytical summary generated. Stale deals are inflating the forecast by $15M (Initial calculation divergence was caught by an outer-loop checkpoint; the pipeline was rolled back to staging to correct duplicate-key contamination).
* **Why this demonstrates the capability**: This illustrates the capability's mandate to police Cascading Failures. The orchestrator defers validation for efficiency, but when the global output violates semantic invariants, it successfully relies on the outer-loop to audit the lineage, isolate the upstream contamination, and rewrite the pipeline flow.

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
