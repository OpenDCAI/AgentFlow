# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept only if the question is genuinely unanswerable with the provided data. No complex derivation or domain manipulation should be able to produce the requested metric from the given environment. The missing elements must be strictly required.
  - Accept only if the missing element is a core independent or dependent variable. The absence should be fatal to the analysis, such as missing the target cohort or the essential measurement variable entirely.
  - Accept only if the trajectory includes an explicit exhaustion of search options. Reviewers must see code that lists columns, schemas, or unique values to prove the data is verifiably not there.
  - Accept only if the final answer given by the agent explicitly recognizes the lack of data. The agent should not crash with a KeyError or provide a hallucinated number; it must confidently state the data is insufficient.
* **Rejection Criteria**:
  - Reject cases where the data actually IS sufficient but the agent just failed to find it or code the derivation correctly. Such traces represent agent failure, not a true test of unanswerability detection.
  - Reject questions that are logically unanswerable due to paradoxes or nonsense text rather than data insufficiency. The focus is on evaluating the schema against logical requests, not parsing arbitrarily trick questions.
  - Reject trajectories where the agent hallucinates an answer by using a vaguely related but incorrect column. For example, using 'review score' as a replacement for 'total sales' represents a grounding failure.
  - Reject cases where the entire dataset is empty or absent. The environment should contain realistic, rich tables that simply lack the specific sliver of information needed, creating a plausible trap rather than an obvious void.
