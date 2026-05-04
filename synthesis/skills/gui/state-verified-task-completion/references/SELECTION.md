# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - **State-grounded success check.** Accept a trajectory only if you can name a verifiable condition showing that a system or app state is actually changed. Write one sentence identifying the exact confirmation signal and one sentence identifying the last causal action.
  - **Non-trivial reasoning burden.** Accept traces where reliance on a transient visual cue would result in a failure or incomplete transaction. Trace the path backward; if a weaker agent could solve it simply by matching the word 'Done' on a pop-up without checking the internal database or file state, revise the case.
  - **Durable Success Signal Verification.** Accept only traces that contain an observation of a permanent UI change that signals a backend data update, such as a 'Record ID' being assigned or an explicit internal debugger execution hook.
  - **Operational Protocol Compliance.** Accept traces that rigorously follow logical save or CUD (Create/Update/Delete) operations without resorting to unsupported read-only shortcuts.
  - **Evidence density threshold.** Accept only traces that preserve enough evidence to reconstruct why each major action happened, tracking both the prep variables and the post-save audits.
* **Rejection Criteria**:
  - **Superficial Success Hallucination.** Reject any trajectory where the agent claims the task is 'done' based solely on a temporary success toast or loading screen while the underlying data remains unverified.
  - **Shortcut contamination.** Reject any case where judging success from a transient visual cue or standard string-match returns the correct state as reliably as the intended deep-validation verification path.
  - **Broken Causal Chain.** Reject trajectories where a crucial save or commit step is missing, yet the final validation step abruptly succeeds. The logical leap into persistent memory requires strict documentation.
  - **Ambiguous answerability.** Reject any case whose final internal state cannot be checked or evaluated durably by benchmark code (e.g., stating a page 'looks pretty' vs ensuring a precise SQL attribute or JSON config update).
  - **Incomplete Transactional Fulfillment.** Reject cases where the agent performs only a subset of the required CUD operations, leaving the simulated system in a fragmented, logically inconsistent state.
