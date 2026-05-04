---
name: symbolic-reactive-replanning-and-repair
description: Use this when the user wants planning data testing an agent's ability to update its course of action when the underlying structure or state of the world changes unexpectedly or when current actions become unfeasible. Trigger it for requests like 'make a task where the plan breaks halfway through', 'detect why I can't do the next step', 'verify if a subtask worked', 'perform a pre-flight check on the next action', 'fix a plan that got stuck', or 'generate data for reacting to changing maps or missing items during execution'.
---

# Skill: symbolic-reactive-replanning-and-repair

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to perform closed-world symbolic reasoning to detect environmental deviations—spanning discrete object state changes to broader graph/topological revaluations—and dynamically generate a restorative or alternative action sequence to satisfy terminal goal predicates from the disrupted state. It incorporates a self-reflective loop consisting of pre-condition verification (logic checks before an action) and post-condition evaluation (verifying execution effects) to trigger recursive replanning or task retirement.
* **Dimension Hierarchy**: Closed-World Symbolic Planning->Dynamic and Adaptive Plan Orchestration->symbolic-reactive-replanning-and-repair

### Real Case
**[Case 1]**
* **Initial Environment**: A mobile robot with a single gripper is standing in front of a microwave. A carrot is observed on the counter. The microwave door is currently closed.
* **Real Question**: Place the carrot into the microwave to heat it up.
* **Real Trajectory**: 1. [Initial Plan]: Pick up carrot -> Open microwave door -> Place carrot in microwave. 2. [Execution]: Robot picks up the carrot. 3. [Pre-condition Check]: Before 'Open microwave door', the robot checks its state. Pre-condition 'Hand-Empty' for the 'Open-Door' action is False because it is holding a carrot. 4. [Reflection & Repair]: The robot identifies the collision of constraints (holding object vs. operating door). It generates a repair: Put down carrot -> Open door -> Pick up carrot -> Place inside.
* **Real Answer**: put_down(carrot, counter) -> open(microwave_door) -> pick_up(carrot) -> place_in(carrot, microwave)
* **Why this demonstrates the capability**: This case demonstrates condition-check based reactive replanning. The agent performs a 'pre-condition' check that reveals its current symbolic state (holding an object) makes the next planned action (opening a door) impossible, forcing a dynamic insertion of restorative steps to satisfy the door's requirements.
---
**[Case 2]**
* **Initial Environment**: Two robots (Robot A and Robot B) are in a kitchen. Robot A is near the counter with a vegetable; Robot B is near the microwave. The microwave door is closed.
* **Real Question**: Coordinate a plan to put the vegetable in the microwave efficiently.
* **Real Trajectory**: 1. [Initial Plan]: Robot A picks up vegetable -> Robot A opens microwave -> Robot A places vegetable. 2. [Reflection]: Robot A realizes that opening the door while holding the vegetable is inefficient or blocked. 3. [Parallel Repair]: Robot A assigns 'Open microwave' to Robot B (who has empty hands) while Robot A performs 'Pick up vegetable'. 4. [Execution]: Robot B opens the door and Robot A simultaneously picks up the item. Robot A then places the item in the now-open microwave.
* **Real Answer**: Parallel([Robot A: pick_up(vegetable), Robot B: open(microwave)]) -> Robot A: place_in(vegetable, microwave)
* **Why this demonstrates the capability**: This demonstrates multi-agent belief-driven reactive repair. The planner identifies a physical bottleneck (one robot cannot hold and open simultaneously) and refines the plan by delegating enabling subtasks to a partner, maximizing parallelism and bypassing the single-agent state constraint.
---
**[Case 3]**
* **Initial Environment**: A symbolic workspace contains a Red block, a Blue block, and an Orange block. The Red block is clear; the Blue block is on the table; the Orange block is on top of the Blue block.
* **Real Question**: Your goal is to have the Orange block on top of the Red block. You started following a plan: 1. Unstack the Orange block; 2. Stack it on the Red block. However, after 'unstack', an event occurred: the Blue block was moved so that it is now on top of the Red block.
* **Real Trajectory**: 1. [Observation]: Detects that Red block is no longer clear (Blue is on it). 2. [Back-tracking]: Inferred that the 'Stack on Red' action's pre-condition (Clear Red) is now violated. 3. [Repair]: Unstack Blue from Red -> Put down Blue on table -> Stack Orange on Red.
* **Real Answer**: unstack(blue, red) -> putdown(blue) -> stack(orange, red)
* **Why this demonstrates the capability**: This case illustrates structural revaluation and repair. The agent detects an environmental change that invalidates the remaining steps of its original plan and must dynamically generate a new symbolic sequence to restore the required pre-conditions for its goal.

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
