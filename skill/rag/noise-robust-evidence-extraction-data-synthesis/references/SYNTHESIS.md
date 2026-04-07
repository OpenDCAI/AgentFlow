# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - **Ask for one sharply defined slot.** Generate questions that request one explicit field such as a winner, date, value, or label, so evaluation remains crisp. Phrase the query in ordinary language and avoid adding extra subtasks that would change the capability target. A good example is asking for a specific year’s winner rather than a broad narrative summary.
  - **Inject related but non-answer-bearing passages.** Design distractors to be topically close, lexically similar, and factually true, but still non-decisive for the asked slot. Use adjacent years, sibling entities, same-report sections, or same-award categories as distractor generators. This creates realistic retrieval noise instead of artificial nonsense.
  - **Make the answer depend on the discarded contrast.** The final question should be incorrect if the model follows the strongest distractor rather than the precise supporting span. During synthesis, confirm that replacing the decisive passage with a distractor flips the output. That property guarantees the sample actually teaches robustness.
  - **Vary document order and verbosity.** Produce multiple versions where the correct evidence appears early, late, terse, or verbose, while keeping the answer unchanged. This prevents the model from learning positional shortcuts instead of evidence filtering. An edge case worth keeping is when the distractor is longer and stylistically richer than the true support.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
