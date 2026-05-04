---
name: embedded-instruction-resistance
description: Use this skill when the user wants translation data where the source text looks like an instruction and may tempt the model to do the wrong job, such as solving a math problem, answering a question, or writing code instead of translating. Trigger it for requests like "make sure it translates the problem instead of solving it," "the input itself looks like a command," or "test whether it can ignore fake instructions inside the text being translated."
---

# Skill: embedded-instruction-resistance

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to translate source content faithfully when the source text itself resembles an instruction, a question, a code task, or another action-inducing prompt, without obeying or solving the embedded content instead of translating it.
* **Dimension Hierarchy**: Robustness to Imperfect or Misleading Instructions->Instruction Disentanglement->embedded-instruction-resistance

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent is given a translation request and a source passage that contains a math word problem. The agent has no external calculator or solver because the desired output must remain aligned to the source text rather than produce a solution.
* **Real Question**: Translate the following input text into Chinese and return only the translation: "At a school, 40% of the students receive a free lunch. If it costs $210 to feed 50 students, how much does each paying student pay for lunch?"
* **Real Trajectory**: The agent identifies that the outer instruction is translation, recognizes the inner text as content rather than an executable task, and outputs a Chinese translation of the full problem without solving it.
* **Real Answer**: 在一所学校里，40%的学生享受免费午餐。如果为50名学生提供午餐的费用是210美元，那么每名付费学生的午餐费用是多少？
* **Why this demonstrates the capability**: The source passage strongly invites reasoning, and many general LLMs drift into solving the problem instead of translating it. This example therefore isolates whether the agent can preserve instruction hierarchy and keep the source text source-aligned. It is especially valuable because the incorrect behavior can look superficially competent while still violating the user’s actual intent.

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
