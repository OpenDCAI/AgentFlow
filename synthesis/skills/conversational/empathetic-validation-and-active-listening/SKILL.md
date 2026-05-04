---
name: empathetic-validation-and-active-listening
description: Use this skill when a user requires emotional support, feels distressed, or needs an expert to help them collaboratively make sense of a complex personal situation (like medical symptoms or life challenges) before jumping to solutions. It is triggered by requests involving emotional venting, counseling needs, or diagnostic confusion where the user might say 'I'm upset,' 'why do I feel this way,' 'can you make sense of these symptoms?', or 'help me figure out what's wrong.' Everyday examples include: 'I'm so stressed about my job loss,' 'help me understand my anxiety about public speaking,' and 'I've been feeling weird lately, why do my test results look like this?'
---

# Skill: empathetic-validation-and-active-listening

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform identity-aware emotional support and collaborative sensemaking through an intention-centered reasoning chain. This involves analyzing a user's underlying state (Issue, Emotions, Needs) to infer a specific supporter intention (Insight, Catharsis, Hope), validating feelings, and structuring a diagnostic funnel that bridges the user's personal context with expert frameworks without premature solutionizing.
* **Dimension Hierarchy**: Conversational Effectiveness->Open-ended Interaction Quality->empathetic-validation-and-active-listening

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-turn dialogue where a seeker has recently experienced a major setback like a job loss and is expressing significant emotional distress.
* **Real Question**: I just lost my job and I feel like a total failure. I've worked so hard for years and it's all gone in an afternoon.
* **Real Trajectory**: 1. Analyze State: Seeker is distressed/shocked due to sudden job loss; feelings of failure; needs emotional validation. 2. Infer Intention: Focus on 'Support' to create a comforting environment and build trust rather than 'Give Information' (advice). 3. Select Strategy: Affirmation and Reassurance. 4. Execute: Generate a response that acknowledges the blow to their identity and validates their hard work.
* **Real Answer**: I can only imagine how hard this must be for you; losing a position you've invested years into is a massive blow, and it's completely natural to feel this way right now.
* **Why this demonstrates the capability**: This demonstrates intention-centered support. By choosing the intention of 'Support' over resolving the problem immediately, the agent avoids the error of telling the user to 'just find a new job,' which would overlook their current emotional state and potentially increase distress.
---
**[Case 2]**
* **Initial Environment**: A dialogue where a seeker is upset after being 'ghosted' by a partner for two weeks following an argument.
* **Real Question**: Me and my partner had an argument and I've been ghosted ever since. It's been 2 weeks and the silence is killing me.
* **Real Trajectory**: 1. Analyze State: Issue is ghosting/conflict; emotions are resentment/loneliness; needs insight into why it happened. 2. Infer Intention: 'Insight'—to help the seeker explore the dynamics of the relationship. 3. Select Strategy: Open Questions and Probes for Thoughts. 4. Execute: Ask a question that pivots the user toward exploring root causes.
* **Real Answer**: I'm so sorry you're going through this silence. Looking back at the argument you two had, what do you think might have caused your partner to react by ghosting you instead of reaching out?
* **Why this demonstrates the capability**: It demonstrates the use of a professional intention-to-strategy mapping. The agent identifies the need for 'Insight' to help the user organize their thoughts and moves beyond simple comfort to guided cognitive exploration.
---
**[Case 3]**
* **Initial Environment**: A multi-turn medical consultation with a patient experiencing severe restlessness after starting a new medication, seeking collaborative expert guidance.
* **Real Question**: I've been so on edge lately. I just can't sit still, and my legs feel like they have to keep moving. It started right after I began that new prescription. What is happening?
* **Real Trajectory**: 1. Fostering: Agent acknowledges the patient's distress empathetically before jumping to a diagnosis. 2. Gathering: Agent questions the timing relative to the specific medication. 3. Providing Information: Agent synthesizes the facts and labels the symptom as a 'restlessness side effect' called Akathisia. 4. Shared Decision: Agent explains the severity and suggests gently discussing dosage changes with a doctor.
* **Real Answer**: That feeling of not being able to sit still sounds incredibly exhausting. Based on your symptoms and the recent medication start, I believe you're experiencing a restlessness side effect called akathisia. Let's talk about how you can safely bring this up with your prescribing doctor.
* **Why this demonstrates the capability**: This illustrates 'Collaborative Sensemaking'. The agent seamlessly blends empathetic validation of the user's exhaustion with a structured diagnostic funnel, ensuring the user feels heard before expert medical information is applied.

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
