---
name: long-horizon-information-recall-and-personalization
description: Use this skill when the user expects the agent to act as a deeply personalized assistant by synthesizing facts, schedules, and persona traits scattered across long conversation histories, or when the agent must proactively use past history to steer the conversation. It is triggered when the agent must detect implicit user preferences, identify schedule conflicts, distinguish between different speakers in group chats, or proactively mention past topics to build rapport. Everyday examples include: 'What should I do this weekend based on what I like?', 'Do you remember which one of us ordered the vegetarian meal?', and 'Bring up things we talked about last week to cheer me up.'
---

# Skill: long-horizon-information-recall-and-personalization

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to extract, reconcile, isolate, and synthesize multi-dimensional user context (personas, objective profiles, schedules) from extensive, asynchronous dialogue histories. This involves leveraging persistent memory to perform high-fidelity personalization, distinct speaker-specific attribute tracking, and proactive topic steering to maintain conversational engagement across multiple sessions.
* **Dimension Hierarchy**: Conversational Memory->Persistent Personal Memory->long-horizon-information-recall-and-personalization

### Real Case
**[Case 1]**
* **Initial Environment**: A long-term dialogue history (approx. 15k tokens) exists. The user's metadata identifies them as an 'adventurous tourism consultant' (profile) who 'admires Salvador Dali' (persona). These facts were revealed incrementally in separate sessions about work and museum visits.
* **Real Question**: I'm looking for a travel destination that offers both cultural depth and some professional inspiration for my next project. Where should I go?
* **Real Trajectory**: 1. Retrieve user's professional background (Tourism Consultant). 2. Retrieve user's personal interest (Salvador Dali). 3. Identify a location connecting both: Figueres, Spain (Dalí's birthplace). 4. Formulate a response that explicitly justifies the choice using both pieces of information.
* **Real Answer**: Considering your adventurous personality and your expert role as a tourism consultant, you might enjoy exploring Figueres. As the birthplace of Salvador Dalí, it provides the artistic inspiration you admire while offering the professional depth needed for your consultancy projects.
* **Why this demonstrates the capability**: This case tests Multi-Info Reasoning spanning temporal gaps. The agent cannot satisfy the request through one fact alone; it must synthesize a profile item (job) with a persona item (artist preference) from different historical sessions to generate a proactive, logic-driven recommendation.
---
**[Case 2]**
* **Initial Environment**: A multi-party spoken dialogue environment with two distinct users (User A and User B) and the Agent. User A has a deep, male-timbred voice, and User B has a higher-pitched, female-timbred voice.
* **Real Question**: (User A's voice): How to make my favourite food at home?
* **Real Trajectory**: 1. Analyze Round 1: Voice A (male) identifies as Jack and states his favorite food is sushi. 2. Analyze Round 2: Voice B (female) identifies as Olivia and states her favorite food is chocolate. 3. Detect current speaker in Round 3: The voice is identified as Voice A (Jack). 4. Retrieve the attribute linked specifically to Jack's identity buffer. 5. Synthesize a response providing a sushi recipe without confusing it with Olivia's state.
* **Real Answer**: Jack, to make sushi, you’ll need sushi rice, seaweed, and your choice of fillings like fish or vegetables. Spread the rice on the seaweed, add the fillings, and roll it up tightly using a bamboo mat!
* **Why this demonstrates the capability**: This demonstrates the agent's ability to maintain 'Speaker-Aware' memory matrices over persistent dialogue. It successfully distinguishes speakers based on previous interactions and ensures that the instructions strictly draw from the specific attribute provided by that explicitly identified speaker.
---
**[Case 3]**
* **Initial Environment**: A multi-session dialogue history is available where the user previously mentioned running a marathon and experiencing significant muscle pain. The current session has just started with the user mentioning a new interest in yoga.
* **Real Question**: I've started getting into yoga lately and I'm finding it really helps with my flexibility.
* **Real Trajectory**: 1. Analyze the 'current context' involving yoga and flexibility. 2. Retrieve relevant historical topics from memory, specifically the 'Marathon Race' session. 3. Perform 'Opportunity Detection' to see if yoga and recovery from a marathon are semantically linked. 4. Produce a proactive memory pivot linking flexibility back to marathon recovery.
* **Real Answer**: That's great! Yoga is excellent for flexibility. Did it help with your recovery after that marathon you ran last week? You mentioned being quite exhausted and in pain afterward.
* **Why this demonstrates the capability**: This case demonstrates proactive cross-session memory steering. By connecting the current user enthusiasm with a historically grounded, functionally relevant event, the agent leverages persistent memory to drive interpersonal continuity and active engagement rather than passive retrieval.

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
