# Phase 3: Data Synthesis Instructions
* **Question Generation Rules:**
  * **Name the schema explicitly in the prompt.** The question should tell the agent which label inventory or field template governs the task. This prevents drift into generic interpretation. A practical pattern is “Classify under the X schema” or “Extract the following fields under the Y annotation rules.”
  * **Use source snippets that can justify the output tightly.** Prefer examples where one sentence or one clause clearly supports the chosen label, or where a small span supports a structured field. This keeps the synthetic dataset auditable. An edge case is a multi-sentence note where only one line should be used despite lots of nearby irrelevant context.
  * **Include near-miss negatives intentionally.** Some generated items should contain semantically related language that does not actually satisfy the schema. This teaches the model to obey definitions rather than keywords. A good example is a relationship mention that is non-adverse next to a genuinely adverse relationship example.
  * **Keep the answer normalized and compact.** The expected output should be a label, subtype, Boolean status, or structured field set with stable formatting across instances. This improves downstream reuse and scoring. If explanations are included, place them after the normalized output rather than instead of it.
  * **Write the trajectory as an annotation trace.** The path should show which span was read, which schema rule fired, and how the normalized label was chosen. This mirrors real document annotation behavior much better than a polished prose explanation. A concrete example is “observe phrase about missing transport,” then “apply transportation-adverse rule,” then “emit normalized label.”
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
