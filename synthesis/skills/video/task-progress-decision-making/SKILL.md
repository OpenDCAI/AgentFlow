---
name: task-progress-decision-making
description: Use this skill when the user asks 'what do I do next?', 'what was the step before this?', 'is it safe to perform this?', 'did they follow the manual?', 'how do I fix this mistake?', or 'score the performance/skill level of this operation'. Trigger it for tasks evaluating sequential procedures, forecasting upcoming actions, verifying adherence to external operational rules (like safety protocols or Critical View of Safety), or proposing optimizations to a completed process. It is also suitable for 'Expert-level' assessment where a set of professional criteria or rubrics must be applied to a long video trajectory to judge technical proficiency.
---

# Skill: task-progress-decision-making

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to evaluate sequential task progress, predict logical next steps, reason about procedural adherence, and perform expert-level performance auditing across a temporally grounded trajectory. This includes mapping observations to external operational protocols to verify compliance (e.g., surgical safety manuals or industrial safety standards), modeling backward-forward sequencing logic, and applying multi-dimensional scoring rubrics (e.g., OSATS or quality assessments) to rate the efficiency, safety, and technical success of a complex workflow.
* **Dimension Hierarchy**: Long-Horizon Reasoning->Inference and Planning->task-progress-decision-making

### Real Case
**[Case 1]**
* **Initial Environment**: A kitchen environment where a user is holding a packet of cling film next to a bowl of yogurt.
* **Real Question**: What is the purpose of using the cling film packet and what are the possible risks of the current operation?
* **Real Trajectory**: Observe the backward context where the yogurt was prepared. Identify the current object (cling film) and its intended interaction with the bowl. Evaluate the forward risk of plastic disposal or physical splashing, concluding the goal is covering the bowl and noting potential contamination hazards.
* **Real Answer**: Goal: The cling film is being pulled out to cover the bowl of Yogurt. Risks: Splashing juice or tearing the film improperly. Response: Move slowly and secure the edges firmly.
* **Why this demonstrates the capability**: The agent must bridge real-time kinetic observations with a forward-looking procedural goal while proactively predicting potential operational hazards. This tests 'Risk-Aware Prediction', directly linking procedural intent to execution safety logic.
---
**[Case 2]**
* **Initial Environment**: A bread-making station featuring a dough mixer, a divider machine, and a shaping table where a worker is actively processing a large batch of dough.
* **Real Question**: After mincing the dough in the divider, what was the next step taken in the bread preparation?
* **Real Trajectory**: Locate the divider machine operation in the timeline. Monitor the worker retrieving the divided dough portions and observe the specific transition to the shaping table where the dough is physically rolled into individual functional balls.
* **Real Answer**: Shaping the dough into balls.
* **Why this demonstrates the capability**: This illustrates 'Coarse-Grained Event Sequencing' where the agent recalls the strictly ordered flow of actions. The model must track object dependencies across a multi-stage procedure to successfully identify the successor to a specific queried milestone.
---
**[Case 3]**
* **Initial Environment**: An endoscopic camera view of a laparoscopic surgery (cholecystectomy) focusing on the hepatic region and the gallbladder.
* **Real Question**: Evaluate the Critical View of Safety (CVS) based on the three essential criteria: proper identification of two structures, adequate cystic plate exposure, and complete hepatocystic triangle clearance. Provide scores (0, 1, 2) for each criterion.
* **Real Trajectory**: The agent identifies the 'Onset' of the dissection phase. It performs a zoomed perceptual audit on the hepatocystic triangle (Calot triangle) to verify if it is cleared of fatty and lymphoid tissue. It then identifies how many structures (cystic duct/artery) are isolated entering the gallbladder. Finally, it checks the visibility of the liver bed (cystic plate) to ensure dissection is deep enough, assigning scores based on the observed adherence to Strasberg’s safety guidelines.
* **Real Answer**: Two structures: 1, Cystic plate: 0, Hepatocystic triangle: 1.
* **Why this demonstrates the capability**: This tests 'Procedural Safety Auditing.' The agent must apply domain-specific safety criteria (CVS) to a temporal video stream to judge if the operator has achieved a 'Safe' state before proceeding with irreversible actions (cutting).

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
