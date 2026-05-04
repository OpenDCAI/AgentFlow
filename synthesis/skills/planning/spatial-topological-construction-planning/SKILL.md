---
name: spatial-topological-construction-planning
description: Use this when the user wants planning data about where the agent can move, what it can paint or place from nearby, or how earlier building steps change what becomes reachable later. Trigger it for requests like 'make planning tasks with layout constraints', 'give me build-order problems', 'create tasks where you can only act from neighboring positions', or 'make plans where the path changes as the structure grows.'
---

# Skill: spatial-topological-construction-planning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to plan over adjacency, occupancy, reachability, and build-order constraints in environments where the legality of movement or placement depends on spatial topology and on structures created earlier in the plan.
* **Dimension Hierarchy**: Closed-World Symbolic Planning->Spatial and Transport Reasoning->spatial-topological-construction-planning

### Real Case
**[Case 1]**
* **Initial Environment**: A floor-painting team must color a grid into a target pattern. Robots can move between adjacent tiles, can paint only neighboring tiles, and cannot step onto tiles that are already painted.
* **Real Question**: Produce a plan that paints the target black-and-white pattern on the 4x4 floor without violating movement or painting rules.
* **Real Trajectory**: Start from an unpainted corner corridor. Paint only those neighbor tiles whose coloring will not trap the robot. Reposition through unpainted lanes before closing them. Finish by sealing the last accessible region from its boundary rather than from the center.
* **Real Answer**: A valid answer is any action sequence that realizes the pattern while maintaining a walkable frontier until the final paint actions.
* **Why this demonstrates the capability**: This task requires the planner to treat geometry as part of the state transition system. A locally appealing paint action can permanently destroy reachability, so the agent must reason about future access before committing to current coloring. The capability is therefore about topology-aware sequencing rather than simple pattern matching.
---
**[Case 2]**
* **Initial Environment**: A construction robot must assemble a stepped tower from blocks. The robot can carry blocks, place them, and climb onto previously placed structure elements, but it cannot magically reach upper placements from ground level.
* **Real Question**: Build the specified two-level tower with a side step that allows the robot to reach the final top placement.
* **Real Trajectory**: Carry the first block to create the side step. Climb onto the step to gain height. Carry and place the support block for the second level. Reposition using the new foothold and place the final top block.
* **Real Answer**: The correct plan first creates reachability, then uses the created topology to access the higher placement site.
* **Why this demonstrates the capability**: The benchmark tests whether the planner understands that construction actions alter future mobility. The right answer depends on build order and climbability, not just on the final geometry. That makes it a clean test of spatial-temporal coupling between structure creation and action feasibility.

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
