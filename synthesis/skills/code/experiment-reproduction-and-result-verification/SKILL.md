---
name: experiment-reproduction-and-result-verification
description: Use this skill when the user wants data where the agent must execute experiments, inspect logs and outputs, and judge whether the intended research results were reproduced. Trigger it for requests like 'generate reproduction verification tasks', 'make result-checking workflows', 'create reproduce.sh evaluation data', or 'give me code-agent tasks about running and validating research experiments'. Do not use it for first-pass paper-to-code implementation only.
---

# Skill: experiment-reproduction-and-result-verification

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to run, monitor, validate, and assess whether an implemented research codebase actually reproduces the empirical results or intermediate execution outcomes required by a benchmark or rubric.
* **Dimension Hierarchy**: Research Reproduction Engineering->Reproduction and Evaluation->experiment-reproduction-and-result-verification

### Real Case
**[Case 1]**
* **Initial Environment**: A repository includes implementation code, a reproduce.sh entrypoint, documentation, and a rubric describing what outcomes count as successful replication. Running the script generates logs, tables, and plots.
* **Real Question**: Execute the reproduction pipeline and determine whether the target experimental results have been successfully reproduced.
* **Real Trajectory**: Run reproduce.sh in a clean environment, inspect reproduce.log and generated outputs, compare observed artifacts against the required result criteria, and record which parts fully match, partially match, or fail.
* **Real Answer**: The reproduction run achieves some required outputs but misses others, yielding a structured assessment of execution success and result fidelity.
* **Why this demonstrates the capability**: This capability centers on verification after implementation. The challenge is interpreting empirical outputs against explicit criteria, not just producing code or running commands blindly.
---
**[Case 2]**
* **Initial Environment**: A partially complete research submission contains code development artifacts and a rubric with code, execution, and result-match requirements. The benchmark awards partial credit based on which requirements are satisfied.
* **Real Question**: Assess the submission by checking which implementation, execution, and result requirements are actually met after running the pipeline.
* **Real Trajectory**: Read the rubric, identify leaf requirements, run the provided scripts, inspect logs and outputs, and connect observed evidence to each requirement type before scoring the submission.
* **Real Answer**: The submission satisfies some code-development and execution requirements but only a subset of result-match requirements, leading to a partial replication score.
* **Why this demonstrates the capability**: The task demonstrates experiment reproduction and result verification because it requires evidence-based judgment over code, execution artifacts, and empirical outputs. The agent must distinguish having code from having runnable code, and runnable code from actually matched results.

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
