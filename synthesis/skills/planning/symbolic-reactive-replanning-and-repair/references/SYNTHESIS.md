# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate the prompt using a 'Disrupted Narrative' style that presents a successful start followed by a sudden environmental shift or a 'Pre-condition Gating' obstacle. The question should be: 'You are currently holding the vegetable and about to put it in the microwave, but you realize the door is closed. How do you adjust your plan?' This forces the agent into an 'In-the-loop' repair scenario.
  - Incorporate 'Gated Dependency' instructions that specifically punish shallow sequences lacking pre-condition checks. Design a task where two subgoals (e.g., 'Opening a cabinet' and 'Holding a bowl') cannot be true simultaneously for the same agent. This forces the synthesizer to produce a plan that inserts a 'Put down' or 'Parallel delegate' action to bypass the state collision.
  - Describe the 'Unexpected Event' in terms of final state observations (e.g., 'The gripper status is now Empty') rather than narrating the cause. This forces the agent to use 'Causal Reconstruction' to infer which steps failed and how to restore the necessary states. For example, instead of saying 'You dropped it,' say 'The item is on the floor and you are not holding it.'
  - Structure the question to ask for a 'Self-Reflective Trace,' requiring the agent to output its Pre-condition check results for every step. Use prompts like: 'List the preconditions for each action and verify them against the current screen before you move.' This ensures the synthetic data captures the meticulous logic-checking required for robust long-horizon agents.
  - Introduce 'False Detours' that appear globally optimal post-perturbation but violate explicit domain limits or graph connections. Generate a scenario where a newly opened door looks like a shortcut but actually leads to a room without the necessary tools, forcing the agent to verify the 'Post-condition' of the detour before committing to a final path.
  - Include 'Multi-Agent Coordination' prompts where a single agent is physically incapable of satisfying all action pre-conditions alone. Ask: 'Help Alpha and Bravo cooperate to heat the food; remember that Alpha is currently busy holding the tray.' This targets the agent's ability to refine a workflow into a parallel multi-agent DAG to solve resource bottlenecks.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
