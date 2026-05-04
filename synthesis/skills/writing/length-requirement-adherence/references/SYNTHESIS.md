# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  * Allocate length before drafting prose. Decide the budget per field, paragraph, or section, and then write within that envelope rather than writing freely and counting afterward. This is especially effective when the task includes both mandatory keys and a hard upper bound.
  * For short outputs, maximize semantic density from the first sentence. Use direct answer-first phrasing, eliminate ornamental transitions, and prefer compact constructions that preserve required information. A concrete edge case is answering a factoid question with labeled values instead of a narrative explanation.
  * For long outputs, expand through planned substance rather than sheer continuation. Move section by section, preserve prior context, and ensure each new block contributes fresh scope or fresh depth. An important example is a serial long-form article where each section develops a distinct historical phase rather than rephrasing the introduction.
  * Perform a last-mile adjustment that is local, not destructive. If the draft is slightly long, trim optional examples or compress duplicated transitions; if it is slightly short, add pre-planned evidence or clarifying detail in designated slots. Do not rewrite the whole answer at the end unless the mismatch is structurally catastrophic.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
