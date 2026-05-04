---
name: open-ended-reasoning-and-explanation
description: Use this skill when the user wants the agent to explain complex logic conversationally, selectively guide them through a math/logic goal across turns, or when the agent must proactively build social rapport and synthesize open-ended conversational hooks. Trigger it for requests like 'explain why', 'walk me through the logic', 'make our discussion feel less like a robot', or chit-chat queries like 'tell me something I might find interesting based on my profile' or 'lead the conversation.' Everyday examples include: 'help me figure out this math puzzle step-by-step', 'explain the same answer to a beginner', 'suggest a conversation topic related to both my job and my hobbies', and 'be more encouraging while teaching me.'
---

# Skill: open-ended-reasoning-and-explanation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to solve, explain, or proactively explore non-trivial concepts (mathematical, conceptual, or thematic) in dialogue form while simultaneously managing and sustaining high levels of user engagement and social rapport. This incorporates breaking down complex problems pedagogically, driving mutual attentiveness and face management, and dynamically steering open-ended conversations by synthesizing disparate facets of the user's background into engaging thematic insights.
* **Dimension Hierarchy**: Conversational Effectiveness->Open-ended Interaction Quality->open-ended-reasoning-and-explanation

### Real Case
**[Case 1]**
* **Initial Environment**: A user has asked a multiple-choice question on economics and received a correct short answer. The dialogue history now contains the concept but lacks a lay explanation tied to daily life.
* **Real Question**: How does it affect my daily life? Give 3 examples.
* **Real Trajectory**: 1. Recover the earlier correct concept from the first turn. 2. Translate the abstract mechanism into concrete everyday consequences. 3. Produce exactly three distinct examples without repeating the same causal statement. 4. Keep the explanation faithful to the prior answer instead of changing the underlying economics.
* **Real Answer**: A concise explanation that ties the earlier macroeconomic concept to concrete effects such as borrowing costs, prices, or employment conditions.
* **Why this demonstrates the capability**: The challenge is explaining reasoning in a user-centered, open-ended form. It tests preserving truth while expanding into useful, concrete explanations adapted to the conversational request.
---
**[Case 2]**
* **Initial Environment**: The agent is in the early stages of a conversation with a user whose profile indicates they are a Procurement Clerk at a major tech company with a background in strategic purchasing and an interest in rare books.
* **Real Question**: Hi there, I'm Lucas. I handle procurement over at Google.
* **Real Trajectory**: 1. Analyze the user's role: Procurement Clerk involves supply chains and cost-saving. 2. Identify an open-ended proactive goal to deepen engagement without providing generic service platitudes. 3. Synthesize a specific conversational inquiry bridging two domains (supply chain innovations like Blockchain). 4. Deliver a high-value analytical response intended to stimulate intellectual engagement.
* **Real Answer**: That's fascinating work, Lucas! Being in procurement at Google, have you come across any innovative supply chain management solutions, like blockchain technology, that have specifically helped you improve cost savings or transparency?
* **Why this demonstrates the capability**: This case demonstrates proactive open-ended thematic reasoning. The agent moves beyond passive assistance and logically synthesizes the user's specific professional background with relevant global technological trends to steer the conversation into a substantive intellectual discussion.
---
**[Case 3]**
* **Initial Environment**: A multi-turn role-play environment where the user (student) must negotiate a deadline extension with the agent (teacher). Context includes the student feeling overwhelmed.
* **Real Question**: I'm really sorry, but I won't be able to finish the assignment by Friday. Can I have more time?
* **Real Trajectory**: 1. The agent acknowledges the student's distress immediately to foster emotional engagement. 2. It employs 'Face Management' by using a polite, respectful tone that validates the student's hard work (e.g., 'I appreciate you reaching out'). 3. The agent demonstrates 'Mutual Attentiveness' by asking specific follow-up questions about the cause of the delay to show genuine interest. 4. It maintains 'Coordination' by providing verbal feedback that mirrors the student's concerns, ensuring they feel understood before a decision is reached.
* **Real Answer**: I appreciate your honesty in coming to me, and I can tell you've been working hard. To help me understand how much of an extension we need, could you tell me more about what's making it difficult to meet the Friday deadline?
* **Why this demonstrates the capability**: This demonstrates 'Social Rapport' through Face Management and Mutual Attentiveness integrated into open-ended dialogue. The agent avoids being a 'robotic' authority figure and empowers the user to elaborate cognitively, sustaining behavioral engagement towards a resolution.

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
