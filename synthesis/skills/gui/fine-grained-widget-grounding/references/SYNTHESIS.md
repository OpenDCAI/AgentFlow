# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Spatial Dilution Instruction Seeding: Design synthesis questions for extremely high-resolution (4K) environments where the target widget occupies less than 0.1% of the total screen area. Use language that emphasizes the search challenge, such as 'Find the tiny icon in the dense toolbar' or 'Pick out the specific checkbox in the list'. This forces the agent to utilize the Stage 1 ROI zoom agents rather than attempting a single-shot guess.
  - Application-Context Contextualization: Formulate prompts that are semantically ambiguous without knowing the specific application context, forcing the agent to use the 'Rewrite Agent' logic. Use generic phrases like 'Click Share' or 'Go to settings' in a screen with multiple apps visible (e.g., a desktop with two open windows). This tests if the agent can correctly identify 'Figma Share' versus 'Chrome Share' based on local visual cues.
  - Spatio-Visual Attribute Enrichment: Inject visual trait constraints into the synthesis phase, such as color, shape, or relative positioning, to measure the grounding model's precision. Formulate instructions like 'Click the blue blue button to the right of the text field' or 'Select the circular icon with the white border'. This creates 'Multi-Constraint' grounding tasks where the agent must align multiple visual attributes to verify the target.
  - Asymmetric Refinement Path Trajectory JSON: Construct the 'trajectory' field in the JSON output to explicitly show the sequence of 'Zoom' actions, including asymmetric crops and recovery zooms. Each step must record the 'ROI Bounds' and the 'Observation' of the target's relative size. For example, 'Step 2: Observation shows the toolbar is in view; Action: prune the left boundary by 20% to center the target' ensures the training data replicates Algorithm 2.
  - Scale-Agent-Aware Final Verification: Ensure the final 'Answer' or success state in the synthesis data matches the coordinates of a 3x upscaled image to train for high-precision motor control. You should provide the translated coordinates in the final step to ensure the agent understands the relationship between the crop and the full screen. A concrete answer would be: 'Target identified at full-screen (1920, 1080) based on 3x scaled alignment at ROI (500, 300)'.
  - Attentional Distractor Seeding: Place a visually salient 'Distractor' (e.g., a larger, brightly colored button) near the tiny target to test the agent's discipline against 'Attentional Fixation'. You must ensure the user prompt contains a specific attribute (like a small icon label) that rules out the distractor. For example, placing a giant 'OK' button next to the tiny 'Share' icon and asking for the latter tests if the agent follows specific constraints over visual dominance.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
