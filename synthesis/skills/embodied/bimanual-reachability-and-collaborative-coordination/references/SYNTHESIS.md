# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Compose Reachability-Dilemma Prompts: Generate questions that place objects at the borders of each arm's workspace to force the model to calculate reachability. For example: 'There are blocks on the far edges and one in the center; which arm is best for the red one on the right, and why?' This explicitly targets the 'Tier 1' spatial awareness from research. A good distractor would be suggesting the left arm for a far-right object and asking the model to correct the plan.
  - Synthesize Multi-Arm Role-Assignment Logic: Create instructions that define a clear 'Tool Arm' and 'Support Arm' role for a task. Phrase the prompt as: 'Use your left hand to hold the container steady and your right hand to drop the beads into it.' This forces the synthesis of a trajectory where arms maintain separate but synchronized state-machines (one holding, one moving).
  - Generate Parallel Execution Deconfliction Queries: Produce tasks where two unrelated items must be moved simultaneously into a shared container. The question should ask: 'How will you coordinate both arms to avoid a collision while placing both items in the center at once?' This requires the output to generate a reasoning trace for spatial deconfliction and timing offsets.
  - Incorporate 'Arm Interference' Feedback: Synthesize training cases where the first branch of the plan fails because an arm is 'too far' or 'blocking its own view'. The question should provide the error feedback: 'Action failed: Right arm cannot reach; left arm is in the path.' The expected answer must show the agent successfully replanning by moving the interfering arm to 'home' first.
  - Standardize Bimanual JSON Trace Formatting: Every generated QA must output the command set for BOTH arms at every time step, even if one arm is idle. Use a structured JSON field like: `["Left_Pose_X,Y,Z,Q_Gripper", "Right_Pose_X,Y,Z,Q_Gripper"]`. This ensures the downstream student model learns to maintain a consistent 16-dimensional world state for dual-arm control at all times.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
