# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - **Write conjunctive or tuple-style queries.** Generate questions whose answer naturally consists of multiple fields or one entity satisfying multiple sourced constraints. Use everyday wording such as 'when were X and Y launched' or 'which movie fits both clues'. These forms make the need for integration intuitive to non-expert users.
  - **Assign one decisive contribution per document.** During synthesis, intentionally distribute the answer pieces so each chosen document contributes exactly one crucial slot or one binding constraint. Do not let any document carry the whole answer by itself. This preserves the capability target during later scaling.
  - **Make incomplete answers obviously wrong.** Choose question forms where providing only one gathered fact produces a visibly incomplete or incorrect response. This sharpens supervision and discourages shallow single-document habits. A good sample should fail loudly when one source is ignored.
  - **Vary source order and document style.** Create versions where the contributing documents come in different orders and use heterogeneous prose styles or metadata layouts. This prevents the model from overfitting to one fixed integration template. An important edge case is one short snippet plus one long article section.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
