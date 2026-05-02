# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write the prompt so the user naturally asks about an outcome, option, or impact, while the real trap sits in the contextual rules. The wording should sound like a normal business or scientific request, not like a rule-following exam. For example, ask which option is most cost-effective rather than telling the agent exactly which rule to apply.
  - Ensure the required rule is present in the provided context and not in the model’s prior world knowledge. The environment should contain the definitions, mappings, or clauses needed to solve the task. This keeps evaluation grounded and prevents hidden dependence on pretrained business knowledge.
  - Prefer questions where misapplying the rule yields a plausible but wrong answer. This is valuable because it teaches the agent that rule grounding matters and cannot be skipped. An edge case to avoid is a rule whose omission obviously causes a crash instead of a subtly wrong result.
  - Represent the trajectory as rule discovery followed by rule execution. The JSON should show the agent locating the relevant rule text, translating it into executable logic, and then applying it to the correct subset of data. That pattern is what this skill is meant to encode.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
