# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Use natural 'connect the dots' wording. Write questions that sound like ordinary holistic user requests but secretly require following a shared entity or sequence through isolated documents. Good formats include yes/no comparisons over distinct articles or naturalistic requests to navigate nested system functions.
  - Bind each individual hop explicitly to one claim or milestone. Construct each supporting text chunk so it contributes precisely one necessary segment attached to the shared bridge. Ensure the required answer is exclusively solvable by appending these segments end-to-end.
  - Insert plausible wrong-bridge decoys. Deliberately construct secondary shared entities or adjacent menu clusters that lure the reasoning matrix into constructing the wrong sequence. The correct trajectory must depend on discriminating these decoys away using deep context.
  - Vary the terminal answer classification formats. Produce multi-hop data resolving into various categorical schemas: a final Boolean conclusion, a sequential numbered layout of steps, or a specific computed numeric delta, preventing the model from associating 'multi-hop' formatting solely with one answer style.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
