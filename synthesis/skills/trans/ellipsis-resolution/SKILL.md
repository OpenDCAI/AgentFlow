---
name: ellipsis-resolution
description: Use this skill when the user wants translation data with short replies, subtitles, or conversational fragments where part of the meaning is missing unless you read the previous line. Trigger it for requests like "the second sentence leaves words out," "the answer is elliptical," or "test whether the translator can fill in what is omitted from context instead of translating the fragment too literally."
---

# Skill: ellipsis-resolution

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to infer and restore omitted lexical material, predicates, or arguments when the source text uses ellipsis that is recoverable only from preceding discourse, and to express the completed meaning naturally in the target language.
* **Dimension Hierarchy**: Contextual and Constraint-Aware Translation->Discourse-Grounded Document Translation->ellipsis-resolution

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent receives a two-turn subtitle snippet in English-to-Spanish translation. The second line is elliptical and does not restate the object from the first line, so the output must recover it naturally.
* **Real Question**: Translate this dialogue into Spanish: "A: Did you finish the report? B: Already did."
* **Real Trajectory**: The agent reads the first turn, identifies that the omitted object in the second turn is "the report," recovers the full underlying meaning, and writes a natural Spanish reply.
* **Real Answer**: A: ¿Terminaste el informe? B: Sí, ya lo terminé.
* **Why this demonstrates the capability**: A literal rendering of the second turn can sound incomplete or unnatural if the omitted object is not restored in the target language. The example is minimal, but the necessary information lives outside the sentence being translated. It therefore tests genuine discourse reconstruction rather than simple sentence conversion.

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
