# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept only if the main challenge is defining the correct analysis frame. The case should require meaningful decisions about variables, filters, denominators, temporal boundaries, or cohorts.
  - Accept only if the trajectory exposes the population or temporal logic explicitly. A reviewer should be able to say who or what is in scope (e.g. 'Only logs within 5min of X') and why.
  - Accept only if the constructed dataset would support reuse for nearby questions. Strong dataset-construction traces leave behind a sensible, clean analysis frame that could answer related questions with small downstream modifications.
  - Accept only if the construction decisions are grounded in provided context. The agent should rely on documentation, schemas, and structural data previews rather than hidden prior assumptions.
* **Rejection Criteria**:
  - Reject cases where variable selection is obvious from the question and headers alone. If the right analysis frame can be assembled natively without making explicit scope or temporal design decisions, the scenario evaluates basic lookup rather than sophisticated framing.
  - Reject trajectories that conflate cleaning and construction without clarifying either. While the two often interact, this skill needs a visible emphasis on orchestrating the right logical bounds of a dataset.
  - Reject examples with unstable cohort definitions. If several plausible populations exist and the environment never resolves which one the question intends via docs or timestamps, the resulting supervision will be unpredictably noisy.
  - Reject tasks whose main burden is downstream modeling or deep inference after a trivial setup. Analytic dataset construction must remain the prevailing bottleneck algorithmically.
