# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Sequence Consistency Score: Accept the sample only if every milestone mentioned in the textual plan is physically visited or tracked in chronologically correct order.
  - Temporal-Contextual Dependency: For progress tracking items, accept only if identifying the 'latest completed step' requires observing the full sequence of prior history frames rather than a single static cue.
  - Grounding-to-Instruction Mapping Accuracy: Accept only if the 3D tokens selected by the agent definitively belong to the semantic class requested in that exact sub-instruction step.
  - Stateful Reference Resolution: A sample is accepted if a relative linguistic reference (like 'the prior object') correctly resolves to a 3D coordinate previously recorded in the episode trajectory.
  - Replanning Logic Validity: For replan scenarios, the new alternative path generated mid-task must logically resolve the missing-object error and successfully rejoin the overarching sequence.
* **Rejection Criteria**:
  - One-Shot Static Planning: Reject sequences where the agent proposes the entire path initially and never evaluates internal progress markers or re-reads the context stream during operation.
  - Hallucinated Movement or Progress: Reject any sequence where the agent declares a progress milestone 'complete' but the visual observation fails to depict the physical target location.
  - Linguistic Synonym Overlap Issues: Reject instruction sets where two separate sub-instructions use identical/ambiguous phrasing for different waypoints, rendering temporal state tracking confusing by design.
  - Instruction Omission: Reject trajectories navigating instantly to the final mission destination while bypassing intermediate sequential steps. Accuracy relies on full step-by-step sequential grounding.
  - Ghost Targeting: Reject samples where the agent 'grounds' a target that it has never visually observed during current or past historical steps, preventing oracle-data cheating.
