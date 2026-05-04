# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Generate the response from the outside in using 'Segment-Wise Blueprinting'. Emit the immutable shell, formatting markers, and required headings exactly as planned, then populate each slot.
  - Implement 'Variable-Locked Injection'. Insert user-provided constants (such as rent integers or specific names) as immutable strings into pre-defined structural slots to prevent semantic simplification.
  - Use deterministic wording for all exact-match surfaces. Required wrappers, titles, and hierarchical boilerplates should be directly cloned from the normalized constraint ledger.
  - Run a final compliance sweep on the assembled document. Count visible sections, audit exact-match opening/closing tokens, and surgically delete any AI conversational pleasantries to achieve complete 'Prose-to-Structure Containment'.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
