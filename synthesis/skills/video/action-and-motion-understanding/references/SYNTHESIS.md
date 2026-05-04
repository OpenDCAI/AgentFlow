# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Construct 'High-Frequency Quantitative Queries' that force the model to specify the exact number of actions within a dense window. Use templates like: 'Identify and count every racquet-to-ball contact during the rally from T1 to T2, justifying each count with a brief description of the player's position.' This prevents guess-based counting and forces 1-to-1 kinetic grounding.
  - Generate 'Action-Outcome Causal Prompts' that link a specific stroke technique to its physical result. Formulate questions such as: 'Analyze the technique used at the 5-second mark; based on the racquet angle, why did the ball land in the net?' This secures the 'Why' bridging kinetic execution and environmental feedback.
  - Implement 'Multi-Step Technique Hierarchy Tasks' requiring the model to identify a player's tactic based on recurring action units. Instead of asking 'What is this?', ask 'Based on the three volleys identified in the first half, what tactic is the far-end player employing to win the point?' This synthesizes atomic actions into higher-level technique identification.
  - Design 'Kinetic Intersection and Prediction Tasks' where the model must forecast the outcome of an ongoing movement vector. Use templates like: 'Given the striker's momentum and the defender's current position at T=3.5s, predict if the next shot will result in an intervention or a winner.' This validates the agent's internal physics emulator for high-speed motion.
  - Apply 'Atomic Rationale Mapping' in the ground truth solutions where the answer is broken down into a sequence of verified maneuvers. Each step must be formatted as: 'Step [N]: Action Unit [Type] detected at [Time] by [Subject] resulting in [Sub-Outcome]'. This forces the synthetic data to mirror the structured logic needed for high-fidelity sports understanding benchmarks.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
