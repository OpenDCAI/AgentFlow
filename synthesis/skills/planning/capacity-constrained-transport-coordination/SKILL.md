---
name: capacity-constrained-transport-coordination
description: Use this when the user wants planning data about moving several items with limited carrying ability, two hands, one hoist, or tight transport capacity. Trigger it for requests like 'make tasks where the robot can only carry a little at a time', 'give me move-things-between-rooms problems', 'create loading and unloading plans with bottlenecks', or 'make planning tasks where one carrier choice blocks another.'
---

# Skill: capacity-constrained-transport-coordination

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to coordinate movement of multiple objects across locations when carriers, manipulators, or transport assets have limited capacity, forcing the planner to schedule pickup, movement, handoff, and drop-off actions under occupancy constraints.
* **Dimension Hierarchy**: Closed-World Symbolic Planning->Spatial and Transport Reasoning->capacity-constrained-transport-coordination

### Real Case
**[Case 1]**
* **Initial Environment**: Two mobile robots with two grippers each stand in separate rooms of a small building. Four sample containers must be moved from a storage room to a lab, but no robot can carry more than two items at once and some door crossings are long enough to make unnecessary backtracking costly.
* **Real Question**: Move all four sample containers from Storage-A to Lab-C using the available robots and grippers.
* **Real Trajectory**: Robot 1 picks up two containers and heads toward Lab-C. Robot 2 picks up the remaining two containers and follows a non-conflicting route. Each robot unloads in the lab, freeing both grippers before any optional repositioning.
* **Real Answer**: A valid answer coordinates robot assignments so every object reaches Lab-C without exceeding per-robot gripper capacity.
* **Why this demonstrates the capability**: The planner must reason jointly about object allocation and transport capacity. Solving the task requires bundling moves efficiently while keeping track of which robot is holding what and when capacity is freed. That makes the benchmark sensitive to coordination errors rather than only shortest-path selection.
---
**[Case 2]**
* **Initial Environment**: A depot contains three crates in different storage zones and two movable hoists. Each hoist can lift one crate at a time, crates must be dropped legally, and a hoist cannot unload a crate at the exact position it currently occupies if the placement configuration is invalid.
* **Real Question**: Relocate the crates into the depot staging area using the available hoists and legal drop operations.
* **Real Trajectory**: Move Hoist-1 to Zone-A, lift Crate-1, reposition to the depot lane, and drop it. Move Hoist-2 to Zone-B, lift Crate-2, reposition and drop it. Reposition one hoist to Zone-C for the last crate while keeping placements legal.
* **Real Answer**: A correct plan sequences hoist travel and crate transfers so that no hoist exceeds capacity and every unload occurs at a valid destination position.
* **Why this demonstrates the capability**: This case tests transport coordination because the planner must interleave carrier movement with object movement under explicit capacity limits. It also checks that the agent respects action applicability constraints on unloading rather than treating transport as a simple teleportation problem. The difficulty comes from coupling who carries with where and when they may legally release.

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
