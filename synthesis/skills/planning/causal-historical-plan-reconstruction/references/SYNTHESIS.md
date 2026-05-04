# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Create 'Interrupted Workflow' prompts where the user provides a goal and the starting state is several steps deep into a task with an ambiguous history. You should say: 'You are now on this page; looking at where you are, what was your previous strategy and how do we finish?' This forces the agent to use 'Causal Reconstruction' to ground its next move. For example, 'You are in the Checkout area; did you remember to apply the discount code?'
  - Introduce 'Action-Observation Mismatch' traps where a command (e.g., 'Click Buy') leads to an unexpected page (e.g., 'Login'). The user should ask 'What went wrong and how do we get back on track?' requiring the agent to back-track its causal logic to identify if the click was misdirected or if the state-transition rule changed. This targets the 'online adaptive' planning requirement.
  - Design cases with 'Fuzzy History Hints' where the user's description of the past is slightly inaccurate (e.g., 'I think you already saved it'). The agent must be forced to 'Refine' the user's belief by checking the environment markers (like file existence) and reconstructing the actual truth. A successful synthesis will show the agent saying: 'Actually, the file was not saved because the step was blocked by a popup; I will save it now.'
  - Embed 'Composite Verification Checks' requiring the agent to output its reconstructed history as an explicit JSON artifact before its forward plan. Use instructions like: 'First, list the steps you took to reach this state, then give me the next action.' This enforces the 'Plan-as-Primary-Artifact' rule and provides a supervision signal for the retrocausal reasoning capability.
  - Structure the synthesis environment with 'Multi-App Ambiguity' where the same state (e.g., a blank screen) could have different historical causes across different apps. The agent must use the 'Perception' layer to distinguish whether it is on a 'loading' screen, a 'timeout' screen, or a 'permission' screen to reconstruct the correct causal path. This ensures the synthetic data punishes shallow, modality-agnostic guessing.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
