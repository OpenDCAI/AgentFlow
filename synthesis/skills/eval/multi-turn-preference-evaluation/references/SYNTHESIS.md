# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Make the context decisive: Draft questions such that the later turn or the user's historical log acts as the absolute discriminator between the candidate responses.
  - Keep both response candidates near-miss realistic: Preserve the weaker response's surface fluency but introduce a controlled memory failure, such as repeating a previously rejected suggestion or dropping a modified instruction.
  - Implement implicit need and constraint extraction rubrics: Force the generated answer key to score responses based on whether they correctly captured the unstated constraints derived from Turn 1 or previous session logs.
  - Require turn-coupled evidence rationale: Ensure the expected label justifies the verdict by explicitly quoting the user's evolving intent or historical reference and contrasting it with the response's failure or success.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
