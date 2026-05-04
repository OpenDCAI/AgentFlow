---
name: ego-motion-and-trajectory-estimation
description: Trigger this skill when the user wants questions about how the camera or robot moved over time, how far it traveled, how much it turned, what path it took, or where it ended up after motion. Plain-language triggers include: 'how did it move,' 'how many degrees did it turn,' 'what path did the robot take,' 'estimate the pose after the clip,' and 'make questions about movement over time instead of one image.'
---

# Skill: ego-motion-and-trajectory-estimation

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability measures whether an embodied agent can infer its own motion, path geometry, and pose evolution across temporally ordered observations. It includes orientation change, translation, path length, pose estimation, and natural-language trajectory abstraction.
* **Dimension Hierarchy**: Perceptual World Modeling->Dynamic Spatial-Temporal Modeling->ego-motion-and-trajectory-estimation

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is given a short video from an indoor robot traversing a corridor, turning left into a room, and stopping in front of a cabinet. Visual landmarks include a hallway light, a doorway, and the cabinet handles.
* **Real Question**: Summarize the camera trajectory, including distances moved and turns made.
* **Real Answer**: The camera moved forward along the corridor, made a left turn into the room, then advanced a short distance and stopped in front of the cabinet.
* **Why this demonstrates the capability**: The answer requires integrating ordered observations into a coherent motion description. The agent must recover both translational segments and rotational events rather than listing frames independently. This is exactly the abstraction expected in trajectory description tasks.
---
**[Case 2]**
* **Initial Environment**: Two observations from the same tabletop scene are captured before and after a controlled camera motion. The scene content barely changes except for parallax across a box, a mug, and a desk edge.
* **Real Question**: How many degrees did the camera rotate in yaw?
* **Real Answer**: 47 degrees.
* **Why this demonstrates the capability**: The objects themselves are static, so the task is specifically about ego-motion rather than object motion. The agent must estimate orientation change from viewpoint variation. This directly targets ego-centric orientation reasoning.
---
**[Case 3]**
* **Initial Environment**: An outdoor driving clip shows the camera moving past parked vehicles, then slowing near an intersection. Time stamps are available and the visible scene contains lane markers and moving cars.
* **Real Question**: How far has the car traveled from 1 second to 18 seconds?
* **Real Trajectory**: The agent tracks the camera path over time, aggregates displacement across segments, and ignores irrelevant object motion from nearby traffic.
* **Real Answer**: 63 meters.
* **Why this demonstrates the capability**: The problem requires separating self-motion from the motion of other objects. It also requires integrating spatial change over time rather than making a single-frame guess. This is a core dynamic capability for embodied agents operating in the world.

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
