# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write prompts in the user’s ordinary fairness language rather than metric language alone. Non-experts often ask whether two attributes are linked unfairly or whether a resource seems unevenly distributed, and the skill should teach the agent to formalize that request. This creates realistic trigger conditions for activation.
  - Ensure the environment supports more than one plausible bias method so that selection matters. The task should be stronger than a single canned test. For example, a categorical-categorical link question should force the agent to choose a suitable association or effect-size method from the available library.
  - Prefer outputs that combine a measurable result with an interpretable conclusion. A bias score plus a bias level, short explanation, or chart recommendation works well because it reflects real analytical usage. An edge case to avoid is asking only for a philosophical discussion of fairness.
  - Represent the trajectory as classify-select-measure-explain. The JSON should show how the agent identified the bias type, selected an appropriate method, ran the analysis, and summarized the outcome. That ordered structure is the core of this capability.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
