---
name: episodic-and-multi-hop-memory-reasoning
description: Use this skill when the user asks personal memory or environment search questions like 'Where did I leave my medication?', 'Where is the shampoo?', 'Did I turn the oven off?', 'Find the red bear cushion in the house', or 'Are there towels in the bathroom?'. Trigger it when the answer requires retrieving facts from distant temporal segments, tracking items that are out of view, or utilizing semantic world knowledge (e.g., connecting a bathroom mirror to the likely location of a toothbrush) to find specific objects or states within a long-horizon environment traversal.
---

# Skill: episodic-and-multi-hop-memory-reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to perform long-horizon retrieval of episodic facts and unobserved states by correlating multi-modal evidence—including hand-object interactions (HOI), audio triggers, and cross-object semantic co-occurrence patterns. This involves executing 'Embodied Question Answering' (EQA) by maintaining a dynamic mental model of the environment, grounding past observations or partner-provided cues in temporal-spatial buffers, and performing multi-hop reasoning to resolve queries about object placement, existence, identity, and progressive state changes across extended and fragmented video trajectories.
* **Dimension Hierarchy**: Long-Horizon Reasoning->Global Content Integration->episodic-and-multi-hop-memory-reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A first-person egocentric video log of a morning routine in a kitchen. The user interacts with various items including a medication bottle and a refrigerator.
* **Real Question**: Where did I leave my medication?
* **Real Trajectory**: The agent monitors the audio for Hand-Object Interaction (HOI) cues, detecting the specific 'click' of the medicine cap at T=45s. It then switches focus to the visual stream to observe the hand placing the bottle into a side drawer of the open refrigerator. Finally, it logs the state change as 'Medication inside fridge drawer' before the user leaves the kitchen.
* **Real Answer**: In the fridge drawer.
* **Why this demonstrates the capability**: This case requires correlating a subtle audio cue (bottle opening) with a brief visual placement action to encode a memory. The agent must retrieve this specific interaction segment from a long-running video to answer a question after the item is out of view.
---
**[Case 2]**
* **Initial Environment**: A large multi-room household environment where Robot 1 is searching for a red bear cushion and Robot 2 is exploring a separate living area containing diverse furniture.
* **Real Question**: Where is the red bear cushion most likely located?
* **Real Trajectory**: The agent receives a message from another exploration trajectory (Robot 2) which has identified a 'basketboard' and 'dolls' at a specific location, noting they are semantically relevant to a cushion. The primary agent evaluates this 'Relevant Object' cue and calibrates its confidence using statistical co-occurrence weights. It navigates to the indicated coordinates and visually confirms the red bear cushion resting on a blue chair near the dolls.
* **Real Answer**: On the blue chair next to the dolls in the living area.
* **Why this demonstrates the capability**: This illustrates 'Semantic Multi-Hop Retrieval' and multi-source information fusion. The agent must bridge a semantic gap (dolls/cushions) to find a target and integrate data from a disjointed exploration path to resolve a global spatial query.
---
**[Case 3]**
* **Initial Environment**: A 3D scan of a bathroom containing various fixtures (sink, mirror, toilet) and accessories (bath mat, towels).
* **Real Question**: What color is the bath mat in the bathroom?
* **Real Trajectory**: The agent performs an active search of the environmental scan, navigating from the hallway toward the bathroom. At T=120s, it enters the room and identifies a rug-like object on the floor. It performs a zoomed perceptual audit of the object's attribute (color) while cross-referencing its location to confirm its identity as the 'bath mat'.
* **Real Answer**: White.
* **Why this demonstrates the capability**: This demonstrates 'Environment Identification and Attribute Retrieval'. The agent must traverse a long spatial horizon to locate a room and extract a specific visual detail (color) about an object whose identity is grounded in its environmental context.

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
