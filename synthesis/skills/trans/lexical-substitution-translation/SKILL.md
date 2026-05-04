---
name: lexical-substitution-translation
description: Use this skill when the user wants the translator to handle everyday wording changes like "turn this into French," "render this in Arabic," or "put this into Spanish" instead of a canonical "translate" instruction. Trigger it when the user says things like "people ask in different words," "use casual phrasing instead of textbook phrasing," or "make sure the system still gets the job when the wording changes but the meaning stays the same."
---

# Skill: lexical-substitution-translation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to execute a translation request when key instruction words are replaced by synonyms, near-synonyms, or lay alternatives that preserve task intent but change the lexical surface of the prompt.
* **Dimension Hierarchy**: Robustness to Imperfect or Misleading Instructions->Prompt Perturbation Robustness->lexical-substitution-translation

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent is given an English customer-support sentence and a simple preservation rule for a product name. The environment contains no ambiguity about the source text, so the challenge is entirely whether the agent understands lexical variation in the instruction.
* **Real Question**: Please render the following note in Italian and leave the product name unchanged: "SmartFit Premium now includes offline workout tracking."
* **Real Trajectory**: The agent maps "render ... in Italian" to a translation request, protects the product name, and outputs a faithful Italian sentence with no extra commentary.
* **Real Answer**: SmartFit Premium ora include il monitoraggio degli allenamenti offline.
* **Why this demonstrates the capability**: Nothing in the instruction uses the most literal task verb, yet the intended operation is still translation. The system must recognize synonymy at the instruction level and avoid treating the request as summarization or style editing. Because the product name is protected, the case also checks that lexical flexibility in the prompt does not weaken literal preservation rules.

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
