---
name: terminology-consistency
description: Use this skill when the user wants translation data where a repeated term must stay the same across a whole document, such as product names, policy labels, medical terms, or recurring entities. Trigger it for requests like "keep the wording consistent across paragraphs," "do not rename the same thing every time," or "test whether the translator locks repeated terms instead of drifting between alternatives."
---

# Skill: terminology-consistency

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to maintain the same target-language rendering for repeated source terms, entities, and technical expressions across a multi-sentence or multi-paragraph document whenever discourse context requires lexical stability.
* **Dimension Hierarchy**: Contextual and Constraint-Aware Translation->Discourse-Grounded Document Translation->terminology-consistency

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent is given a three-paragraph English automotive note and a small glossary. The term "lane keeping assist" appears four times, and the downstream evaluation checks whether the same Chinese term is used every time.
* **Real Question**: Translate the following document into Chinese and keep repeated terminology consistent across the whole document. The phrase "lane keeping assist" appears several times in the source.
* **Real Trajectory**: The agent scans the full document before drafting, locks the repeated term to a single Chinese rendering, applies that choice in every paragraph, and then emits the final document translation.
* **Real Answer**: …车道保持辅助…车道保持辅助…车道保持辅助…车道保持辅助…
* **Why this demonstrates the capability**: The challenge is not sentence-local adequacy but document-level lexical stability. A system that translates each sentence independently may alternate between near-synonyms and still look locally plausible, yet fail the discourse requirement. This example therefore targets the exact kind of cross-sentence cohesion that only appears when the whole document is considered jointly.

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
