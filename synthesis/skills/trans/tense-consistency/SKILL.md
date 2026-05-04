---
name: tense-consistency
description: Use this skill when the user wants translation data for stories, novels, or multi-sentence narratives where the timing of events (past, present, or future) must stay consistent across the entire text. It is triggered for plain-language requests like 'don't flip-flop between past and present tense,' 'make sure the story stays in the past,' 'test if the translator can handle a flashback properly,' or 'ensure the grammar matches the timing of the actions.'
---

# Skill: tense-consistency

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to maintain consistent narrative temporal frames and aspectual markers across multi-sentence or document-level translations, especially when moving from tenseless languages (like Chinese) to languages with explicit tense/aspect systems (like English). This ensures that temporal shifts—such as those found in dialogue, flashbacks, and inner monologues—are grammatically aligned with the established narrative perspective without unauthorized fluctuations.
* **Dimension Hierarchy**: Contextual and Constraint-Aware Translation->Discourse-Grounded Document Translation->tense-consistency

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent is provided with a two-sentence narrative segment describing a character's journey and subsequent morning routine. The source sentences use standard narrative Chinese, which lacks explicit morphological tense markers for 'past' or 'present.'
* **Real Question**: Translate the following passage into English as a story: 张骆宇穿越到了异世界，第二天早上，他拿着剑冲向了练武场。
* **Real Trajectory**: The agent identifies the source as a serialized fiction segment (web novel) which typically uses the narrative past in English. It recognizes the sequential relationship between 'traveling' and 'the next morning,' assigning a consistent past tense ('traveled', 'took', 'rushed') to all actions to preserve narrative coherence.
* **Real Answer**: Zhang Luoyu traveled to another world, and the next morning, he took his sword and rushed to the training ground.
* **Why this demonstrates the capability**: This demonstrates the capability to infer a stable narrative tense when the source is ambiguous. A failure mode would be 'tense-drifting' where the first action is past ('traveled') but the next morning is suddenly present ('takes 그의 sword'), which disrupts the reader's temporal immersion.
---
**[Case 2]**
* **Initial Environment**: The agent receives a complex narrative paragraph involving a character's current actions and a brief inner emotional reflection. The challenge is distinguishing the 'narrative time' of the action from the 'present state' of the thought.
* **Real Question**: Translate this into English, ensuring the timing of the events makes sense: 他静静地看着远方，心里明白这一切都已经结束了。
* **Real Trajectory**: The agent identifies the main action ('watching the distance') as the narrative present or past depending on context, then correlates the subordinate clause ('knowing it was over') to the same frame. It carefully selects the past tense for the narrative to ensure consistency with standard literary conventions.
* **Real Answer**: He looked quietly into the distance, knowing in his heart that it was all over.
* **Why this demonstrates the capability**: It tests the ability to handle 'Tense Cohesion' where secondary clauses must align with the primary narrative tense. Incorrect handling often results in 'is looking... was over,' creating a disjointed timeline that traditional metrics like BLEU often fail to penalize.

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
