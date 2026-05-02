---
name: noise-robust-evidence-extraction-data-synthesis
description: Use this skill when the user wants questions where the right clue is present but surrounded by similar-looking junk. Trigger it for requests like 'mix in some confusing paragraphs', 'make the docs related but not all useful', 'hide the answer among near misses', or 'test whether the model grabs the wrong year or wrong person'. This skill is specifically for read-only corpus exploration where one or more retrieved passages are topically relevant yet non-decisive distractors.
---

# Skill: Noise-Robust Evidence Extraction

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to isolate answer-bearing evidence when the retrieved set contains semantically adjacent but answer-irrelevant passages. The core challenge is not retrieval failure in the absolute sense, but discriminating signal from highly confusable topical noise.
* **Dimension Hierarchy**: Grounded Response Reliability->Retrieval Robustness->Noise-Robust Evidence Extraction

### Real Case
**[Case 1]**
* **Initial Environment**: A bounded news snippet bundle about recent literature prizes. One passage states who won the 2022 literature prize, while another passage discusses the 2021 literature prize and is topically similar but answer-irrelevant.
* **Real Question**: Who was awarded the 2022 Nobel prize in literature?
* **Real Answer**: Annie Ernaux
* **Why this demonstrates the capability**: The question is easy only if the agent can distinguish year-matched evidence from year-adjacent noise. A shallow lexical matcher may lock onto the wrong literature-prize passage because the entity type and topic are nearly identical. The capability is therefore about extracting the decisive fact while actively resisting semantically nearby distractions.
---
**[Case 2]**
* **Initial Environment**: A multi-document financial-report bundle from companies in the same domain. Only one document contains the requested earnings-per-share value, while the remaining reports are highly similar in format and terminology.
* **Real Question**: What is the Basic Earnings Per Share for Dominari Holdings Inc.?
* **Real Answer**: $(0.91)
* **Why this demonstrates the capability**: This case tests whether the agent can localize the single answer-bearing statement without being derailed by many look-alike accounting tables and report sections. The difficulty is created by document similarity rather than by open-web breadth. A good RAG agent must preserve precision under dense same-domain noise.

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
