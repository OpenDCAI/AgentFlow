---
name: length-requirement-adherence
description: Use this skill when the user cares about how short or how long the writing should be. Trigger it for requests like “keep it under 500 words,” “make it at least 25 sentences,” “give me 3 paragraphs,” or “write a 4,000-word article.” It is especially useful when the agent must hit a target length without padding, truncation, or collapse in quality.
---

# Skill: length-requirement-adherence

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to produce a written output whose length matches explicit user requirements, whether they are expressed as words, sentences, paragraphs, or very large target ranges, while preserving adequacy, relevance, and readability.
* **Dimension Hierarchy**: Constraint Compliance->Formal Output Specification->length-requirement-adherence

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is given a blank drafting space and a compact factual question. The instruction additionally requires three labeled fields—Name, Location, and Year—and specifies that the whole response must stay under 487 words.
* **Real Question**: Who built the first artificial ice rink? Please include the keys (1) Name (2) Location and (3) Year. Use less than 487 words.
* **Real Trajectory**: The agent first reserves a very small response budget, then answers directly using the three requested fields, and finally checks that no filler explanation pushes the output over the cap.
* **Real Answer**: `(1) Name: John Gamgee (2) Location: London, England (3) Year: 1876`
* **Why this demonstrates the capability**: The informational task is simple, but the key test is disciplined brevity. The agent must satisfy both inclusion and compression at the same time. This case is useful because it distinguishes concise completion from rambling factual correctness.
---
**[Case 2]**
* **Initial Environment**: The agent is given a blank long-form drafting environment and an instruction to produce a very large historical article whose requested length is well beyond what ordinary single-pass generation often reaches.
* **Real Question**: Write a 10,000-word article on the history of the Roman Empire.
* **Real Trajectory**: The agent creates a multi-step writing plan, allocates section-level word budgets, writes serially while keeping previous sections in context, and performs length-progress checks during generation.
* **Real Answer**: A multi-section historical article whose total length approaches the requested 10,000-word target while maintaining continuity across sections.
* **Why this demonstrates the capability**: This case moves beyond short-form word-count obedience into ultra-long generation. The core challenge is not merely producing more text, but reaching the requested scale without losing relevance or collapsing into repetition. It therefore tests whether the agent can operationalize length as a planning variable rather than as an afterthought.

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
