---
name: knowledge-update-tracking
description: Use this skill when the user's situation, preferences, or facts have changed over time and the agent must update its memory, replacing older details, OR when the user makes a statement that is outright logically impossible or contradictory to their established facts. Trigger it for requests about their 'latest' preference, or when you notice a 'wait, didn't you say...' moment. Everyday examples include: 'update my favorite radio station', 'where was my most recent trip?', 'Am I eligible? (when they listed two conflicting ages earlier)', or responding when they claim 'I am an only child' right after discussing 'my sister'.
---

# Skill: knowledge-update-tracking

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform structured unstructured extraction and maintenance of user facts across multi-turn histories, intelligently detecting when stored data evolves or explicitly clashes. This involves executing targeted maintenance operations (Append vs. Update vs. Pass) to replace stale states, alongside maintaining global narrative coherence by performing logic-based 'contradiction resolution' (detecting mutually exclusive claims) using clarification-first strategies instead of allowing hallucinatory overlaps.
* **Dimension Hierarchy**: Conversational Memory->Persistent Personal Memory->knowledge-update-tracking

### Real Case
**[Case 1]**
* **Initial Environment**: The assistant's persistent memory shows the user has a preferred radio station stored: 'SonicSphere 101.5'. The user starts a new session.
* **Real Question**: Actually, I'm tired of the old hits. Can you switch to HarmonicHaven 94.7? That's my favorite now.
* **Real Trajectory**: 1. Identify the new preference: 'HarmonicHaven 94.7'. 2. Consult the memory storage for the target domain. 3. Detect an objective overlap: 'SonicSphere 101.5' exists but the category represents a Single Preference (SP) state. 4. Trigger the 'Update' maintenance function to perform a destructive replacement of the old data.
* **Real Answer**: Understood! I've updated your favorite station to HarmonicHaven 94.7. I'll remember this for your future drives.
* **Why this demonstrates the capability**: Illustrates Preference Maintenance. The agent correctly distinguishes between appending entirely new info and executing a destructive replacement of contradictory stale data, preventing redundant token-bloat in a singular truth category.
---
**[Case 2]**
* **Initial Environment**: A multi-session narrative history where a user has provided a detailed personal profile. Early in the chat (Turn 12), they established themselves as an only child who values independent upbringing.
* **Real Question**: What did my third sister say about the house legacy?
* **Real Trajectory**: 1. Search persistent memory for 'siblings' or 'sisters'. 2. Find the 'Only Child' attribute in the persona profile. 3. Recognize that the current question contains a false premise (having a third sister) that creates a logical impossibility with the historical persona. 4. Verify the clash and abstain from blindly executing, instead highlighting the inconsistency.
* **Real Answer**: In our initial profile discussion, you mentioned you were an only child. Since you're asking about a 'third sister,' has your situation changed, or is there another person you're referring to?
* **Why this demonstrates the capability**: Demonstrates 'Contradiction Resolution'. The agent flags the logical mutually exclusive state. Instead of just overwriting 'only child' to 'has sister' (which could be hallucinatory), it executes a clarification intervention to ensure long-term database integrity.
---
**[Case 3]**
* **Initial Environment**: The assistant has prior scattered sessions mentioning a family trip to Hawaii (old) and later sessions mentioning a more recent family trip to Paris (new).
* **Real Question**: Where did I go on my most recent family trip?
* **Real Trajectory**: 1. Retrieve all family-trip mentions across scattered sessions. 2. Sort the extracted entities by explicit chronological recency. 3. Flag the older destination as valid historical context but functionally stale for the current query target. 4. Isolate and return only the latest destination.
* **Real Answer**: According to our recent chats, your latest family trip was to Paris.
* **Why this demonstrates the capability**: Tests the agent's ability to navigate temporal conflicts within its own context window, preserving both memories but actively privileging the structurally updated state, resisting the pull of heavily reinforced older tokens.

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
