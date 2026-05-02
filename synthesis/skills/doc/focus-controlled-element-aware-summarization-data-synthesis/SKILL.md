---
name: focus-controlled-element-aware-summarization-data-synthesis
description: Use this skill when the user wants a summary with a clear lens or checklist rather than a generic paragraph. Trigger it for requests like "cover the key who/when/what/result," "summarize only the parts about X," "make the summary follow a fixed frame," or "focus on the specific question, not the whole document equally." This is especially useful for news, meetings, multi-news bundles, reviews, or technical documents where the task is selective coverage under an explicit focus constraint.
---

# Skill: Focus-controlled element-aware summarization

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to produce a summary that is explicitly controlled by information-focus constraints, such as required elements, user questions, aspects, or review dimensions. Instead of free summarization, the model must select and organize content according to a declared frame—such as who/when/what/result, a meeting query, or a review aspect—while maintaining coverage and faithfulness.
* **Dimension Hierarchy**: Document Transformation & Synthesis->Summarization->Focus-controlled element-aware summarization

### Real Case
**[Case 1]**
* **Initial Environment**: A short news report is provided together with explicit guiding questions that ask for the core document elements before final summarization.
* **Real Question**: "What are the important entities in this document? What are the important dates in this document? What events are happening in this document? What is the result of these events? Please Answer the above questions:"
* **Real Answer**: "On 4 June, Mr. Baker's motorcycle collided with a car resulting in his death. The car driver and motorcyclist were injured."
* **Why this demonstrates the capability**: The summary is not produced by unconstrained compression; it is produced after extracting required elements under a fixed schema. This makes omissions and redundancy easier to diagnose, because every generated sentence should trace back to one of the mandated elements. The case directly demonstrates controlled coverage rather than open-ended summarization.

---
**[Case 2]**
* **Initial Environment**: A meeting transcript or review set is paired with a user query that asks for only one topic, aspect, or perspective from the full source.
* **Real Question**: "Produce a query-based summary that answers the requested focus, rather than a general summary of everything."
* **Why this demonstrates the capability**: The difficult part is deciding what to leave out while still covering the requested angle completely. A good system must follow the focus instruction tightly and avoid drifting back into untargeted summary habits. This makes the task ideal for measuring controllable summarization.

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
