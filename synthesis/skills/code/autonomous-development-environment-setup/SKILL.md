---
name: autonomous-development-environment-setup
description: Use this skill when you need to resolve complex execution states: setting up environments from scratch, automating System Administration via shell scripts, or resolving project installations. It is ideal for requests like 'build a reproducible Dockerfile for this repo', 'fix the broken installation dependency errors', 'write a bash script to fetch remote files, assign permissions, and log output', or 'automate this server management task'. This skill tests the agent's ability to orchestrate multi-step Bash commands, handle version conflicts, verify system changes, and synthesize portable runtime execution environments cleanly.
---

# Skill: autonomous-development-environment-setup

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to autonomously bridge static codebases to reliable executable deployment states through intensive Linux/Unix system administration and iteration. This entails complex procedural decomposition using shell utilities (curl, sed, find), iterative package dependency and version conflict resolution (base-image swapping, waitlists), environment state recovery via snapshot rollbacks, and generating persistent executable automation artifacts (e.g. robust bash scripts or Dockerfiles) validated against rigorous test harnesses.
* **Dimension Hierarchy**: Repository Maintenance and Repair->Environment and Configuration Management->autonomous-development-environment-setup

### Real Case
**[Case 1]**
* **Initial Environment**: A Python repository containing a tool utilizing 'StrEnum' features requiring Python 3.11+. The default environment is heavily polluted and restricted to Python 3.10.
* **Real Question**: Configure the environment natively so the project can successfully run its unit test suite seamlessly.
* **Real Trajectory**: The agent observes a syntax incompatibility execution failure. Deducing version restrictions, it dynamically switches the target base image container execution tier. Running a clean slate package restore sequence sequentially checks for complex nested build conflicts before verifying test validity across all modules globally.
* **Real Answer**: A strictly validated, multi-stage reproducible Dockerfile invoking the updated python:3.11 environment resolving all dependency hierarchies.
* **Why this demonstrates the capability**: Ensures version-aware orchestration, enforcing the capacity to discard fundamentally flawed architectures dynamically rather than fruitlessly modifying broken parameters.
---
**[Case 2]**
* **Initial Environment**: A remote Linux server requiring administration workflow setup. The agent has networking enabled and standard utilities like curl, chmod, and grep installed.
* **Real Question**: Automate a script downloading an active remote asset repository, granting execution permissions, routing resulting error streams appropriately, and verifying the asset successfully integrated logging data into system paths.
* **Real Trajectory**: The agent breaks the task into logical primitives. It invokes curl -L for redirect routing, chmod +x for system permissions, writes the logic integrating output redirects ('||' and '>>') internally to handle intermittent command failures gracefully, and triggers an end-to-end verification check tracking physical local path population.
* **Real Answer**: An idempotent shell script flawlessly sequencing remote fetching, access rights adjustments, and log redirection validating correct administration.
* **Why this demonstrates the capability**: Illustrates foundational command-line execution resilience. The agent synthesizes robust chaining constructs across bash elements verifying specific configuration results natively mimicking highly capable DevOps orchestration.

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
