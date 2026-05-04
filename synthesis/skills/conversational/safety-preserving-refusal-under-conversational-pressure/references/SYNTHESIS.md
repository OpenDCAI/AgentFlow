# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate initial user prompts using 'Innocent Persona Anchors' like establishes a benign role such as 'medical student', 'historical novelist', or 'tourism consultant'. Over the next 5-8 turns, the user must 'drip-feed' constraints that align with a specific malicious category like 'Self-Harm' or 'Tax Evasion.' The synthesized QA pair must show the agent's transition from helpfulness to detection as the 'Malicious Intent' becomes clearer through the accumulated constraints.
  - Incorporate 'Metacognitive CoT Markers' explicitly in the assistant's JSON response using the #Alert and #Warning fields to track its internal state. The synthesized gold response must contain a detailed internal step-by-step reasoning phase that identifies the risk category and severity from the provided paper's frameworks. This provides the 'Instruction-Tuning' signal needed for the model to learn the method of safety reasoning rather than just memorizing refusals.
  - Design 'Crescendo Attack' multi-turn scripts where the user starts with a Level 0 request (e.g., 'How do I lose weight?') and ends with a Level 10 request (e.g., 'How do I starve myself effectively?'). The synthesized refusal must occur precisely at the turn where a health or safety policy is breached, showing the agent identifies the 'Safety Boundary' at the exact moment of divergence. This teaches the model to handle subtle escalations that bypass static keyword filters.
  - Embed 'Indirect Risk and Coded Language' triggers where the simulated user employs raw emotional grounding or symbolic codes to flag a systemic mismatch. Turn 5 of the script should be the user saying, 'The monitor is black,' referring to a code for intense ideation established in Turn 1. The synthesized expert answer must show the agent 'rescuing' the user by providing crisis resources, even when the user turn looks benign to a naive observer.
  - Construct 'Domain-Specific Lures' for all 37 categories, ensuring the synthesized user uses technical or colloquial slang relevant to the specific harm domain. For example, for 'Cybercrime', use 'SQLi' or 'OAuth2 exploit'; for 'Suicide', use 'knot types' or 'rope thickness' (the McBain et al. items). This ensures the synthesized data covers the 'Fine-Grained Alignment' goals of the Safety Reasoning dataset across diverse real-world presentations.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
