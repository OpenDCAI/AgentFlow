# Phase 3: Data Synthesis Instructions
* **Question Generation Rules:**
  * **State the capability target directly in the question design.** Ask for a fact, value, label, or page-local finding whose answer can be pointed to exactly. This ensures the generated example probes the intended reasoning pattern instead of drifting into generic summarization. A good operational check is whether the answer can be highlighted on one page or one tightly bounded region.
  * **Bind the question to document evidence, not to background knowledge.** Use entity names, document-specific fields, local layouts, or source-bound time ranges that force the agent to consult the workspace. The wording should make outside-world guessing unattractive and unhelpful. An edge case is avoiding famous facts unless the required answer depends on a specific phrasing or page structure in the source.
  * **Engineer realistic distractors.** Create distractors that are semantically close but not actually answer-bearing, such as repeated metrics from another company or a nearby chart with a related trend. The distractor should be naturally embedded in the corpus so the task still feels like ordinary document work rather than an artificial puzzle. One practical method is to pair the target evidence with neighboring regions that share surface vocabulary but differ in one crucial attribute.
  * **Keep the answer format evaluable.** Make the expected answer short and normalized whenever possible, such as a scalar, exact phrase, or page-grounded label. This reduces evaluation ambiguity and keeps the synthetic data reusable. If a brief explanation is needed, require that the first clause still contain the normalized short answer.
  * **Write the trajectory from the real exploration path, not from hindsight.** Each step should preserve what was actually seen, what action followed, and why that action was taken. This produces training data that matches agent behavior rather than polished post-hoc rationalization. A concrete example is logging that the agent inspected a wrong page first and then corrected course after detecting a date mismatch.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
