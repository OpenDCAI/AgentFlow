---
name: entity-and-key-detail-retrieval
description: Use this skill when the user asks 'where are my keys?', 'what specific tool did they use?', 'find the object of interest among the mess', 'what does the sign in the background say?', or 'extract the numbers/names so I can look them up'. Trigger it for tasks extracting exact metrics, reading subtle OCR/text from the environment, identifying fleeting details, and performing object-centric reasoning where a specific entity or variable must be isolated from distractors and complex scenes.
---

# Skill: entity-and-key-detail-retrieval

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to perform fine-grained visual extraction, identity-aware geometric localization, and object-centric scene decomposition to isolate target components within high-density video streams. This encompasses distinguishing between 'slots' of interest (e.g., active tools, target objects) and passive distractors, resolving multi-object interactions, and extracting specific environmental text, symbols, or localized anchor clues required to compute variables or execute downstream tool-use (e.g., extracting an exact location and year from a background sign).
* **Dimension Hierarchy**: Temporal-Spatial Understanding->Temporal Structure Analysis->entity-and-key-detail-retrieval

### Real Case
**[Case 1]**
* **Initial Environment**: A full football match video lasting over 100 minutes, with scoreboard overlays and multiple replay cuts. The question targets a specific shot sequence near the 81:38 mark.
* **Real Question**: How does the goalkeeper prevent Liverpool's shot from scoring at 81:38 in the video?
* **Real Trajectory**: Navigate to the clue window around 81:38, identify the goalkeeper in the defensive sequence, inspect the saving motion frame by frame, and isolate the exact body part and outcome of the save.
* **Real Answer**: He uses his right hand to deflect the ball out of bounds.
* **Why this demonstrates the capability**: The question is not about the whole match; it is about retrieving a very small but decisive detail from the correct segment. It tests whether the agent can first find the right window and then read fine-grained entity-level evidence inside that window.
---
**[Case 2]**
* **Initial Environment**: A tabletop environment featuring a Franka robot arm, a single red cube, and multiple distractor cubes of varying colors (e.g., blue, yellow, purple) on a table with a randomized background color.
* **Real Question**: Does the robot successfully grasp the red cube while ignoring the nearby yellow and blue distractors?
* **Real Trajectory**: The agent first performs an object-centric decomposition to segment the scene into 'slots', identifying the robot arm, the red cube (target), and the colored distractors. It tracks the trajectory of the end-effector as it approaches the red cube. Despite the presence of high-salience yellow blocks, the agent maintains an identity lock on the red cube, verifying the closure of the grippers around its specific geometric center and its subsequent lift.
* **Real Answer**: Yes, the robot successfully isolates the red target and completes the grasp, demonstrating that the policy is not confused by the distractor entities.
* **Why this demonstrates the capability**: This case demonstrates 'Active-Distractor Disambiguation'. The agent must use object-centric reasoning to distinguish the target entity from distractors and track the interaction (grasping) between two specific entities (Robot and Red Cube) despite the randomized environment.
---
**[Case 3]**
* **Initial Environment**: A first-person video recording of a traveler walking through the Joliet Iron Works Historic Site, showing a massive steel movable bridge in the distance. The speaker mentions it looks like a bridge from a specific 1970s movie.
* **Real Question**: What is the exact name of the historic site written on the entrance sign, and what specific type of bridge is seen spanning the river at 02:30? (This information is needed to search for its construction year).
* **Real Trajectory**: Navigate to the dense visual frame at T=00:15, perform OCR isolation on a partially obscured park sign to extract 'Joliet Iron Works'. Scan the horizon at T=02:30 to isolate the target entity (the bridge) from the background infrastructure, specifically identifying its structural type as a 'movable bridge'. Retrieve both details as explicit string variables.
* **Real Answer**: The site is Joliet Iron Works, and the bridge is a movable bridge.
* **Why this demonstrates the capability**: This demonstrates 'Anchor Fact Extraction' for downstream multi-hop/tool augmented reasoning. The video agent must retrieve high-fidelity micro-details (OCR text and architectural entity classification) from a noisy visual stream, providing the exact grounded variables necessary to resolve external knowledge queries.

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
