# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept the trajectory only if it contains at least one explicit evidence conflict, contradiction, or high-quality false lead. The conflict can be temporal, factual, or relevance-based, but it must be concrete and visible in the retrieved material. If every retrieved page agrees, the item is too clean for this capability.
  - Accept only when the final decision cites the exact criterion used to resolve the conflict. The criterion might be recency, first-time status, officialness, scope match, or entity identity. If the answer is chosen without an explicit tie-break rule, the reasoning is under-specified.
  - Accept only if the agent verifies the winning candidate with a source that is better aligned than the losing candidate’s evidence. Better aligned can mean more current, more direct, or more authoritative for the disputed field. This guards against lucky guessing disguised as reconciliation.
  - Accept only if the rejected candidate is rejected for a question-specific reason. It is not enough to say it ‘looks less reliable’; the agent must explain why it fails the precise wording of the task. For example, Broadcom may be relevant to the trillion-dollar event, but it fails if another company crossed later.

* **Rejection Criteria**:
  - Reject trajectories where the distractors are obviously irrelevant. Noise must be plausible enough to tempt a strong but careless agent. If the wrong pages are easy to dismiss without reading, the example does not test triage.
  - Reject trajectories where the accepted answer is justified only by citation count or source prestige. This capability is about reconciling evidence under the question’s exact semantics. A pile of vaguely authoritative pages is not a substitute for a clear conflict-resolution step.
  - Reject examples with unresolved ambiguity at the end. The final state must leave one answer standing under a defensible rule. If two candidates still survive and the trajectory simply picks one, the item is not ready for synthesis.
  - Reject trajectories that rely on private annotations telling the agent which page is right. The entire conflict must be resolvable from open evidence visible to a web agent. If the correctness signal lives outside the environment, the task is not a valid reconciliation benchmark.
