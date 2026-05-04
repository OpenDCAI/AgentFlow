---
name: sentential-rephrasing-translation
description: Use this skill when the user wants translation data where the ask is phrased in an unusual sentence shape, such as an indirect request, a longer setup sentence, or a differently ordered instruction. Trigger it for requests like "say the same thing but in a more roundabout way," "people do not always ask in one short command," or "test whether the system still translates when the request is worded awkwardly but means the same thing."
---

# Skill: sentential-rephrasing-translation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to preserve translation behavior when the instruction is re-expressed through different sentence forms, discourse ordering, or indirect phrasing, while leaving its underlying meaning unchanged.
* **Dimension Hierarchy**: Robustness to Imperfect or Misleading Instructions->Prompt Perturbation Robustness->sentential-rephrasing-translation

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent is provided an English meeting reminder and a target language setting. The environment is intentionally simple so that any failure can be attributed to sentential rephrasing rather than terminology or discourse complexity.
* **Real Question**: I need the next line available for our French-speaking office, so please take it as it stands and give it back in French: "The meeting has been moved to next Tuesday at 9 a.m."
* **Real Trajectory**: The agent resolves the indirect request into a translation task, preserves the time expression semantically, and outputs only the French translation.
* **Real Answer**: La réunion a été reportée à mardi prochain à 9 h.
* **Why this demonstrates the capability**: The request is not phrased as a short imperative but as a longer conversational sentence. A brittle system may fail to map this discourse form to a translation action, whereas a robust one should. The case therefore isolates whether the model depends too strongly on one prompt template or can generalize across equivalent sentence formulations.

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
