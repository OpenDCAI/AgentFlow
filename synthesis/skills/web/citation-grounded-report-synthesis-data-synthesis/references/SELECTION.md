# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept the trajectory only if it yields coverage for the major sub-questions implied by the user request. Coverage means the agent has evidence for the problem framing, the main options or methods, and the key trade-offs or recommendations. If one of those areas is unsupported, the report is not ready to synthesize.
  - Accept only when at least two distinct sources support the final report’s central content. This guards against overreliance on a single page and better matches real research behavior. The sources should contribute non-redundant value, not just repeat each other.
  - Accept only if the agent can align major claims with concrete evidence locations. This can be sentence-level, section-level, or statement-level, but the mapping must be explicit enough that citation trustworthiness can later be checked. If the report would require retrofitting citations after the fact, reject the trajectory.
  - Accept only when the planned output remains within the evidence collected. The trajectory should not contain unsupported speculative sections or placeholder claims. As an edge case, if the user asked for a general framework but the sources only discuss narrow implementations, the agent should narrow the report rather than hallucinate breadth.

* **Rejection Criteria**:
  - Reject trajectories that collect many sources but do not map them to report content. Volume alone is not evidence of grounded synthesis. If the agent cannot say what each source will support, the trajectory is not mature enough.
  - Reject examples where the final answer could be a short factoid. This capability is about structured, citation-rich synthesis rather than concise lookup. If a one-line answer would satisfy the task, it belongs to a different skill.
  - Reject trajectories that rely on unsupported summarization of broad topics. The synthesized output must stay close to the actual collected evidence. If major conclusions would have to come from background model knowledge rather than retrieved sources, the example fails.
  - Reject examples where citations are decorative rather than functional. The benchmark should make it possible to test whether removing or swapping citations would materially weaken trustworthiness. If citations do not matter to correctness, the item is not well targeted.
