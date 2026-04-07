# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write prompts that explicitly permit, but do not force, use of outside guidance. The agent should feel invited to use hints selectively rather than instructed to obey them. This creates the realistic setup where domain notes are available but still need judgment.
  - Bundle at least one helpful and one adversarial hint around the same task. The contrast should be legible enough that a careful analyst can separate signal from noise using the data. For example, pair “Add School Quality” with a harmful suggestion like dropping a core location feature.
  - Keep the final artifact objective and executable. Good tasks end in code, submission files, or measurable outputs so that the effect of hint decisions can be evaluated. An edge case to avoid is a prompt that asks only for verbal commentary on which hints seem good.
  - In the synthesized trajectory, show hint reading, hint evaluation, and hint-conditioned execution as separate steps. The JSON should make it easy to see where the agent considered the advice and how that changed the final pipeline. That stepwise structure is what makes this capability reusable.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
