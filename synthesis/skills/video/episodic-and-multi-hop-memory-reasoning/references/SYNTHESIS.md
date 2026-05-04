# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Construct 'Semantic-Anchor Verification Queries' that force the model to first identify an unstated entity or room before performing a memory lookup. Use templates like: 'Given you saw a mirror at T=10, where did you find the item most likely related to it?'. This forces the agent to (1) perceive the anchor, (2) identify its semantic neighbors, (3) search for targets, and (4) verify the final placement.
  - Generate 'State-Change Verification Tasks' that require the agent to confirm if a specific environmental rule or state was maintained across a long gap. You should draft questions like: 'Based on your visit to the kitchen at T=20, is the toaster still plugged in at T=500?'. These questions mandate that the agent performs a 'History Scan' to find the interaction segment corresponding to the toaster, ensuring long-term state tracking.
  - Implement 'Multi-Choice Distractor Calibration' where incorrect options reflect 'typical' object locations (priors) versus the 'actual' documented location (episodic fact). First, look for distractors based on common house habits (e.g., 'shampoo is on the sink'); then, set the correct answer to the unique location found in the video (e.g., 'on the blue chair'). This tests if the agent possesses 'recency bias' toward standard habits or true episodic memory recall.
  - Design 'Calibrated Relevance Reasoning Prompts' that ask the agent to justify why a previous observation helped it find a later target. Formulate prompts like: 'Which specific object seen earlier served as a clue for your current search, and why was it relevant?'. This forces the agent to explicitly link the semantic trigger (e.g., sink) to the visual outcome (e.g., soap), confirming it understands the multi-hop methodology of the synthesized data.
  - Apply 'Interaction-Anchored Contextual Inquiries' that use 'I/You' personal pronouns to simulate a memory assistant relationship. First, identify the exact moment an object was last touched and anchor the question to the user's past actions: 'Where did I leave my keys after entering the bedroom?'. The answer should be formatted as: 'You placed them on the nightstand next to the lamp', ensuring adherence to the verified spatial path.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
