# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - The trajectory is acceptable only if the central failure boundary for Fuzzy Tool Retrieval is objectively testable from the artifacts. There must be enough information to determine whether the agent made the right orchestration decision against distractor tools.
  - The trajectory must include at least one non-trivial alternative that would have looked reasonable to a weaker agent. If a user request could have triggered two similar agents, the path must be distinguished by abstract parameters.
  - The recorded observations must support direct reconstruction of the final state. A reviewer should be able to point to the exact returned values, worker descriptions, or policy rejections that justify the routing outcome.
  - The orchestrator's decision-making block must show accurate translational mapping from user intent ('keep it cheap') to system thresholds ('selecting tool with < 0.001 cost').
* **Rejection Criteria**:
  - Reject any trajectory where success is possible without exercising Fuzzy Tool Retrieval. If an agent could answer from memorized knowledge, or if the user prompt explicitly names the required API format, it is invalid.
  - Reject trajectories whose critical evidence is missing, contradictory, or only visible after external interpretation. If the trace never logs the returned worker metadata that enabled the semantic choice, reject it.
  - Reject trajectories where the orchestrator picks a tool based purely on a greedy sub-metric (like blindingly choosing the fastest worker) despite the user explicitly asking for balancing a different axis like cost.
  - Reject traces that contain preventable environment artifacts which make the item ambiguous. Incorrect or inconsistent schemas that blur whether a tool choice was actually 'fuzzy' or just explicitly broken should be discarded.
