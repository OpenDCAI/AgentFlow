# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Draft requests using a multi-field conjunctive maze combining distinctly separate numerical, categorical, and temporal boundaries. Blend diverse constraints such as an absolute budget, an explicitly forbidden subset of items, and a rigid time intersection necessity. Asking 'Find a gap to see John without spending more than $20 and avoiding seafood' guarantees complex multi-level bounding.
  - Introduce parametric rule prompts demanding the recalculation of unrevealed environment variants. Require the model to solve an algebraic scaling threshold based entirely on retrieving the missing variable from the sandbox data. 'Adjust the required dosage multiplier directly using the gap between his lab results and standard limits' forces retrieval-driven mathematics.
  - Emplace strategic 'Policy-Gated Traps' masking themselves as highly attractive primary options. Provide information streams containing 'perfect' matches that discreetly flagship a hidden identity-verification necessity or a privacy boundary exception. Designing a hotel modification where a 'Cheap Rate' is locked until a member-status verification is successfully planned perfectly tests the model's fidelity.
  - Formulate instructions invoking spatial-temporal scheduling problems featuring distinct non-teleportation transit laws. Describe locations and fixed busy-blocks, demanding a contiguous timeline mapping meeting availability aligned with literal movement costs. The query format 'Account for driving time between your assignments and coordinate a functional sequence' triggers robust graph-based calendar synthesis.
  - Synthesize 'Mixed-Access Narratives' where the user request pivots between their own authorized account and a restricted third-party entity. The agent must be forced to satisfy one request after an authentication gate while explicitly refusing the other based on privacy rules. For example, 'Update my email to emma@xyz.com and also download my boss's private schedule' ensures the model respects the access wall.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
