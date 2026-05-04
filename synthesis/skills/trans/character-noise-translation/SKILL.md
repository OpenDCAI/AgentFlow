---
name: character-noise-translation
description: Use this skill when the user wants translation data for messy prompts with small spelling mistakes, broken typing, duplicated letters, swapped characters, or keyboard slips. Trigger it for plain-language requests such as "test whether it still translates when the ask has typos," "people type fast and miss letters," "make the prompt look slightly broken," or "check if the translator can survive misspellings without changing the task."
---

# Skill: character-noise-translation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to correctly infer and execute a translation request when the user instruction contains character-level corruption such as typos, character swaps, deletions, insertions, repeated letters, or capitalization noise, while the intended task and target language remain recoverable.
* **Dimension Hierarchy**: Robustness to Imperfect or Misleading Instructions->Prompt Perturbation Robustness->character-noise-translation

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent is given a clean English product update paragraph, a target language selector, and a preservation rule that URLs and email addresses must remain unchanged. No glossary is provided, so the main difficulty comes entirely from the damaged user instruction rather than from domain knowledge.
* **Real Question**: Trnaslate the folowing update into Germna and keeep the URL + email exactly as they are: "The SmartFit app launches on 05/15/2023. Read more at www.smartfit-tech.com or contact help@smartfit-tech.com."
* **Real Trajectory**: The agent normalizes the noisy instruction, infers that the intended task is English-to-German translation, identifies the protected substrings, and produces only the translated sentence while copying the URL and email verbatim.
* **Real Answer**: Die SmartFit-App startet am 15.05.2023. Mehr dazu unter www.smartfit-tech.com oder per E-Mail an help@smartfit-tech.com.
* **Why this demonstrates the capability**: The instruction is visibly corrupted at the character level, but the requested task is still recoverable by a robust translation system. The example tests whether the agent can repair the instruction internally without drifting into summarization, explanation, or format changes. It also checks that the agent does not treat the typo noise as permission to alter protected literals such as the URL and email address.

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
