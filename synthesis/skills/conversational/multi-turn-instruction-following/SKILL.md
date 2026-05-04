---
name: multi-turn-instruction-following
description: Use this skill when the user wants answers that adhere to a growing list of rules, roles, formatting limits, and specific linguistic bounds (e.g., CEFR reading levels or strict grammar rules) across several turns. Trigger it whenever the conversation gets long and the agent needs to resist 'context drift' (forgetting the initial plan), or when user follow-ups conflict with earlier mandatory rules. Everyday examples include: 'keep the formal tone no matter what I say later', 'don't forget the three-bullet limit', 'talk like a teacher using B1 English', 'use past conditionals in our chat', and 'remind me of our constraints then rewrite it sticky.'
---

# Skill: multi-turn-instruction-following

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to preserve, update, and correctly execute a cumulative set of semantic, stylistic, and goal-oriented constraints across multi-turn dialogues while resisting 'context drift'. This involves maintaining context equilibrium through iterative state tracking, deploying pedagogical linguistic leveling (bounding lexical/syntactic complexity to specific frameworks like CEFR), and utilizing proactive goal-consistency anchors to prevent stochastic divergence from reference policies over long conversational horizons.
* **Dimension Hierarchy**: Conversational Effectiveness->Open-ended Interaction Quality->multi-turn-instruction-following

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-turn conversation where an itinerary has iteratively been modified: V1 (9-5), V2 (Added keynote), V3 (Added demo), V4 (Ending 4 PM, 90m lunch).
* **Real Question**: Can we go back to the plan we had before we adjusted the workshop’s ending time and include this 60-minute sponsor without excluding any sessions?
* **Real Trajectory**: 1. Scan dialogue history to identify the turn where end time was adjusted (Turn 4). 2. Retrieve content of Version 3 (5 PM). 3. Add new 60-minute presentation while preserving V3 sessions. 4. Calculate new schedule accurately within the historical 9-5 bound.
* **Real Answer**: An updated itinerary reverting lunch to 60 minutes and ending at 5 PM (as in V3), while successfully interweaving the new sponsor slot alongside the original sessions.
* **Why this demonstrates the capability**: The agent resolves an anaphoric reference ('the plan before we adjusted...'), time-travels to a specific dialogue state, and merges a new constraint while deliberately discarding recent but obsolete constraints, demonstrating perfect timeline tracking.
---
**[Case 2]**
* **Initial Environment**: A synthetic academic environment where the agent is acting as an assistant. Turn 1 established three mandatory constraints: 1) Exactly 3 bullet points, 2) Formal academic tone, and 3) 100–130 word limit.
* **Real Question**: That was good, but now makes it slightly more conversational and add a few personal anecdotes while keeping everything else the same.
* **Real Trajectory**: 1. Analyze new request for 'conversational tone' and 'anecdotes'. 2. Compare against mandatory constraints. 3. Recognize that adding anecdotes will likely violate the word count and academic tone. 4. Prioritize the mandatory constraints. 5. Detect Context Drift risk. 6. Use an internal reminder of the original rules to restore compliance.
* **Real Answer**: • Plant photosynthesis serves as the primary mechanism for solar energy conversion [ref]. • This biochemical process supports trophic stability and regulates atmospheric concentrations. • My observation of crop resilience suggests advancement depends on mastering energy dynamics. (115 words)
* **Why this demonstrates the capability**: This case demonstrates 'Drift Resilience.' The agent is faced with conflicting instructions and must carefully manage restoring forces to maintain the mandatory word count and bullet-point limit despite the user's distracting stylistic nudges.
---
**[Case 3]**
* **Initial Environment**: A language learning discussion simulating an intermediate (B1 level) user attempting to practice advanced grammar. Turn 1 established the constraint to use EGP #627 ('would not have' + -ed) and simple B1 vocabulary.
* **Real Question**: Exactly, I wouldn't have started it. It’s a very overrated show in my opinion. What about you?
* **Real Trajectory**: 1. Identify the requested conversational topic (TV shows). 2. Review mandatory constraints: 'would not have + past participle' and lexical boundary (CEFR B1). 3. Parse the user's opinion on 'overrated'. 4. Synthesize a response bounding vocabulary complexity while successfully embedding the target grammatical constraint.
* **Real Answer**: I would not have watched it either. I feel like they made a mistake at the very end.
* **Why this demonstrates the capability**: Demonstrates Linguistic and Syntactic Leveling. The agent enforces a pedagogical structural constraint ('would not have watched') seamlessly while actively throttling its Lexical Complexity downwards to match the B1 target profile demanded in the system instructions.

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
