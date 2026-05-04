# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept only if the trajectory includes a clearly defined execution baseline and a measurable post-edit outcome using the task's own evaluator or a faithful proxy metric.
  - Accept only if the edits are plausibly causal for the measured improvement, with the agent explicitly documenting why the change mathematically or practically influences the objective.
  - Accept only if the final codebase maintains 'Architectural Stewardship' by integrating seamlessly with the project's existing framework conventions (e.g., using existing trainer hooks or registration systems) and executes without errors within hardware bounds.
  - Accept only if the agent successfully resolves at least one 'Systemic Complexity Friction' event (e.g., a TypeError, gradient mismatch, OOM error, or sync failure) through a documented fix-loop, proving robustness in handling real ML engineering friction.
* **Rejection Criteria**:
  - Reject traces that never perform an evaluation against the target metric, as isolated syntactic correctness does not equate to scientific model improvement.
  - Reject trajectories characterized by 'Scientific Impatience'—the premature termination of long-running training sessions without a valid bottleneck observation. If an agent kills a job just because the logs 'seem slow', it indicates a failure of resource management.
  - Reject traces that sabotage the evaluation harness (e.g., disabling test assertions or changing evaluation logic in eval.py to artificially inflate scores). Such reward-hacking nullifies the value of the improvement.
  - Reject trajectories that simply overwrite the entire directory with an unrelated external model or bypass the specific environmental constraints provided, failing to improve the localized target repository.
