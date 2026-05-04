# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - **Schema-Grounded Parameter Injection.** Formulate the final question specifically using constraints and values that demand an underlying system change. Use verbs like 'create', 'update', or 'commit' followed by an explicit object to be verified.
  - **Hide the direct surface cue.** Ensure the wording does not collapse easily into matching simple text prompts on screen. Request verifiable outcomes, requiring the agent to search out confirmation parameters (like file paths or DB labels).
  - **Implicit Logic Constraint Embedding.** Include subtle rules in the prompt that mandate multi-step verifications. Frame instructions like: 'Do not save unless the state allows' or 'Count only the records flagged as finalized in the backend.'
  - **Plant one controlled distractor.** Include a plausible distractor, such as a screen that appears superficially complete even though the final save or runtime event has not occurred, forcing disciplined verification.
  - **Constrain the final answer.** Keep the final answer format short and dependent entirely upon the durable verification step. Formulate an answer string that is mathematically equivalent to the exact record metric or debug execution state triggered.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
