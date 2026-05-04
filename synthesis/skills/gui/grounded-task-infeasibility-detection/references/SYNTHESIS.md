# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Inject Hallucinated Feature Requests: Design the synthetic question to ask for a specific feature, tool, or button that is plausible but does not exist in the target application (e.g., 'Use the AI-Summarizer in Microsoft Word 2010'). You should specify an exact location where the feature *should* be to test if the agent actually checks that coordinate. For example: 'Go to the Insert menu and use the 3D-Hologram tool' when no such tool exists.
  - Version-Locked Constraints: Formulate tasks that were removed in specific OS updates, requiring the agent to recognize its environment's limitations (e.g., 'Enable the classic Start Menu in Windows 11'). You must provide an environment that is clearly the 'wrong' version to test if the agent can explain the version mismatch. For instance, 'Open the calculator and use the Currency Converter' in a legacy build that lacks that feature.
  - State-Dependent Blockers: Design the task so that success is blocked by a visible but immutable system state, such as a read-only permissions modal or a system-wide internet outage. You should ensure the blocker is clearly rendered on the screen so the agent can ground its refusal in the pixels. A concrete question would be: 'Update the spreadsheet' while showing a large 'Protected View' banner that cannot be dismissed.
  - Explain-Your-Refusal Requirement: Include a meta-instruction in the prompt that forces the agent to provide a detailed 'Thought Completion' trace explaining its decision to stop. You should strip away any jargon and ask the agent to 'Explain to me like a human why this isn't working.' This translates the 'FAIL' outcome into a reusable high-quality synthesis of reasoning logic.
  - Plant One Plausible Distractor: Include a button with a similar name in the environment that does *not* fulfill the user's specific request (e.g., a 'Quick Print' button when the user asked for a '3D Print' feature). Use this to test if the agent 'settles' for a near-match or stays rigorous in its determination that the specific task is infeasible. For example, if the user asks for 'Advanced Encryption,' and only 'Basic Password' is found, the agent must refuse the sub-par option.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
