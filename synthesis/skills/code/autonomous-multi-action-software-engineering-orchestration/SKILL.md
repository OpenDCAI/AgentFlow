---
name: autonomous-multi-action-software-engineering-orchestration
description: Use this skill when the task requires orchestrating a complex, multi-stage engineering lifecycle to develop advanced features across diverse and esoteric scientific/engineering domains. Trigger it for requests like 'implement this Verilog hardware module', 'automate the MOOSE multiphysics modeling of a fuel assembly', 'convert these game rules into an executable Python world simulator', or 'build a formally verified Lean algorithm'. It universally covers objectives requiring translation of specific domain constraints into specialized logic, iterative compilation/simulation, and managing state across multiple files.
---

# Skill: autonomous-multi-action-software-engineering-orchestration

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to autonomously orchestrate diverse engineering work units into a dynamic, goal-oriented workflow across highly divergent paradigms (e.g., Finite Element Method simulations, partial-observable World Model synthesis, Hardware RTL, Formal Verification, Social Robotics). This involves parsing highly specialized domain rules or framework API documents, decomposing tasks into specialized components, executing in domain-specific simulation engines (e.g., MOOSE, CocoTB, Theorem Provers), and iteratively refining implementations via residual logs or state observation checks.
* **Dimension Hierarchy**: Repository Maintenance and Repair->Complex Software Feature Engineering->autonomous-multi-action-software-engineering-orchestration

### Real Case
**[Case 1]**
* **Initial Environment**: A cloud-based engineering environment with a MOOSE multiphysics solver binary, a target 16-sided prismatic fuel assembly mesh file (assembly.e), and a knowledge base of simulation components.
* **Real Question**: Solve for the thermal and mechanical performance of the prismatic fuel element. Set the heat flux on the inner boundary to 5e5 W/m^2, and fix the displacement at the bottom nodeset.
* **Real Trajectory**: The agent searches the knowledge base to identify requisite HeatConduction and SolidMechanics kernels. It drafts the MOOSE input card (.i file), explicitly mapping the [Mesh] boundaries to Dirichlet/Neumann conditions. Execution yields a parameter syntax error; the agent consults documentation, surgical edits the block, and re-executes. It verifies physical correctness by monitoring the L2-norm residual decay in the terminal logs.
* **Real Answer**: An iteratively verified multiphysics MOOSE input file that successfully models thermal expansion without solver or convergence errors.
* **Why this demonstrates the capability**: Shows translation of high-level physics requirements into specialized Domain Specific Language (DSL) execution logic, utilizing a solver's residual feedback to iteratively resolve nonlinear convergence states.
---
**[Case 2]**
* **Initial Environment**: A hardware repository containing a skeleton 'sorting_engine.v' (Verilog) and a CocoTB-based Python simulation harness. The target is cycle-accurate Register-Transfer Level (RTL) code.
* **Real Question**: Implement a sequential brick sort module in Verilog that handles N 8-bit elements. The system must meet strict cycle latency constraints.
* **Real Trajectory**: The agent inspects port constraints and implements a Finite State Machine (FSM) utilizing non-blocking datapath assignments. It executes the CocoTB testbench and encounters a 'Timing Violation' log. Identifying a critical path in the swap logic, it updates the clock-edge registers and re-runs the simulation, validating the logic against the functional golden model.
* **Real Answer**: A functional, synthesized Verilog module where the FSM correctly manages data phases within cycle-accurate precision, natively verified by the hardware simulator.
* **Why this demonstrates the capability**: Illustrates domain-specific orchestration where the agent must adapt to low-level hardware constraints and iteratively debug based on timing verification traces.
---
**[Case 3]**
* **Initial Environment**: A repository with rules defining an incomplete-information card game, alongside empirical trajectory logs displaying player 'action-observation' pairs.
* **Real Question**: Develop a grounded executable world model (Python simulator) for this game that encapsulates transition dynamics and includes an inference function mapping observed state sequences to hidden representations.
* **Real Trajectory**: The agent analyzes the text rules to formulate transition logic and cross-references trajectory variables to ensure state fidelity. It implements a stochastic inference function, then utilizes an inference-to-observation replicator check, determining if its inferred hidden deck state actually produces the observation found in the log. It iterates until the simulation models match empirical logs perfectly.
* **Real Answer**: An integrated simulation engine containing both environment transition rules and a latent state inference sampler aligned perfectly with trajectory records.
* **Why this demonstrates the capability**: Tests the ability to synthesize executable 'world models' bridging English rule-sets and empirical trace data, requiring heavy constraint alignment and domain feature abstraction.

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
