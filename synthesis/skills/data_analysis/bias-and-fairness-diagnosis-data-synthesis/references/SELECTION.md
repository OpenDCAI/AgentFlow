# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept only if the task requires selecting or applying a bias-specific analytical method. A generic summary by subgroup is not enough unless it is tied to a fairness interpretation or metric. The trajectory should revolve around actual diagnosis rather than simple reporting.
  - Accept only if the relevant data type and bias type are inferable from the environment. The agent should have enough schema and value information to route to an appropriate method. If that routing is impossible, the supervision will be noisy.
  - Accept only if the result can be justified numerically and communicated clearly. Strong traces support both a measurable output and an explanation or visualization plan. This dual grounding is important for fairness tasks in practice.
  - Accept only if the bias analysis remains end-to-end solvable in a sandbox. The methods may be specialized, but they should be executable with callable tools or generated code inside the environment. This keeps the task within the allowed operating scope.
* **Rejection Criteria**:
  - Reject cases that reduce to generic descriptive comparison with no fairness interpretation. If the task merely asks for group means or counts and never frames them as bias or unfairness, it does not target this capability specifically. The diagnosis dimension must be explicit.
  - Reject trajectories that choose metrics arbitrarily. Applying a convenient test without justifying why it fits the feature types and fairness question yields poor supervision. Strong examples need method-task alignment.
  - Reject examples whose main challenge is data retrieval rather than bias analysis. While retrieval may appear, the central burden here should be diagnosing bias once the relevant features are in hand. Otherwise the case belongs under a grounding skill.
  - Reject fairness tasks that depend mainly on normative policy judgment rather than data-based quantification. The agent should analyze structured evidence, not legislate abstract values. If the environment cannot ground the diagnosis numerically, the case is too open-ended.
