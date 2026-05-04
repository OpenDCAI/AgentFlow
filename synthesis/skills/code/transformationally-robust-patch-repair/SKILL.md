---
name: transformationally-robust-patch-repair
description: Use this skill when the user wants bug-fix or security-fix data that stays the same in meaning but looks different on the surface, so the agent cannot rely on memorized code patterns. Trigger it for requests like 'make decontaminated repair tasks', 'generate bug fixes with renamed or refactored code', 'create harder unseen patching data', or 'give me semantically same but structurally different repair problems'. Do not use it for standard repair data where surface form can directly reveal the answer.
---

# Skill: transformationally-robust-patch-repair

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to repair a software defect or vulnerability when semantically equivalent code transformations such as identifier renaming or structure rewriting obscure superficial memorization cues, forcing the agent to generalize to underlying program logic.
* **Dimension Hierarchy**: Repository Maintenance and Repair->Repair Robustness->transformationally-robust-patch-repair

### Real Case
**[Case 1]**
* **Initial Environment**: A repository contains an authorization bug in a connection-check path, but variable names and helper ordering have been rewritten compared with a known historical version. Security tests still fail in the transformed repository.
* **Real Question**: Repair the permission gate so network actions are allowed only when the authorization predicate holds in the transformed code path.
* **Real Trajectory**: Reproduce the failing security test, trace the transformed control flow despite renamed identifiers, locate the missing or inverted permission condition, patch the logic, and rerun the transformed test suite.
* **Real Answer**: The transformed authorization path now enforces the correct permission restriction regardless of renamed variables and altered code structure.
* **Why this demonstrates the capability**: This demonstrates transformation-robust repair because the agent must recover semantic intent from a changed surface form. The challenge is not discovering a novel fix type, but recognizing the same logical flaw under presentation shifts that weaken memorization shortcuts.
---
**[Case 2]**
* **Initial Environment**: A bug in path normalization remains after the project has undergone helper extraction and control-flow reshaping. The issue text still describes incorrect handling of traversal-like inputs, but the surrounding code no longer resembles the original patch context.
* **Real Question**: Restore safe path normalization in the refactored codebase without relying on the original code layout.
* **Real Trajectory**: Inspect the refactored helper chain, compare where path components are normalized and validated, patch the semantically responsible helper, and rerun the failing normalization tests plus adjacent file-access regressions.
* **Real Answer**: The refactored implementation correctly normalizes and constrains path inputs, and the transformed tests now pass.
* **Why this demonstrates the capability**: The benchmarked capability is robustness to semantics-preserving transformation. The agent must reason over behavior and data flow rather than over exact token sequences, line positions, or memorized diffs.

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
