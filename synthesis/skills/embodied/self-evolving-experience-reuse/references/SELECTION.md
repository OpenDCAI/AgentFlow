# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Demonstrable Reuse Path: Accept the sample solely if an explicit connective logic path runs from the stored prior experience directly resolving an inefficiency in the subsequent task.
  - Procedural Rather Than Factual Transfer: Validate that the transferred memory pertains to how an agent must execute steps or frame preconditions, prioritizing dynamic behavior adaptation over static factual retrieval.
  - Later-Task Adaptation Evidence: Accept cases verifying the recalled strategy was robustly adjusted to fit a new object paradigm or localized map rather than naively parroting a copy-paste motion sequence.
  - Old Skill Preservation Validation: For multi-task continuous streams, accept sequences only if the agent reliably executes the original anchor tasks without significant performance breakdown or hesitation.
  - Outcome or Efficiency Gain: Ensure the application of the stored experience actively prevented an error or diminished total operation timesteps in the second task phase.
* **Rejection Criteria**:
  - Identical-Task Leakage: Discard sequences repeating fundamentally identical scenes and goals with negligible variations, which merely rewards rigid script memorization rather than flexible schema reuse.
  - Static Fact Recall Only: Reject task connections where the later prompt is solved purely by recalling a background world fact (e.g., 'cup is green') that does not mechanically guide an active procedural strategy.
  - Catastrophic Skill Degradation: Disqualify evaluation segments where the agent successfully adapts to the novel secondary task but hopelessly fails simple baseline tasks it had previously resolved.
  - Unrefined Failure Logs: Reject paths reliant upon raw, noisy failure transcripts without a synthesized realization explaining the precise correction mechanism adopted.
  - No Explicit Retrieval Opportunity: Eliminate prompt pairings lacking structural similarity or shared prerequisite logic, precluding any physical opportunity for the agent to adapt earlier procedural behaviors.
