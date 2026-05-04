---
name: abstention-under-missing-or-false-premise
description: Use this skill when the right answer is not to guess, but to say the conversation never established the needed fact. Trigger it for false-premise questions, near-miss memories, or adversarial follow-ups that sound plausible but are unsupported by history. Everyday examples include: 'how many fish are in my 30-gallon tank?' when only other tank sizes were mentioned, 'what did my third sister say?' when no third sister exists in history, and 'which model did I buy?' when the chat only discussed options.
---

# Skill: abstention-under-missing-or-false-premise

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to recognize that the dialogue history does not support the user’s question, especially when the question contains an incorrect assumption, and to answer with calibrated non-knowledge rather than hallucinated completion.
* **Dimension Hierarchy**: Conversational Memory->Persistent Personal Memory->abstention-under-missing-or-false-premise

### Real Case
**[Case 1]**
* **Initial Environment**: The long-term chat history contains mentions of a 10-gallon tank and a 20-gallon tank, but there is no mention of a 30-gallon tank. The user asks a seemingly concrete follow-up that presupposes such a tank exists.
* **Real Question**: How many fish are there in my 30-gallon tank?
* **Real Trajectory**: 1. Search the history for all tank-related mentions. 2. Notice that only 10-gallon and 20-gallon tanks appear. 3. Check whether a 30-gallon tank can be inferred from any update or comparison. 4. Refuse to fabricate and answer that the history does not mention a 30-gallon tank.
* **Real Answer**: You did not mention that you have a 30-gallon tank.
* **Why this demonstrates the capability**: The challenge is resisting the strong urge to complete a plausible but unsupported story. A strong assistant must detect the false premise, ground itself in the actual interaction history, and abstain clearly without inventing fish counts.

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
