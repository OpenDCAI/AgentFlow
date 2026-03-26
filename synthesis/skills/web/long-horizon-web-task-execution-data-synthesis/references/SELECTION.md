# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept the trajectory only if the task requires multiple dependent actions whose order matters. Reordering the steps should either fail or materially change the outcome. This distinguishes long-horizon execution from unordered browsing.
  - Accept only when the trajectory preserves all stated constraints through to the end. There should be evidence that each requirement was applied or checked, not merely mentioned at the beginning. If the final state violates a forgotten earlier constraint, reject it.
  - Accept only if at least one intermediate verification step is present. The agent should confirm that a filter, form field, or navigation action had the intended effect before continuing. This is essential because many real failures come from invisible or mistaken intermediate states.
  - Accept only if success depends on complete execution rather than on answer extraction alone. A workflow that can be graded without seeing whether the agent finished the action is not ideal for this capability. Final-state completion or fully verified selection is required.

* **Rejection Criteria**:
  - Reject trajectories that are long only because they wander. Extra steps caused by confusion, repetition, or irrelevant clicks do not create a valid long-horizon benchmark. The required length should arise from genuine task structure.
  - Reject tasks whose constraints are mostly decorative. If the agent can ignore one or more conditions and still arrive at the accepted answer, the example does not enforce long-horizon precision. Every declared requirement should matter.
  - Reject examples that collapse into a single search result or a single page extraction after one interaction. Those belong to search or reading benchmarks, not execution-heavy workflows. The browser should have to do sustained work.
  - Reject trajectories with no reliable completion signal. Long-horizon tasks are hard enough without ambiguous endpoints, so the environment should provide a perceivable way to know the task is done. If completion is hidden or unverifiable, the item should be revised.
