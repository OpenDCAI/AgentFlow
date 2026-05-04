---
name: referential-recovery
description: Use this skill when the user wants translation data that forces the system to trace who or what a pronoun ('he,' 'she,' 'they') or omitted subject refers to using context from previous sentences. Trigger it for requests like 'the subject is dropped,' 'pronouns are ambiguous,' or 'make sure pronouns don't rely on sexist stereotypes based on the person's job type.'
---

# Skill: referential-recovery

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to recover omitted, ambiguous, or distant discourse referents across sentence boundaries and render them correctly with proper morphological agreement in the target language. This explicitly tests for anti-stereotypical coreference resolution, ensuring that agents prioritize long-distance syntactic evidence (e.g., reading a distinct gendered pronoun chapters later) over statistical biases (e.g., defaulting stereotyped professions to a specific masculine or feminine norm).
* **Dimension Hierarchy**: Contextual and Constraint-Aware Translation->Discourse-Grounded Document Translation->referential-recovery

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent is given a short Japanese narrative paragraph in which the first-person subject is omitted and heavily implied through verbs. The target is English, requiring explicit pronouns.
* **Real Question**: Translate the following paragraph into English: "『かしこまりました』。すばやく箱を取り、レジでスキャンする。"
* **Real Trajectory**: The agent uses earlier discourse cues mapping social hierarchy to infer that the narrator is the working store clerk speaking in the first person. It resolves the omitted subject syntactically into an explicit 'I' clause with stable reference.
* **Real Answer**: "Right away." I quickly took the box and scanned it at the register.
* **Why this demonstrates the capability**: The source omits subjects entirely. Successful translation demands tracking multi-sentence discourse cues to extract the latent identity, preventing severe actor misassignment.
---
**[Case 2]**
* **Initial Environment**: A multi-sentence English paragraph where an occupation ('mechanic') is established early on, but the concrete gender-identifying pronoun ('she') only surfaces several sentences later, stressing distance-based bias resistance.
* **Real Question**: Translate the following passage into French: 'The mechanic looked at the engine. The tools were spread across the workbench. After a few minutes of inspection, she found the source of the leak.'
* **Real Trajectory**: The agent scans the full text context, identifies the pronoun 'she' separated by intermediate sentences, and anchors this back to the subject 'mechanic'. It defies the statistical occupational stereotype and deliberately outputs the feminine morphological forms ('La mécanicienne').
* **Real Answer**: La mécanicienne a regardé le moteur. Les outils étaient étalés sur l'établi. Après quelques minutes d'inspection, elle a trouvé la source de la fuite.
* **Why this demonstrates the capability**: This explicitly resolves distant coreference against gendered biases. Because statistical LLM limits default 'mechanic' to masculine forms, reading distant semantic cues to recover the specific gender marker is a high-capability grammatical necessity.

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
