# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Incorporate massive-scale priors or chained landmarks. Question generation should initially establish a global constraint—such as referring to a specific map zone, a massive landmark, or a regional coordinate—before attaching the final focused query. This forces the downstream model to utilize its macro-navigation skills before initiating detailed movement. A robust pattern binds a natural language intent (e.g., 'check for fires') directly to a spatial macro-anchor (e.g., 'around the northern industrial sector').
  - Enforce payload diversity after spatial grounding. Once the geographic area is firmly established in the prompt, intentionally vary the semantic payload to cover recognition, detailed attribute checking, rigorous counting, or existence verification. This multifaceted approach ensures that the single cross-scale navigation skill supervises a wide array of semantic capabilities. For example, after routing the agent to a target warehouse, alternately ask its color, what vehicles are present, or whether its loading docks are occupied.
  - Craft naturalistic, mission-style language. The synthesized prompt should read exactly like a professional dispatch instruction or a highly descriptive natural user request in a massive environment. It is crucial to avoid dry, purely symbolic coordinate lists; instead, blend geographic terminology (e.g., 'the intersection of the main highway', 'the eastern wing') with conversational goals. This maintains the critical bridge between casual intent and expert spatial execution.
  - Derive distractors from partial-chain errors. When synthesizing multiple-choice or negative examples, design the distractors to map perfectly to the physical mistakes an agent would make if it aborted the landmark chain prematurely. Generate incorrect answers based on the attributes of a similarly colored car parked near the *wrong* building in the same district. This brilliantly punishes shallow, lazy exploration models that stop at the first superficial match.
  - Demand explicitly grounded, concise answers. The final generated answer must be punchy and direct, yet unmistakably tied to the physically verified coordinate or terminal landmark. Avoid sprawling, novelistic summaries unless specifically demanded; provide exactly the color, integer count, named entity, or boolean judgment derived from the final view. This absolute operational precision is fundamental to maintaining automated, high-fidelity downstream evaluations.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
