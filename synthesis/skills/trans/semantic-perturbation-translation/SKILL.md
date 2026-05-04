---
name: semantic-perturbation-translation
description: Use this skill when the user wants translation data with bigger but still meaning-preserving prompt changes, such as role prompts, extra setup language, or semantically equivalent rewrites that sound very different on the surface. Trigger it for requests like "wrap the ask in a role," "change the wording a lot but keep the job the same," or "see if it still translates when the instruction is semantically the same but phrased very differently."
---

# Skill: semantic-perturbation-translation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to preserve correct translation behavior under higher-level prompt alterations that keep the task semantics intact but introduce role framing, extra explanatory wording, or semantically equivalent reformulations that are farther from the original prompt surface.
* **Dimension Hierarchy**: Robustness to Imperfect or Misleading Instructions->Prompt Perturbation Robustness->semantic-perturbation-translation

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent receives an English marketing sentence, a target-language constraint, and a role-framed instruction. The source sentence is short and non-technical so the challenge lies in semantic prompt variation rather than source complexity.
* **Real Question**: You are acting as a localization specialist for a retail launch. Your responsibility here is not to explain the copy, but to deliver the same message naturally in Brazilian Portuguese: "Free shipping ends this Friday."
* **Real Trajectory**: The agent recognizes that the role frame does not change the underlying task, infers that only translation is required, and returns a Brazilian Portuguese sentence with no added explanation.
* **Real Answer**: O frete grátis termina nesta sexta-feira.
* **Why this demonstrates the capability**: The instruction is semantically equivalent to a standard translation request, but it arrives wrapped in extra role-setting language and a negated side instruction. A robust system must separate this added framing from the core operation and still produce a faithful translation. The case therefore tests deeper semantic stability rather than shallow token matching.

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
