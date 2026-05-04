# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Candidate Set Scaling: Compose questions by providing the agent with a massive, multi-attributed candidate set (e.g., a CSV or JSON of 2,000 entities) and a specific hidden target outcome. The prompt must require the agent to 'find the target or the best match' by outputting a sequential inquiry plan. This forces the model to perform the comparative analysis required to calculate information gain.
  - Vague Initial Intent: Start the user request with an extremely high-level category (e.g., 'I want a tool', 'I have an error message') and no other details. This necessitates a multi-turn planning sequence where the agent must decide which questions will reveal the most information first. An example is 'I want to buy a computer for work' which could be for a lawyer, a designer, or a coder, forcing the agent to split by 'Usage' first.
  - Controlled Attribute Traps: Include one or two 'Noisy Attributes' in the candidate set that are present in many items but provide very little splitting power (e.g., a feature that 95% of items have). The synthesized QA pair must show the agent correctly identifying and ignoring these noisy features in its plan, prioritizing the 'Sharp Splitters' instead.
  - Knowledge-Knowledge Discrepancy: Design scenarios where the user's intent uses a layman term (e.g., 'shiny') and the agent's internal data uses a technical term (e.g., 'glossy finish'). The agent must be forced to use its 'Perception' to translate the user feedback into its decision-tree logic, ensuring the synthetic data reinforces the semantic-symbolic bridge.
  - Forced Multi-Turn Constraint: Explicitly state that the user 'only has time for 3 or 4 questions' and the agent's search space is large (e.g., 1000 items). This forces the synthesizer to produce an 'Optimal' path where only the highest-gain attributes are selected. If the resulting plan fails to reach a small final set within the limit, the data point is non-compliant.
  - Expected Output Format: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory. { "question": "...", "answer": "...", "trajectory": [ {"step": 1, "observation": "...", "action": "..."}, {"step": 2, "observation": "...", "action": "..."} ] }
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
