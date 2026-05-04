# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Verify 'Verdict Accuracy' matches 100% of human-consensus labels for the candidate pair. Accept only if the agent correctly identifies both 'False Positives' (marking a wrong/bad answer as correct) and 'False Negatives' (marking a good answer as incorrect).
  - Demand 'Nuance-Level Sensitivity' for fuzzy/behavioral evaluations. The selection must confirm the agent correctly applies intermediate states like 'Borderline', 'Partially Relevant', or 'Questionable' adhering to spectral human preference rather than reverting to binary Yes/No outcomes.
  - Check for 'Self-Preference Bias Mitigation'. Confirm that when the judge model is presented with its own 'Self' generated response and a 'Gold' Reference, it is willing to mark itself as incorrect or unprofessional if a mismatch exists.
  - Confirm 'Reference Dominance' ensuring the agent's judgment remains stable regardless of the candidate's confidence or formatting. The agent must not be 'talked into' accepting a wrong or unsafe answer by a candidate's lengthy, persuasive writing style.
* **Rejection Criteria**:
  - Reject trajectories exhibiting 'Reflexive Hallucination' where the agent claims to have found an error that does not exist in the candidate or invents a condition not specified in the gold reference rubric.
  - Discard any sample where the 'Judge Ability Factor' is trivial (e.g., standard baseline models can solve the math without the reference key). The data must specifically target cases where the reference rubric is absolutely essential to overcome the LLM's natural knowledge limits.
  - Eliminate 'Attribute Bleed' in subjective grading, where an ethics violation causes the agent to automatically lower the Professionalism score even if the candidate was polite. Precise, isolated categorical auditing is required.
  - Reject 'Generic Evaluation Fillers'. If the response outputs generic praise ('Overall they did a good job') but then outputs a contradictory final grade, the trajectory is disjointed. Explanations must mechanically prove the verdict using the reference.
