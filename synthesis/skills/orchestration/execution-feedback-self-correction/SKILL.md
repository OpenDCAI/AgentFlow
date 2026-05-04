---
name: execution-feedback-self-correction
description: Use this skill when the orchestrator encounters technical errors, hallucinated identifiers, or missing context that requires an autonomous debugging loop to fix. This is triggered by layman requests such as “fix the tool call,” “find why the simulation failed,” “repair the script it wrote,” “connect the dots if it crashes,” or “figure out why the database query is wrong.” It includes cases where the agent must read machine-readable tracebacks (like Python or SQL errors), detect technical mismatches (like 0-indexed vs 1-indexed systems), or correct how one sub-agent calls another agent's work. It also applies to long-duration scientific or industrial batch jobs where the agent must detect 'abnormal completion' or 'convergence failure' buried within massive output logs and trigger a workflow rollback to resubmit corrected tasks. Example triggers: “I want the agent to fix its own bugs,” “test if it can recover from a broken API call,” “debug the physics simulation failures,” “make the agent double-check its logic if the results look suspicious,” and “automatically restart the calculation if it gets stuck or fails to converge.”
---

# Skill: execution-feedback-self-correction

## 1. Capability Definition & Real Case
* **Professional Definition**: Execution-feedback self-correction is the orchestrator's capability to autonomously close the loop between execution and refinement by processing machine-readable feedback (logs, tracebacks, and status codes). For complex multi-agent systems, this extends to ‘Trace-Driven Logic Recovery,’ where the orchestrator interprets technical diagnostics—such as Python exceptions, SQL EXPLAIN errors, or missing completion markers in scientific batch logs—identifies the root cause, and dispatches specialized correction or research agents to remediate the code. Furthermore, it incorporates 'Workflow State Rollback,' a resilient protocol where the orchestrator identifies logical failures in long-horizon batch processes (e.g., non-convergent mathematical states) and reactively reverts the session state to a previous high-stability node to resubmit corrected parameters without user intervention.
* **Dimension Hierarchy**: Trustworthy Execution->Verification and Resilience->execution-feedback-self-correction

### Real Case
**[Case 1]**
* **Initial Environment**: A large-scale enterprise data lake containing millions of tables and a Knowledge Graph indexing up-to-date schema semantics, historical query logs, and business jargon. The environment includes a Query Writer Agent, a Validator equipped with a Trino-EXPLAIN mode, and a specialized Researcher LLM Agent with tools to search the Knowledge Graph metadata index.
* **Real Question**: What is the total click-through rate for our search notifications in the last 30 days? Use the 'notification_metrics' table.
* **Real Trajectory**: The Orchestrator dispatches the Query Writer, which generates a SQL query targeting a 'notification_metrics' table. The Validator runs a syntax check and returns a 'Table Not Found' error because 'notification_metrics' is an outdated synonym for the actual table 'search_notif_events_v2'. The Orchestrator identifies this as a hallucination error and dispatches the Researcher Agent, which queries the Knowledge Graph for tables similar to 'notification_metrics'. The Researcher retrieves the correct schema for 'search_notif_events_v2' and provides a recommendation. The Orchestrator then prompts the Query Fixer to rewrite the query with the validated metadata, resulting in a successful data retrieval.
* **Real Answer**: CTR for search notifications (v2): 4.12%
* **Why this demonstrates the capability**: This case demonstrates discovery-augmented self-correction. Success is not achieved by a simple retry; it requires the orchestrator to manage a multi-agent loop that interprets a machine error, executes a 'Research' sub-task to find the missing ground truth in an external index, and integrates that new context to salvage the plan.
---
**[Case 2]**
* **Initial Environment**: A complex scientific simulation workspace equipped with a physical system simulator (for water, power, or gas networks) and a specialized Python interface library. The simulator (back-end) follows a 1-based indexing convention for its system elements, while the Python interface (front-end) returns data in standard 0-indexed arrays.
* **Real Question**: Find the maximum flow rate at the junction with ID 'VALVE_01' during the simulated 24-hour period.
* **Real Trajectory**: The agent generates a Python script to retrieve 'Flow' for 'VALVE_01'. The execution fails with an 'IndexError' or returns a logical mismatch because the agent attempted to use the 1-based index directly in a 0-indexed array calculation. The orchestrator captures the Python traceback, identifies the 'Indexing' error, and consults its internal 'Modeling Tips' manual. It correctly identifies the off-by-one technical invariant, adjusts the code to subtract 1 from the index, and re-executes the simulation, reaching the correct flow value.
* **Real Answer**: Maximum flow at VALVE_01: 42.5 L/s.
* **Why this demonstrates the capability**: This demonstrates self-correction of domain-specific technical invariants. The orchestrator must bridge the gap between two conflicting technical standards (1-based vs 0-based) by interpreting a runtime error and mapping it back to a specific domain rule discovered in the technical documentation.
---
**[Case 3]**
* **Initial Environment**: A multi-agent development environment featuring a 'Generator Agent' that writes Python function definitions and a 'Caller Agent' that must generate a one-line command to evaluate those functions. The environment uses an isolated sandbox for execution.
* **Real Question**: Create a script to find the average water age at all demand junctions in our current network model.
* **Real Trajectory**: The Generator Agent defines a function named calculate_avg_age(d). However, the Caller Agent, in its attempt to execute it, generates the line get_water_age(d) based on a semantic guess. The execution fails with a 'NameError'. The orchestrator identifies the 'Signature Mismatch' error, compares the generated function definition with the evaluation command, discovers the naming discrepancy, and prompts the Caller Agent to use the correct function name. The corrected script then runs and returns the average age results.
* **Real Answer**: Average water age at demand junctions: 12.4 hours.
* **Why this demonstrates the capability**: This highlights self-correction of handoff specification errors in a multi-agent delegation chain. It proves the orchestrator can identify when the internal interface between its own specialized sub-workers is broken and surgically repairs the alignment to ensure end-to-end execution.
---
**[Case 4]**
* **Initial Environment**: An autonomous scientific research project for topological materials. The orchestrator manages a 'Material Property Computation Subsystem' utilizing a supercomputer cluster for Density Functional Theory (DFT) calculations via VASP. The architecture uses a LangGraph state machine tracking states (Planning, Selection, Action, Review) and a MongoDB persistence layer for fault tolerance.
* **Real Question**: Perform ab initio computational verification to classify the topological phase of the crystal structure SrSbO3.
* **Real Trajectory**: The CP Agent submits the DFT calculation files to the High Performance Computing (HPC) environment. During the subsequent monitoring turn, the Review (RE) Agent analyzes the OUTCAR output file and detects that it lacks the 'Normal termination' string, specifically identifying that the Self-Consistent Field (SCF) calculation failed to converge. Instead of terminating the session, the orchestrator triggers a 'Fault Recovery Protocol': it executes a workflow rollback to the 'Action' state, logs the convergence error, modifies the INCAR parameter file to adjust the mixing scheme, and autonomously resubmits the job to the cluster until a valid converged state is reached.
* **Real Answer**: Calculations complete: SrSbO3 is confirmed to be a topological crystalline insulator.
* **Why this demonstrates the capability**: This case demonstrates advanced scientific self-correction and state-machine resilience. The orchestrator identifies a high-stakes 'logical failure' buried in a multi-day execution log (lack of convergence) and utilizes a dedicated rollback mechanism to repair and resubmit the task without human intervention.

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
