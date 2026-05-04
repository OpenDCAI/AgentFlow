# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - The trajectory is acceptable only if the 'Reactive Correction' was triggered by an explicit, observable environment delta or telemetry push (e.g., status code change or text alert) arriving mid-workflow.
  - Selected traces must exhibit 'Precedence Preservation,' meaning that despite the schedule or resource change, the agent maintains the correct sequence of operations (e.g., Step A must still complete before Step B).
  - The agent's final decision must perfectly align with the *most recent* data point or disruption pushed into its memory, avoiding reliance on older 'Success' logs preceding the disruption.
  - The interaction must display 'Logical Persistence' showing the agent remembers which previously completed tasks are still valid after the disruption occurs, proving the orchestration functions as an incremental update.
* **Rejection Criteria**:
  - Reject any trajectory where the agent's 'Replanning' is just a complete restart of the entire task without acknowledging what state was already completed successfully. Reactive adaptation is not a 'Blind Retry'.
  - Discard traces where the agent 'hallucinates' the removal of a disruption (e.g., attempting a 'Navigate' action across an explicitly 'Closed' bridge). Evaluated actions must be physically compatible with the disrupted state.
  - Reject situations where the agent ignores a live push notification and proceeds with its stale, failing plan. Notification neglect reflects broken coordination fidelity.
  - Reject trajectories where 'Action Loops' occur—repeatedly attempting the same blocked path despite receiving repeated 'Unavailable' errors. Agents must permanently mark failed resources according to the live alert.
