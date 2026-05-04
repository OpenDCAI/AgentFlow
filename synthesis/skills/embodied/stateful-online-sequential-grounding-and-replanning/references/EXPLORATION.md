# Phase 1: Environment Exploration Guide
* **Exploration Strategy**:
  - Instruction-to-Milestone Decomposition: The agent must translate long-horizon global commands into linear sequences of 3D milestones, mapping sub-instructions to initial 3D feature seeds in its memory.
  - Sequential Landmark Anchoring: As the agent navigates toward a sub-goal, it must intentionally identify 'transit landmarks' mentioned in the text, tagging and anchoring them in its 3D awareness graph as verified checkpoints.
  - Historical State Graph Maintenance: The agent must continuously feed previous navigation waypoints and grounded targets into its input context to build a stateful memory, uniquely allowing it to follow relative commands (e.g., 'the other room').
  - Trajectory Truncation for Progress Snapshots: Simulate mid-task snapshots by cutting successful trajectories at exact milestone timestamps to test the agent's retrospective understanding of how many sub-instructions have been completed.
  - Active Re-verification of Sub-Goal Progress: At each decision block, the agent must cross-check its current viewpoint against the active sub-goal's target tokens to decide if it should declare a milestone 'Complete' or propose a replan.
* **Target Trajectory Profile**:
  - Closed-Loop Milestone Logic: Trajectories must document explicit 'sub-goal reached' markers in the output stream, ensuring smooth transition states between one anchored target and the next.
  - State-Dependent Goal Resolution: The target profile must demonstrate the physical resolution of context-dependent descriptions ('return to it', 'the previous desk') through clear navigation to a historically acquired coordinate.
  - Visible Milestone Alignment: Truncated sequences must end with an observation that definitively signals an unambiguous completion of a linguistic sub-instruction to provide clean supervision for progress tracking.
  - Adaptive Replanning upon Grounding Failure: If a milestone target is unexpectedly missing or occluded, the trajectory dynamically showcases a 'Recovery Search' loop rather than crashing.
  - Integrated Planning and Action Trace: The profile exhibits 'Plan -> Ground -> Move -> Progress Check' explicitly in the reasoning trace at each spatial node.
