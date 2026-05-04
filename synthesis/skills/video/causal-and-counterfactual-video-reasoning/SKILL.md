---
name: causal-and-counterfactual-video-reasoning
description: Use this skill when the user asks questions like 'is this a crime?', 'is there an anomaly here?', 'is this person acting suspicious?', 'why did the fight break out?', 'is this area safe?', 'classify this dangerous event', or 'pinpoint the exact moment the robbery started'. Trigger it when the agent must distinguish between normal behavior and anomalous/illegal activities, deduce the hidden motives of actors in a conflict, or evaluate the causal progression of crimes and accidents in surveillance or open-world videos.
---

# Skill: causal-and-counterfactual-video-reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to perform high-level inferential, normative, and anomaly-centric reasoning to deduce physical and social root causes, classify criminal/anomalous activities, and align multi-agent intent within surveillance or safety-critical contexts. This involves differentiating between standard environmental states and anomalous deviations (crimes, accidents, hazards), interpreting communicative and kinetic signals to resolve social conflicts (Theory of Mind), and performing temporal grounding of causal triggers to explain unobserved motives or predict consequences under modified conditions.
* **Dimension Hierarchy**: Long-Horizon Reasoning->Inference and Planning->causal-and-counterfactual-video-reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A low-angle CCTV surveillance view of a public sidewalk where two men are standing and talking near a storefront.
* **Real Question**: Is there anything abnormal in this video? Describe the interaction and classify the event if an anomaly is detected.
* **Real Trajectory**: The agent first establishes the baseline of a normal conversation between the two subjects. It then detects a sudden shift in kinetic energy at T=45s where Subject A lunges toward Subject B. The agent tracks the physical contact, noting Subject A hitting and pushing Subject B repeatedly. It concludes that the social norm of peaceful interaction has been violated and classifies the event as an 'Assault' based on the unprovoked violence.
* **Real Answer**: Yes. A man violently assaulted another man by hitting and pushing him, which is an anomalous event of Assault.
* **Why this demonstrates the capability**: This case tests 'Anomaly Perception' and 'Normative Violation Deduction.' The agent must not only describe the pixels but also perform a causal analysis to label a specific kinetic interaction as a social and legal violation (Assault) rather than mere motion.
---
**[Case 2]**
* **Initial Environment**: A high-angle city camera overlooking a busy plaza with a police officer and several civilians present.
* **Real Question**: Detect an abnormal event of Arrest in the video and provide the start and end time of this specific event.
* **Real Trajectory**: The agent scans the environment to identify 'Safety-Critical' actors, specifically the police officer. It observes the officer approaching a man in a white T-shirt who is holding a bag. It marks the 'Onset' frame (T=21s) when the officer first makes physical contact to subdue the man. It then tracks the struggle and arrival of backup, finally marking the 'Offset' frame (T=109s) when the suspect is secured on a stretcher for transport.
* **Real Answer**: {"start time": 21, "end time": 109}
* **Why this demonstrates the capability**: This illustrates 'Temporal Anomaly Grounding.' The agent must precisely localize the causal boundaries of a social intervention (an arrest), distinguishing the preparation and follow-up from the core anomalous interaction window.
---
**[Case 3]**
* **Initial Environment**: A surveillance camera at a crowded transportation hub showing a suspect being apprehended by multiple law enforcement officers.
* **Real Question**: Who was the main perpetrator in the video and how was the suspect transported away? (A) Stretcher, (B) Car, (C) Electric scooter, (D) Bike.
* **Real Trajectory**: The agent performs an 'Audit of Intent' by looking back through the timeline to identify the individual whose actions triggered the police response. It identifies the man in the white T-shirt as the one showing resistance. It then tracks the resolution phase of the causal chain, observing the officers lifting the neutralized suspect onto a medical stretcher rather than into a vehicle.
* **Real Answer**: The main perpetrator was the man in the white T-shirt, and he was transported away by a (A) Stretcher.
* **Why this demonstrates the capability**: This demonstrates 'Causal-Object Detail Integration.' The agent must link the identification of a causal agent (perpetrator) with the retrieval of specific outcome-related details (transport method), proving it can track a complete crime-to-resolution narrative.

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
