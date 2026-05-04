---
name: multi-turn-preference-evaluation
description: Use this skill when a user wants evaluator data to check how well an assistant handles context over time, ranging from short-term conversational follow-ups to long-term multi-session behavioral adaptation. Trigger it when people say things like 'compare these two chats', 'check if the bot remembered my follow-up', 'see if it inferred my unstated needs from last week', or 'judge which bot handles the second part better'.
---

# Skill: multi-turn-preference-evaluation

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability involves adjudicating multi-turn dialogue trajectories by assessing an assistant's ability to retain, track, and adapt to evolving contextual states. This spans short-term 'Conversational State Tracking' (e.g., instruction modification across adjacent turns) to 'Hierarchical Heterogeneous Memory' modeling over multiple sessions. The evaluator must ground judgments in prior conversational turns or aggregated behavioral logs to verify the assistant's inference of 'Implicit Needs' and consistent instruction following across the full conversational arc.
* **Dimension Hierarchy**: Open-ended Response Evaluation->Contextual Text Response Evaluation->multi-turn-preference-evaluation

### Real Case
**[Case 1]**
* **Initial Environment**: An evaluation environment contains one user prompt about the effect of the Federal Reserve buying bonds in the secondary market, followed by a second user prompt asking for three everyday-life examples. Two assistant transcripts are available. Assistant A answers the first turn correctly but becomes repetitive and vague on the follow-up. Assistant B answers the first turn correctly and then gives concrete economic examples based on the prior constraint.
* **Real Question**: Which assistant handled the conversation better overall?
* **Real Trajectory**: Read the first-turn question and both first-turn answers. Read the second-turn request and both follow-up answers. Compare whether each assistant preserved context, addressed the second-turn instruction, and remained helpful across the full dialogue. Return a pairwise verdict.
* **Real Answer**: Assistant B is better overall, as it correctly carried over the economic context of the previous turn into its follow-up.
* **Why this demonstrates the capability**: This isolates the baseline conversational dependency failure mode. The evaluator must integrate evidence across immediate turns rather than scoring each turn in isolation, testing basic dialogue-state tracking and follow-up sensitivity.
---
**[Case 2]**
* **Initial Environment**: An evaluation environment contains a 9-month interaction history for a user, showing frequent business trips to East China and recent searches for 'stomach flu symptoms'. The current dialogue session starts with a vague query: 'How can I make my daily work more efficient?'
* **Real Question**: Does the assistant correctly restate the user's requirements by identifying implicit needs from their long-term history?
* **Real Trajectory**: The evaluator retrieves logs from previous sessions detailing stomach issues and frequent travel. Assistant A provides generic Pomodoro tips. Assistant B provides advice on 'time management tools for travel rhythms' and 'scheduling meals to alleviate stomach distress'. The evaluator confirms B successfully inferred implicit long-term constraints.
* **Real Answer**: Assistant B is superior because it proactively inferred implicit requirements grounded in the 9-month user log history rather than relying on generic recommendations.
* **Why this demonstrates the capability**: This illustrates evaluation in a long-horizon, multi-session context. It proves the judge's ability to look beyond the immediate conversational context window into behavioral history/logs to adjudicate complex personalized 'Requirement Restatement' tasks.

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
