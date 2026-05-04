---
name: action-and-motion-understanding
description: Use this skill when the user asks 'how many times did [action] happen?', 'what is the player doing?', 'where did the ball go?', 'is this a complex move?', 'what happens next?', or 'compare these two athletes'. It is triggered for tasks assessing high-frequency sports dynamics, counting rapid repetitive actions (like rally counts), identifying specific kinetic stroke techniques, predicting immediate athletic outcomes, and ranking technical difficulty based on observed action units.
---

# Skill: action-and-motion-understanding

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to perform advanced temporal-kinetic evaluation and intent forecasting on dynamic, high-frequency visual streams. This encompasses decomposing complex global maneuvers into discrete atomic Action Units (AUs) to project next-states, tallying rapid repetitive events in information-dense sequences, ranking technical difficulty based on physical exertion metrics, and analyzing the spatial mechanics of both moving agents and their associated equipment (e.g., ball trajectories, hitting outcomes).
* **Dimension Hierarchy**: Temporal-Spatial Understanding->Dynamic Event Perception->action-and-motion-understanding

### Real Case
**[Case 1]**
* **Initial Environment**: A 10-second clay court tennis match clip. Two players are visible; one is preparing to serve from the near end of the court.
* **Real Question**: How many times did the two players hit the ball in total during this rally?
* **Real Trajectory**: Isolate the sequence beginning with the serve impact. Perform high-density frame sampling (10+ FPS) to distinguish between rapid return shots and volleys at the net. Count each discrete racquet-to-ball contact event while ignoring the player's recovery footsteps or ball-bounce sounds. The trace identifies 1 serve, 1 return, and 2 baseline groundstrokes.
* **Real Answer**: 4
* **Why this demonstrates the capability**: This demonstrates 'High-Frequency Quantitative Tallying' in information-dense sports. The agent must successfully segment and count atomic units that occur within millisecond windows, which is impossible without fine-grained kinetic perception of impact moments.
---
**[Case 2]**
* **Initial Environment**: A high-angle view of a tennis rally where the far-end player has just moved aggressively toward the net.
* **Real Question**: What is the specific technique used by the player to hit the ball and what was the direction of the shot?
* **Real Trajectory**: Analyze the player's body orientation and swing path as they approach the net. Detect the cross-court arm extension and the open-faced racquet angle. Map the resulting ball trajectory from the impact point across the longitudinal axis of the court. Conclude the action is a volley and its direction is cross-court.
* **Real Answer**: The player hit a forehand volley to the cross-court.
* **Why this demonstrates the capability**: This illustrates 'Kinetic Action Recognition and Directional Inference'. The agent must link the physical biomechanics of the player (shoulder rotation, wrist angle) to the resulting equipment state (ball path), proving an understanding of specialized technical execution.
---
**[Case 3]**
* **Initial Environment**: A synchronized multi-clip view of two athletes performing gymnastics floor routines. The first performs a double-tuck, the second a triple-twist.
* **Real Question**: Which of these videos has the highest difficulty in terms of technical skills?
* **Real Trajectory**: Divide each routine into countable rotational sub-units (Action Units). Trace the 360-degree rotation count for both the vertical and horizontal axes. Identify that the second athlete completes three full revolutions in the air compared to the first athlete's two, establishing a measurable increase in centrifugal momentum and technical complexity.
* **Real Answer**: Video 2 is more difficult due to the higher rotational count.
* **Why this demonstrates the capability**: This presents 'Technical Difficulty Ranking' through AU decomposition. The agent utilizes objective kinetic metrics derived from the video stream to synthesize a comparative judgment of athletic proficiency.

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
