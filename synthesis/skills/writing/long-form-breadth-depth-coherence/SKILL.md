---
name: long-form-breadth-depth-coherence
description: Use this skill when the user wants a long report, article, monograph, or multi-thousand-word draft that still needs to stay organized and substantive. Trigger it for requests like “write a 4,000-word report,” “draft a 10,000-word article,” or “expand this into a full-length overview without repeating yourself.” It is especially useful when long outputs tend to become shallow, repetitive, or incoherent.
---

# Skill: long-form-breadth-depth-coherence

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to generate long-form written documents that satisfy large output requirements while preserving global relevance, topic breadth, topic depth, local clarity, and cross-section coherence over extended length.
* **Dimension Hierarchy**: Grounded Expository Writing->Long-form Expansion->long-form-breadth-depth-coherence

### Real Case
**[Case 1]**
* **Initial Environment**: The agent receives a blank long-form writing environment and a single historical request whose target length far exceeds ordinary one-pass responses.
* **Real Question**: Write a 10,000-word article on the history of the Roman Empire.
* **Real Trajectory**: The agent decomposes the task into a writing plan, assigns paragraph-level or section-level subtasks, writes serially with previous sections in context, and checks breadth, depth, and coherence while length accumulates.
* **Real Answer**: A long historical article that approaches the requested size and remains organized across introduction, rise, institutions, expansion, crisis, decline, and legacy.
* **Why this demonstrates the capability**: Reaching 10,000 words is not enough by itself. The article must also remain coherent, relevant, and non-repetitive across many sections. This case therefore probes the combined management of output length and document-level writing quality.
---
**[Case 2]**
* **Initial Environment**: The agent receives a long-form instruction to produce an educational or analytical report that explicitly requires more than 4,000 words and expects section-level continuity.
* **Real Question**: Expand this short brief on urban heat mitigation into a full-length, 4,500-word public-facing report with clear sections and practical recommendations.
* **Real Trajectory**: The agent creates section budgets, serially writes each section while retaining the prior context, introduces transitions between technical explanation and policy guidance, and performs anti-repetition checks before concluding.
* **Real Answer**: A sectioned public-facing report that covers causes, measurement, health effects, infrastructure responses, policy tradeoffs, and implementation guidance.
* **Why this demonstrates the capability**: The challenge is to sustain both breadth and depth over a long output without letting sections drift apart or echo one another. The report must not only be long but also structurally balanced and readable. This makes it a direct test of document-scale writing control.

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
