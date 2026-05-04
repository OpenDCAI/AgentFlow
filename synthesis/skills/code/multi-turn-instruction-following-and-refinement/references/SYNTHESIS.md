# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer 'Cumulative Constraint Packs' by providing a series of 5-8 non-conflicting verifiable instructions to be delivered over a multi-turn session. Use a mix of functional (Edge Case, IO conditions) and non-functional (Complexity, Standard) strategies to challenge the agent's memory span. The final question should reward the agent for maintaining 100% adherence to all 8 instructions. For example: 'Update the function to use snake_case, handle negative numbers, and include full type hints.'
  - Embed 'Implicit Context Dependencies' where the correct implementation of Turn 5 depends on the variable names or class structures initialized in Turn 1. This forces the agent to read the 'Grounding Context' and the 'Historical Dialogue' to remain aligned. A successful synthesis will result in an agent correctly referencing `self.settings` from the class definition provided five rounds earlier. This creates high-density training data for repository-level multi-turn reasoning.
  - Design 'Regression Trap Feedback' in the Dynamic Conversation scenarios where the feedback for Turn 4 specifically tests a boundary case that was solved in Turn 2 but broken in Turn 3. The synthetic task should mandate that the agent recover the previous turn's success while simultaneously fixing the current turn's error. This forces the agent to perform 'Self-Correction' and 'Constraint Recovery'. For instance: 'The last change broke the handling of 'None' inputs which was working previously; please fix this while adding the new log output.'
  - Require the final output JSON to include an 'Instruction-Following Matrix' in the trajectory that tracks the status of all current VIs (Passed/Failed). Each turn should update this matrix, showing the agent's awareness of the session-level state. This documentation makes the synthesized data valuable for training models to self-evaluate their own multi-turn consistency. A specific requirement is: 'Every code generation action must be preceded by a summary of all active instructions being targeted.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
