# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept only if the final execution cleanly completes the end-to-end task (e.g., resolving all dependencies and running the evaluation pipeline, or saving the correct output artifact) using the repository's native orchestration.
  - Accept only if the agent successfully resolves at least one 'Tangled Dependency' or 'Undocumented Prerequisite' purely through iterative execution and self-correction, such as installing a missing library or adjusting an expected tensor key.
  - Accept only if the agent executes automated solutions without manual interactive intervention. Bypassing human-required steps with scriptable counterparts confirms autonomous execution capability.
  - Accept only if the generated logic or shell commands follow portable standard practices, using relative paths and preserving environment states across successive sub-processes during the pipeline.
* **Rejection Criteria**:
  - Reject trajectories that produce 'Stub' functions containing solely standard docstrings missing explicit logic, or paths demonstrating 'README-matching' without verifying structural logic. An agent that blindly follows outdated text instructions and abandons execution when it falls short fails to represent active reuse.
  - Reject traces where the agent achieves the goal by 'Bypassing' the core repository algorithms entirely to write custom independent scripts reliant on generic online libraries. The fundamental objective requires the reuse and adaptation of the dense codebase specified.
  - Reject trajectories characterized by 'Environment Variable Blindness' where the agent repeatedly ignores feedback about missing paths or unactivated environments, causing identical path-resolution failures in a loop.
  - Reject traces where 'Dirty Modifications' solve localized problems without persisting to repeatable scripts or wrapper implementations. Submitting manual 'sed' hacks without encoding them transparently guarantees future users cannot replicate standard runtime results.
