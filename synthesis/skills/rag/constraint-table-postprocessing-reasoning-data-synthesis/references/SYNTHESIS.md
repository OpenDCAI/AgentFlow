# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - **Phrase the query around a concrete operation.** Generate questions that naturally ask for the result of filtering, ranking, grouping, reading a table cell, or converting a derived value. Use ordinary user phrasing rather than formal reasoning labels. This makes the skill discoverable through layman language.
  - **Expose the operation only after retrieval.** Distribute the needed operands or constraints across the corpus so the model must first gather evidence and only then apply the operation. Do not embed the full computed answer directly in one passage. That would bypass the intended capability.
  - **Make wrong intermediate states produce wrong answers.** Choose samples where a mistake in row selection, constraint intersection, or conversion clearly flips the output. This increases the training value of the supervision. An operation task should fail for the right reasons.
  - **Vary the operation family.** Create a balanced mix of table lookup, constraint intersection, ranking, light arithmetic, and output-format conversion. This prevents the downstream model from reducing the skill to only one surface form such as simple addition. A diverse operation set better reflects real RAG workloads.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
