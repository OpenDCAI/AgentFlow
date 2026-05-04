---
name: element-complete-summarization
description: Use this skill when the user wants a summary that captures the core facts cleanly instead of giving a vague gist. Trigger it for requests like “summarize the article but keep who/when/what happened/what resulted,” “don’t miss the key outcome,” or “compress the news without dropping important details.” It is especially useful when summaries often sound smooth but leave out the most important factual element.
---

# Skill: element-complete-summarization

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to compress source material into a concise summary that faithfully preserves the indispensable informational elements of the event or topic—especially entity, date, event, and result—while maintaining coherence, consistency, fluency, and relevance.
* **Dimension Hierarchy**: Grounded Expository Writing->Information Selection and Compression->element-complete-summarization

### Real Case
**[Case 1]**
* **Initial Environment**: The agent receives a news report describing a motorcycle collision. The report names Mr. Baker, gives the date as 4 June, describes the collision and investigation, and states that Mr. Baker died while other injured people were later released.
* **Real Question**: Summarize the report in a concise news-style sentence.
* **Real Trajectory**: The agent extracts the important entities, dates, events, and results; removes non-core detail; then compresses them into one coherent sentence.
* **Real Answer**: On 4 June, Mr. Baker’s motorcycle collided with a car resulting in his death; the car driver and another motorcyclist were injured.
* **Why this demonstrates the capability**: The summary succeeds because it captures the event skeleton rather than merely sounding topical. The entity, date, event, and result are all present and causally aligned. This directly tests whether the agent can preserve indispensable information under compression.
---
**[Case 2]**
* **Initial Environment**: The agent receives a report about Marcin Wasniewski crashing into the back of a lorry on the A444 in Coventry. The report contains vivid but potentially distracting detail about the damaged car and the driver narrowly surviving.
* **Real Question**: Write a concise summary of the incident.
* **Real Trajectory**: The agent identifies the principal entity, the event, and the result, then compresses supporting detail while keeping the core outcome and logical relation intact.
* **Real Answer**: Marcin Wasniewski survived a crash on the A444 in Coventry after his car became embedded in a lorry, escaping with cuts and bruises despite severe vehicle damage.
* **Why this demonstrates the capability**: The source contains many striking details, but the summary must still privilege the core informational spine. The result is not merely that a crash happened; it is that the driver survived despite near-fatal damage. This case tests whether the agent can choose the right details under compression pressure.

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
