# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Three-or-more comparable candidate answers: Accept only trajectories with three or more candidate responses to the same prompt, ensuring enough structure for multi-level quality distinctions.
  - Each adjacent ordering has a reason: Accept only if every contiguous rank boundary can be explained by concrete criteria (e.g., better instruction following, superior tension, factual adequacy). If middle candidates cannot be distinguished, reject.
  - Prompt-stated constraint influences rank: Accept only if the user's explicit constraints dictate the final order, ensuring rankings don't collapse into vague textual impressions.
  - No single catastrophic failure dominates: Accept only if at least two candidates remain broadly plausible after first-pass reading. The sample should test comparative gradients, not exclusionary binary filtering of nonsensical garbage.
* **Rejection Criteria**:
  - Style-over-substance dominance: Reject sets where the winner is chosen solely on prose length or fluency while failing on narrative substance or factual correctness, which encourages superficial heuristics.
  - Forced rank over true tie: Reject any sample where the natural outcome is a tie but the trajectory forces a strict, unstable order. Produce pairs with resolvable ties instead if needed.
  - Incompatible response formats: Reject comparison sets where responses use completely incompatible modalities (e.g., table vs essay) when the prompt never specified a required format, polluting the judgment.
  - Missing rationale for middle ranks: Reject trajectories evaluating only the best answer while ignoring the comparative ordering among remaining candidates. Full listwise ranking depends heavily on middle-list explanations.
