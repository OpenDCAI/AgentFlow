---
name: visual-front-end-bug-resolution
description: Use this skill when the user wants front-end or visual bug-fix data where the question depends on screenshots, diagrams, UI appearance, layout, styling, or rendered interaction behavior. Trigger it for requests like 'give me UI bugs with images', 'make website fixes that need looking at the screenshot', 'generate front-end tasks with CSS or rendering issues', or 'create visual JavaScript bug-fix data'. Do not use it for purely backend repository issues, general software debugging without visual evidence, or security-only vulnerabilities.
---

# Skill: visual-front-end-bug-resolution

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to resolve bugs in user-facing software where the problem statement or validation signal contains essential visual information, requiring the agent to connect screenshots, diagrams, render differences, or style expectations to the responsible front-end code changes.
* **Dimension Hierarchy**: Repository Maintenance and Repair->Issue-Driven Repair->visual-front-end-bug-resolution

### Real Case
**[Case 1]**
* **Initial Environment**: A JavaScript diagramming library includes an issue report with a rendered example where message flow labels are missing from a BPMN-style diagram. The repository contains renderer code, example assets, and a visual regression test harness.
* **Real Question**: Restore rendering of message element names on message flows in the diagram view.
* **Real Trajectory**: Read the issue and screenshot description, inspect the diagram element renderer and the message-flow label branch, compare how related labels are drawn, patch the omitted render call, and run the targeted rendering test plus the visual snapshot suite.
* **Real Answer**: Message element names are rendered again on message flows, matching the expected diagram output.
* **Why this demonstrates the capability**: The bug cannot be solved from text alone because the missing output is a visual property. The agent must interpret the rendered expectation, map it to the front-end rendering path, and validate the fix with execution-backed visual checks.
---
**[Case 2]**
* **Initial Environment**: A syntax-highlighting library includes a screenshot showing incorrect bracket highlighting in a class-inheritance context. The repo has lexer rules, theme mappings, and reproduction snippets.
* **Real Question**: Fix the bracket highlight color mismatch that appears inside class inheritance declarations.
* **Real Trajectory**: Open the reproduction snippet, inspect the tokenization and highlight assignment for inheritance syntax, compare bracket-scoping logic in nearby contexts, patch the token-class assignment, and rerun the highlight snapshot tests.
* **Real Answer**: Brackets in class inheritance contexts now receive the expected highlight category and match the intended rendered color behavior.
* **Why this demonstrates the capability**: This demonstrates the capability because the observable failure is a rendered mismatch rather than a textual exception. Correct resolution requires grounding the visual symptom in front-end parsing or styling code and then confirming rendered behavior.

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
