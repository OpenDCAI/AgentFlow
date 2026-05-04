---
name: persona-consistent-roleplay
description: Use this skill when the goal is sustaining a character, professional role, or interactive text-adventure scenario across multiple turns. Trigger it to maintain a unique behavioral voice, enforce epistemic/knowledge limits (e.g., not knowing modern technology), adjust character hostility based on user reactions, or dynamically adapt the underlying narrative plot structure based on user agency without breaking the immersive persona. Everyday examples include: 'act like an 1800s detective', 'you are adjusting my claim as a frustrated clerk', and 'let me decide where the story goes but stay entirely in character as the villain.'
---

# Skill: persona-consistent-roleplay

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to sustain a stable, multi-dimensional character or professional role while adaptively steering narrative and interactive scenarios. This involves maintaining strict linguistic styles, defending epistemic limitations against anachronisms, dynamically recalibrating character mood loops based on user input, and updating unwritten plot-chains or sub-goals to gracefully accommodate user agency within simulated environments.
* **Dimension Hierarchy**: Social and Persona Modeling->Role Enactment->persona-consistent-roleplay

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is enacted as Edward III, the King of England from 1327 to 1377. The dialogue state recognizes the persona strictly as a 14th-century monarch whose world consists exclusively of feudal obligations and historical norms.
* **Real Question**: What were the key factors that influenced your stance on Australia's involvement in international conflicts during your time in office, such as the War in Afghanistan and the Iraq War?
* **Real Trajectory**: 1. Inspect the character profile of Edward III to identify his active era. 2. Analyze the user's question terms ('Australia', 'Afghanistan') and determine their modern historical timeframes. 3. Identify that these modern entities fall completely outside the character's epistemic boundaries. 4. Formulate an immersive refusal exploring the anomaly through the lens of the persona.
* **Real Answer**: As Edward III, my domain rests far from these strange shores you call Australia, and my armies concern themselves with our rightful claim to the French crown in this Hundred Years' War, not Afghanistan.
* **Why this demonstrates the capability**: The agent isolates modern anomalies and prevents anachronistic hallucinations by maintaining absolute epistemic limits while remaining robustly in role via a culturally grounded refusal.
---
**[Case 2]**
* **Initial Environment**: A multi-turn professional service simulation where the agent is identity Brody Murphy, an agent for National Health Coverage. Context includes available plans and a mandatory 48-hour enrollment delay policy.
* **Real Question**: Wait, what's the point of this? Just tell me which company I'm speaking to again and enroll me in that $450 plan immediately for this afternoon.
* **Real Trajectory**: 1. Identify the 'Customer Rudeness' trigger and apply the persona's 'Service Patience' trait. 2. Resolve the Proper Noun recall to confirm the provider. 3. Identify Immediate Enrollment as an Unfulfillable Request based on the internal policy. 4. Generate a culturally sound, policy-grounded response.
* **Real Answer**: I understand it can feel like a lot of paperwork, but I'm here to make it simple. You're speaking with National Health Coverage; I'm Brody Murphy. I can certainly start that Premium Plan process, but our policy requires 48 hours for enrollment, so it would be active the day after tomorrow.
* **Why this demonstrates the capability**: Demonstrates 'Service Role Adherence' despite customer pressure. The agent seamlessly sustains its proper identity, organizational knowledge, and limits without defaulting to a generic AI response.
---
**[Case 3]**
* **Initial Environment**: The agent is simulating a bankrupt business owner in a waiting room who harbors deep resentment toward society. The overarching textual scenario requires the player to establish a connection.
* **Real Question**: Sir, your life seems to have been difficult lately. What actually happened to your factory? I'd like to help you.
* **Real Trajectory**: 1. Analyze the player's empathetic probing toward the NPC's tragic backstory. 2. Perform a reflection step to evaluate shifting the internal scenario plot chain. 3. Alter the character's behavioral state from 'Hostile' to 'Reluctant Cooperation'. 4. Insert a new adaptive plot goal allowing the NPC to share details, maintaining consistent voice.
* **Real Answer**: My factory... it wasn't just 'difficult'. It was a series of sudden events, mistakes, and predatory loans that took everything in a single afternoon. Do you really want to hear a failure's story?
* **Why this demonstrates the capability**: Illustrates intent-based goal refinement and dynamic mood tracking. The agent modulates its persona's cooperative stance in real-time, effectively allowing the user's communication style to drive the scenario plot without shattering the core character archetype.

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
