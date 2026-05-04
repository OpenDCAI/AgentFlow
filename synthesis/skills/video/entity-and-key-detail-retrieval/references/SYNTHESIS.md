# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Construct 'Entity-Centric Relational Queries' that explicitly ask for the comparative state of a target object relative to surrounding distractors or the background. Use tightly structured templates like: 'Identify the red cube among the distractors; does the robot successfully interact with it or is it physically blocked by the blue block at T=4s?'. This format forces the underlying model to perform rigorous slot decomposition, target identification, and interaction verification sequentially.
  - Generate 'Robustness-Check Prompts' that actively require the agent to ignore introduced visual noise, irrelevant motion, or sudden environmental shifts. You should draft uncompromising questions mirroring: 'Despite the aggressive change in table color from black to grey mid-task, can you confirm the exact final resting position of the isolated red cube?'. This mandates that the agent demonstrates pure 'Object-Centric Generalization' and proves its feature retrieval remains independent of background training bias.
  - Implement 'Interaction-outcome Verification Tasks' focusing explicitly on analyzing the physical result of two retrieved entities engaging each other. Formulate precision-driven questions such as: 'Analyze the precise moment the machine grippers close; specify if they have fully captured the red cube or if the cube slipped due to poor geometric alignment?'. This secures the causal 'Why', successfully bridging fine-grained static entity retrieval and dynamic kinetic motion understanding.
  - Design 'Adversarial Presence Nullification Queries' that operate specifically to hunt for and verify objects structurally absent from the validated rendering zone. You should integrate templates explicitly mirroring: 'Is there a(n) [Absent Object] functionally observable directly adjacent to the [Visible Landmark] within the 30-second window?'. Establishing these deterministic endpoints enforces strict logical outputs confirming structural deprivation over lazy omission.
  - Generate 'Downstream-Variable Extraction Challenges' that categorically require the agent to isolate specific numbers, background text, or precise category names expressly intended for external tool workflows. You should formulate rigid extraction prompts like: 'Extract the license plate number and the specialized delivery company name shown at T=12s so it can be properly verified in an external database.' Establishing these structured outputs forces the agent to act as an infallible visual parser bridging raw pixels to subsequent multi-agent reasoning loops.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
