# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer 'Asymmetric Knowledge Gaps' by providing a competitive goal where the 'Overview' is detailed but the 'Data Structure' is withheld until the agent explicitly requests it. The question should describe the business problem (e.g., 'Predict stock prices') but not the column names or data types. Success is awarded when the agent uses the 'request_info' tool chain to discover the 'timestamp' and 'closing_price' columns and implements a time-aware split. This ensures the synthetic task rewards the 'discovery' phase of the MLE loop.
  - Implement 'Multi-Modality Performance Hurdles' where the agent must solve tasks across divergent ML domains (e.g., a Tabular task first, then an Image task). The instruction should require the agent to adapt its 'toolbox' between turns, shifting from 'Scikit-Learn' encoders to 'Torchvision' transforms. This creates high-density training data for 'Zero-Shot Adaptability' where agents don't rely on a single domain-specific pattern. A successful synthesis will show the agent performing a 'Library Audit' before each new task type.
  - Incorporate 'Hidden Complexity Traps' where the provided 'Sample Submission' implies a different granularity than the 'Goal Description'. For instance, the goal might be 'classify images', but the sample submission requires 'bounding box coordinates'. The question rewards the agent for identifying this mismatch through the 'request_info' feedback and adjusting its entire model architecture (from classification to detection). This tests the agent's 'Critical Interpretation' capability beyond shallow reading.
  - Design 'Scale-Aware Resource Stressors' where the validation set is small enough for a large model, but the private leaderboard set is large enough to trigger a Time Limit Exceeded (TLE). The question should reward the agent for using 'selective execution' or 'caching' to ensure the final submission completes within the 12-hour window. This allows the synthetic data to teach agents to operate responsibly in professional environments. A specific requirement is: 'Your final answer must explain why your model's inference speed is appropriate for the target leaderboard's latency limit.'
  - Require the final output JSON to include a 'Historical Reflection Matrix' that maps specific observed rank results to subsequently attempted architectural changes. Each 'execute_code' step must record the 'Score Delta' (e.g., 'Elo increased by 15 points') and the reasoning for the next optimization. This documentation makes the synthesized data valuable for training models to optimize their own development paths. A requirement is: 'Every code generation must be preceded by a summary of the 'Lesson Learned' from the previous execution result.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
