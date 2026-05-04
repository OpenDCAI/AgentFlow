---
name: symbolic-state-tracking
description: Use this when the user wants planning data about keeping track of where things are, what is on top of what, what is free or blocked, mapping a path mentally, or when later steps only work if earlier moves changed the state correctly. Trigger it for requests like 'make tasks where one wrong early move ruins everything', 'give me block moving plans that depend on what is clear', 'navigate this maze by keeping a visual note of turns', or 'create tasks where the plan must remember what changed after each step, even if the actions use weird or random code names.'
---

# Skill: symbolic-state-tracking

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to maintain an internally consistent symbolic model of object relations, spatial grids, action preconditions, and action effects across a multi-step plan. This ensures every subsequent action is grounded in the true state produced by earlier actions, including the ability to perform pure relational or spatial logic mapping even when terminology is intentionally obfuscated or navigation pathways require an internal visual scratchpad.
* **Dimension Hierarchy**: Closed-World Symbolic Planning->State and Resource Reasoning->symbolic-state-tracking

### Real Case
**[Case 1]**
* **Initial Environment**: A symbolic tabletop world contains five blocks. The planner is told that b5 is on b3, b4 is on b2, b2 is on b1, b3 is on b4, b1 is on the table, b5 is clear, and the robot arm is empty.
* **Real Question**: You have 5 blocks. One cannot place more than one block on another block. b5 is on top of b3. b4 is on top of b2. b2 is on top of b1. b3 is on top of b4. b1 is on the table. b5 is clear. Your arm is empty. Your goal is to move the blocks. b1 should be on top of b2. b3 should be on top of b5. b4 should be on top of b1.
* **Real Trajectory**: Unstack b5 from b3 and put it on the table. Unstack b3 from b4 and stack it on b5. Unstack b4 from b2 and put it on the table. Unstack b2 from b1 and put it on the table. Pick up b1 and stack it on b2. Pick up b4 and stack it on b1.
* **Real Answer**: A valid final plan is: unstack(b5,b3) -> putdown(b5) -> unstack(b3,b4) -> stack(b3,b5) -> unstack(b4,b2) -> putdown(b4) -> unstack(b2,b1) -> putdown(b2) -> pickup(b1) -> stack(b1,b2) -> pickup(b4) -> stack(b4,b1).
* **Why this demonstrates the capability**: The task cannot be solved by local pattern matching because the planner must update the truth of ON, CLEAR, ARM-EMPTY, and holding predicates after every move. Each later action depends on whether prior actions created the required clear surfaces and free gripper state. This makes the benchmark sensitive to state-update errors rather than mere goal recognition.
---
**[Case 2]**
* **Initial Environment**: A randomized symbolic logic puzzle where all actions and predicates are replaced by random alphanumeric strings (e.g., j4gv801gnu...). This removes all semantic hints, forcing the agent to rely entirely on tracking the provided PDDL-style precondition and effect definitions.
* **Real Question**: As initial conditions I have that, af9tse23ljclsqad object_0, af9tse23ljclsqad object_2, af9tse23ljclsqad object_3, b6e9q4r60gagvdcn object_1 object_2, cql4o62p1yeke3ok, tv30k33pzoulql6w object_0, tv30k33pzoulql6w object_1 and tv30k33pzoulql6w object_3. My goal is to have that b6e9q4r60gagvdcn object_2 object_1.
* **Real Trajectory**: 1. wio5amhq7814n006 object_1 object_2; 2. kip9uw781pv62umn object_1; 3. u64y1a9apusmslxb object_2; 4. j4gv801gnu2it0yj object_2 object_1.
* **Real Answer**: wio5amhq7814n006 object_1 object_2 -> kip9uw781pv62umn object_1 -> u64y1a9apusmslxb object_2 -> j4gv801gnu2it0yj object_2 object_1.
* **Why this demonstrates the capability**: This represents the peak difficulty of objective state tracking, where no linguistic cues exist. The agent must parse the abstract rules to realize that state relationships change according to abstract mechanics. By finding a plan, the agent proves it can handle System 2 reasoning over pure symbolic state updates without relying on pre-trained semantic shortcuts.
---
**[Case 3]**
* **Initial Environment**: A grid-based maze environment (e.g., 5x5) where the agent starts at a green arrow and must reach a red circle endpoint. The layout contains black lines representing walls and white traversable paths, requiring the agent to maintain an internal state (a spatial tracker or latent sketchpad) of its position to avoid backtracking.
* **Real Question**: Given the maze layout provided, determine the valid action sequence (go forward, turn left, turn right) to move from the green arrow to the red circle. Show your progress in the maze every few steps to ensure you are tracking your location.
* **Real Trajectory**: 1. [Textual Reasoning] Starting at the green arrow, move forward into the corridor; [Latent State] Internal representation of the agent at coordinates 1,2. 2. [Textual Reasoning] Reach the first corner and turn right; [Latent State] Updated internal mapping showing a new heading North. 3. [Textual Reasoning] Continue to the junction and turn left toward the goal; [Latent State] Final path trace connecting start to end on the grid.
* **Real Answer**: <actions>go forward, turn right, go forward, turn left, go forward</actions>
* **Why this demonstrates the capability**: This tests state tracking in a continuous spatial grid because the agent cannot rely solely on its initial coordinates for a long-horizon task. By dynamically tracking internal updates of its path (a visual scratchpad or Cartesian map state), it grounds its textual movement actions in a perfectly consistent spatial state matrix across time.

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
