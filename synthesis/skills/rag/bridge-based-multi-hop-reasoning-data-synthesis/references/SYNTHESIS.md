# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - **Use natural 'connect the dots' wording.** Write questions that sound like ordinary user requests yet secretly require following a shared entity or concept across documents. Yes/no comparison forms and bridge-entity identification forms work especially well. The wording should not expose the bridge mechanically.
  - **Bind each hop to one claim.** Construct each support document so it contributes one clean claim attached to the shared bridge. Then require an answer that only appears after those claims are connected. This keeps the later trajectory easy to reconstruct.
  - **Insert plausible wrong bridges.** Where possible, include secondary shared entities or topics that could lure the model into a wrong hop chain. The correct answer should depend on selecting the right bridge, not just any overlap. This sharply increases the diagnostic value of the sample.
  - **Vary the answer form after the hops.** Produce bridge-based questions whose final answers are sometimes yes/no, sometimes an entity, and sometimes a computed value derived after the bridge traversal. This prevents the model from associating multi-hop only with one output type. An important edge case is multi-hop followed by a small calculation.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
