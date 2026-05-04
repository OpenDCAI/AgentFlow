# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - The intervention must be 'Objectively Justified' by the preceding 3-5 actions in the trace which demonstrate a lack of progress or a repeat of errors. You must verify that flags in the overseer's output accurately match the visual stagnation in logs.
  - Selected traces must exhibit 'Causal Recovery,' where the intervention leads directly to an observable change in the agent's strategy. It must execute a different tool or reason down a differing data path.
  - The overseer's analysis must identify the 'Root Cause' of the intervention, such as 'Token Waste' or 'Information Stagnation'.
  - The trajectory must provide a 'Resource Baseline,' showing that the intervention occurred before the task hit its catastrophic cost or systemic timeout limits.
* **Rejection Criteria**:
  - Reject any trajectory where the 'Overseer' is just a second agent that solves the problem instead of monitoring the first one's execution hygiene or state process.
  - Discard traces where the overseer intervenes 'Prematurely' before the agent has had a fair chance to resolve its own error (e.g. killing it after one standard tool failure).
  - Reject trajectories where the 'Notification' is ignored by the agent, and the agent proceeds with its failing logic. A contextual disconnect means the loop integration is nonfunctional.
  - Reject traces where the overseer's judgment is based on information that would be invisible to a real monitor, such as utilizing raw pre-training facts rather than analyzing the live trace stream for stalling evidence.
