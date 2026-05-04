# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Create 'Perceptual Trap' questions where the intuitive visual answer is the exact opposite of the mathematically correct answer. For example, invert the Y-axis and ask 'Which category represents the lowest value?'; the correct answer will be the visually tallest bar. This forces the agent to rely on structural metadata over generated images.
  - Design synthetic environments with 'Dual-Axis Cross-Scaling' where two related metrics are plotted but only one axis starts at zero. Ask the agent to compare the 'growth rate' or 'magnitude' of the two metrics. The synthesis is successful only if the agent detects the offset baseline and normalizes the two values.
  - Create 'Best Practice Stress-Tests' using high-cardinality charts or excessive 3D effect parameters. Synthesize a dataset with 20 categories and a pie chart script, then ask 'Identify the core message.' The correct answer must involve a critique of the chart's unreadability and a rewrite to a bar chart.
  - Mandate an 'Audit -> Truth-Check -> Fix' trajectory structure in the synthesized JSON output. The agent should first inspect the chart metadata (axis ranges, inversions, slice counts), print the 'True' values from the CSV, calculate the visual distortion, and finally output the corrected code or raw answer.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
