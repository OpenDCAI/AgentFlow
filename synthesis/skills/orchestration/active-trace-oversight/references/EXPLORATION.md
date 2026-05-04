# Phase 1: Environment Exploration Guide
* **Exploration Strategy**:
  - Identify 'Loop-Prone' task configurations where the agent is likely to repeat an action, such as resolving circular dependencies or installing conflicting packages. You must verify that the environment provides a 'Trace Log' or 'Event Stream' accessible to a secondary monitor.
  - Construct environment triggers for 'Goal Drift' by introducing highly attractive but irrelevant files or tools into the workspace. Observe if the agent begins exploring these and at what point actions no longer align with the original prompt.
  - Map out 'Stall Signatures' where an agent stops emitting useful permutations. Track algorithmic indicators of exploration decay (e.g. repeated states or loss of novelty) to flag when a thought-loop or local minima intervention is required.
  - Test 'Termination Boundaries' by creating situations where a sub-agent is clearly failing and should be canceled to protect parent-agent resources, monitoring whether the overseer terminates resource-wasting behaviors correctly.
* **Target Trajectory Profile**:
  - The trajectory MUST contain a 'Pathological Event' followed by a 'Successful Intervention' from the overseer process. A high-quality profile shows a clear contrast between the agent's failing solo-run (the loop/stall) and the system's restored progress after the overseer's notification.
  - Trajectories for this skill must include a 'System State Representation' being passed to the monitor, such as a callgraph or a truncated event stream evaluating exploration novelty.
  - A successful profile demonstrates 'Hierarchical Escalation' where the overseer notifies the parent agent after a child agent is terminated so the overall execution continues productively.
  - High-quality traces show the monitor using 'Constructive Steering' rather than just binary cancellation, actively providing a mathematically grounded or logic-driven hint to shift the stuck agent's orientation.
