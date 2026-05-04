# Phase 1: Environment Exploration Guide
* **Exploration Strategy**:
  - Immediate conversational dependency mining: Discover dialogue seeds where the second or later turn cannot be judged correctly without understanding the earlier turns. Collect prompts whose follow-up refers back to a prior answer, constraint, or mistake, verifying that removing the earlier turn renders the follow-up ambiguous.
  - Heterogeneous multi-session log harvesting. For long-context edge cases, collect diverse multi-session data consisting of behavioral logs (e.g., searches, device operations) and dialogue turns spanning months to support complex persona synthesis.
  - Follow-up stress and constraint shift testing: Construct follow-ups that force revision, elaboration, simplification, or memory of named entities. Observe whether the candidate responses update correctly or suffer from repetition and context drift.
  - Implicit need contradiction profiling: Find instances where a model generates an answer that sounds helpful for a generic user but explicitly violates a trait or constraint established in a previous turn or a previous log session.
* **Target Trajectory Profile**:
  - Cross-turn and cross-session dependence: The judgment trajectory must explicitly cite earlier turns or specific past log entries as the rationale for why the current turn's response succeeds or fails.
  - Preference-relevant evidence density: The superior transcript must have a concrete advantage in responsive adaptation or memory, rather than merely being factually correct in isolation.
  - Discriminative preference against sychophancy: The evaluator must be shown rejecting an AI that is superficially polite but fails to integrate the user's historical restrictions or immediate follow-up constraints.
  - Full transcript traceability: The full dialogue context, including the exact order of user requests and assistant replies, must be preserved perfectly to reconstruct the state transitions.
