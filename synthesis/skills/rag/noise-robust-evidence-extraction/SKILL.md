---
name: noise-robust evidence extraction
description: Use this skill when the user wants questions where the right clue is present but surrounded by similar-looking junk, typographical errors, or misleading formatting. Trigger it for requests like 'mix in some confusing paragraphs', 'test whether it finds the wrong year', 'hide the answer among near misses', or 'test if the model can read through OCR errors like WN8A'. This skill ensures the agent can isolate the true semantic signal amidst both macro-level topical distractors and character-level document degradation.
---

# Skill: noise-robust evidence extraction

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to isolate answer-bearing evidence when the retrieved set contains semantically adjacent, lexically corrupted, or topically identical but non-decisive distractors. The core challenge lies in discriminating true signal from highly confusable noise, utilizing contextual clues to reconstruct intended meaning even when primary entities are mangled by OCR or embedded deeply within highly repetitive templates.
* **Dimension Hierarchy**: Grounded Response Reliability->Retrieval Robustness->noise-robust evidence extraction

### Real Case
**[Case 1]**
* **Initial Environment**: A bounded news snippet bundle about recent literature prizes, where passages discuss overlapping eras. One passage states who won the 2022 literature prize, while another passage discusses the 2021 literature prize and is topically similar but wholly answer-irrelevant.
* **Real Question**: Who was awarded the 2022 Nobel prize in literature?
* **Real Trajectory**: The agent reads the first snippet, notes the entity 'Annie Ernaux', and checks the date '2022', bypassing the secondary snippet discussing '2021'.
* **Real Answer**: Annie Ernaux
* **Why this demonstrates the capability**: The question tests whether the agent can distinguish year-matched evidence from year-adjacent noise. A shallow lexical matcher may lock onto the wrong literature-prize passage because the entity type and topic are nearly identical, requiring the agent to actively resist semantically nearby distractions.
---
**[Case 2]**
* **Initial Environment**: A multi-document financial-report bundle containing numerous companies in the same domain. Only one document contains the requested earnings-per-share value, while the remaining reports are highly similar in tabular format and corporate terminology.
* **Real Question**: What is the Basic Earnings Per Share for Dominari Holdings Inc.?
* **Real Trajectory**: The agent filters out the generic corporate filler, isolates the specific table tagged for 'Dominari Holdings Inc.', and extracts the precise numeric value corresponding to Basic EPS.
* **Real Answer**: $(0.91)
* **Why this demonstrates the capability**: This case tests whether the agent can localize the single answer-bearing statement without being derailed by many look-alike accounting tables and report sections. The difficulty is created by exact-match document similarity rather than open-web breadth, forcing high precision under dense same-domain noise.
---
**[Case 3]**
* **Initial Environment**: A RAG context containing a technical report regarding the 'Unrivaled' basketball league, classified as an 'Imperfect Scan' containing extreme layout artifacts. The OCR process has mangled key target tokens, presenting 'WNBA' as 'WN8A' and '2024' as '2O24' due to digital visual noise.
* **Real Question**: What strategic value does the introduction of Unrivaled provide to WNBA players in the 2024 landscape?
* **Real Trajectory**: The agent scans the document, recognizes that 'WN8A' and '2O24' refer contextually to the target query terms based on the surrounding basketball lexicon, reconstructs the mangled tokens, and extracts the uncorrupted strategic value.
* **Real Answer**: The introduction of Unrivaled provides strategic value by capitalizing on the record-setting engagement in women's sports seen in 2024, offering WNBA players increased visibility.
* **Why this demonstrates the capability**: This demonstrates deep resilience to character-level noise and imperfect formatting. The agent must not fail because of literal string mismatches, but instead must employ global semantic context to repair and lock onto the target facts.

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
