# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - The trajectory exhibits a verified 'Validation Gap' where two or more non-trivial actions occur without a redundant supervisor check, proving that unnecessary overhead was eliminated in favor of batched mile-stone reviews.
  - Traces must explicitly display 'Successful Tiered Escalation.' The Outer Loop (Global Revision) must only activate in response to a documented Inner Loop failure or systemic data-flow contamination that demonstrably could not be patched on-the-fly.
  - The agent's recovery phase validates 'Dependency-Aware Pruning', keeping valid nodes perfectly intact. Upon revising a failed node, the agent logically circumvents re-running parent tools that supplied purely successful, un-tainted baseline data.
  - The trace explicitly highlights 'Upstream-Aware Cascading Validation', wherein an intermediate summary is cross-referenced with a global semantic invariant (e.g., a total row count anomaly) specifically revealing an upstream logic leak successfully remedied by the Outer Loop.
* **Rejection Criteria**:
  - Reject any trajectory utilizing solely 'Step-by-Step Validation.' If the supervisor halts the workflow to demand verification following every discrete API call, it utterly fails the progressive efficiency milestone concept.
  - Discard instances triggering 'Global Plan Revision' without documenting any localized fix attempt or presenting a valid, systemic justification. Trivial typos repaired by unwarranted total project restarts offer zero tiered resilience training value.
  - Reject trajectories applying 'Blind Retries' that totally ignore the Graph Memory. If the orchestrator mindlessly hammers the terminal failing step instead of investigating the pipeline lineage for root upstream propagation, the logic falls short.
  - Exclude occurrences where subsequent calculation steps wildly inherit corrupted baseline data (Cascading Failure Score = Zero) because the outer-loop checkpoint negligently missed a glaring, mathematically impossible derivation output.
