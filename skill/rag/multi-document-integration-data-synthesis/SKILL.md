---
name: multi-document-integration-data-synthesis
description: Use this skill when the user says things like 'questions that need two or three docs together', 'split the answer across sources', 'make the model combine facts', or 'force it to read more than one passage'. Trigger it whenever the answer should only emerge after combining complementary evidence from multiple retrieved documents.
---

# Skill: Multi-Document Integration

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to assemble a correct answer whose required information is distributed across multiple documents, with no single document sufficient on its own. The agent must accumulate complementary evidence slots and then synthesize them into one coherent answer.
* **Dimension Hierarchy**: Multi-Source Evidence Composition->Cross-Document Synthesis->Multi-Document Integration

### Real Case
**[Case 1]**
* **Initial Environment**: A bounded current-events bundle in which one document states the launch date of the ChatGPT iOS app and another states the launch date of the ChatGPT API. No single passage contains both dates together.
* **Real Question**: When were the ChatGPT app for iOS and ChatGPT api launched?
* **Real Answer**: May 18 and March 1.
* **Why this demonstrates the capability**: The answer requires collecting two distinct slots from separate documents and emitting them in one response. A model that reads only one source will necessarily produce an incomplete answer. The capability is therefore true cross-document integration rather than single-hop extraction.
---
**[Case 2]**
* **Initial Environment**: A bounded Wikipedia article set about film music, awards, and directors. One article identifies a year in Hans Zimmer’s Grammy history, another identifies the film tied to Michael Bay’s first musical score, and the answer appears only after joining both constraints.
* **Real Question**: I am thinking of a movie where Hans Zimmer won a Grammy Award for his work. He won the Grammy award the same year that he did his first musical score for film director Michael Bay. Can you please tell me the name of that movie?
* **Real Answer**: Crimson Tide
* **Why this demonstrates the capability**: The question cannot be solved by retrieving one fact in isolation. The model must integrate multiple pieces of evidence and hold both constraints together until the intersection yields a single movie. This is the archetypal compose-then-answer pattern for end-to-end RAG.

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
