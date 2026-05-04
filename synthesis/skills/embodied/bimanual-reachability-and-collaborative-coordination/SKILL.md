---
name: bimanual-reachability-and-collaborative-coordination
description: Trigger this skill when the agent must coordinate two arms or manipulators to solve a task. Use this when the user's need involves bimanual tasks such as 'use both hands to lift this', 'pass the object from the left arm to the right', 'pick up two items at once without bumping the arms', 'which hand should I use for this?', or 'can the left arm reach that far?'. It is essential for tasks requiring role assignment between arms, reachability analysis, and collaborative movement to prevent inter-arm collisions or kinematic failures.
---

# Skill: bimanual-reachability-and-collaborative-coordination

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability evaluates an embodied agent's ability to perform reachability analysis and spatio-temporal coordination for dual-arm systems. It involves dynamic role assignment (deciding which arm is best suited for a target based on workspace constraints), managing independent parallel execution (multi-tasking in a shared workspace), and executing collaborative sequences (e.g., handovers or synchronous lifting). The agent must navigate kinematic singularities, workspace limits, and the high-dimensional control required to synchronize two end-effectors without mutual interference.
* **Dimension Hierarchy**: Continual and Safe Task Execution->Multi-Actuator Strategic Coordination->bimanual-reachability-and-collaborative-coordination

### Real Case
**[Case 1]**
* **Initial Environment**: A robot overlooks a long tabletop containing three distinct colored cubes: a red cube on the far left, a green cube in the center, and a blue cube on the far right. Both the left and right robotic arms are in their retracted 'home' positions.
* **Real Question**: Assign the correct arm to grasp each block based on reachability and workspace efficiency.
* **Real Trajectory**: The agent identifies that the red cube is deep within the left workspace and assigns the 'Left' arm to it. It evaluates the center green cube and, noting the kinematic ease for the right side, assigns 'Right'. Finally, it identifies the blue cube as being on the far right, assigning the 'Right' arm. It avoids 'crossing' arms, which would lead to a collision.
* **Real Answer**: [{'object': 'red_block', 'use_arm': 'LEFT'}, {'object': 'green_block', 'use_arm': 'RIGHT'}, {'object': 'blue_block', 'use_arm': 'RIGHT'}]
* **Why this demonstrates the capability**: This case tests the fundamental spatial reasoning and reachability analysis required to map environmental coordinates to specific hardware actuators. The agent must respect the physical constraints of each arm's workspace to prevent unreachable command failures.
---
**[Case 2]**
* **Initial Environment**: A kitchen counter with a small red block located near the far-left edge and a blue target pad on the far-right edge. A single arm cannot reach from the far-left to the far-right in one movement due to reachability limits.
* **Real Question**: Move the red block from the far-left edge onto the blue pad on the far-right edge.
* **Real Trajectory**: The agent initiates a 'Sequential Collaborative' plan. The left arm grasps the red block and moves it to a central 'handover' zone on the table. The right arm then moves to the central zone and grasps the block while the left arm releases it. The right arm then completes the motion to place the block on the blue pad.
* **Real Answer**: Task successful: Block transferred via bimanual handover to bypass single-arm reachability constraints.
* **Why this demonstrates the capability**: It demonstrates a collaborative sequence where one arm's output serves as the prerequisite for the other. The agent must manage the logical handoff and the temporal synchronization needed for two grippers to interact with the same object safely.
---
**[Case 3]**
* **Initial Environment**: A workspace where two different tasks must be completed: a hamburger needs to be placed on a tray in the center, and french fries need to be placed on the same tray. The tray is located in a central 'shared' workspace reachable by both arms.
* **Real Question**: Use both arms to pick the hamburger and french fries and put them both onto the tray simultaneously.
* **Real Trajectory**: The agent analyzes the 'Independent Parallel Manipulation' requirement. It commands the left arm to go to the burger and the right arm to the fries. Crucially, it plans non-intersecting trajectories for both end-effectors to ensure that as they converge on the central tray to drop the items, the physical structures of the arms do not collide.
* **Real Answer**: Both items placed on the tray; arms successfully deconflicted during parallel trajectory execution.
* **Why this demonstrates the capability**: This demonstrates collision avoidance and parallel coordination. The agent must not only plan for the targets but also maintain a 'safety awareness' of its own internal geometry (inter-arm collision) while occupying a shared central workspace.

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
