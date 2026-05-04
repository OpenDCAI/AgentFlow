# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Apply 'Anchor-Point Drafting' when executing local rephrasings. Place the protected technical invariants (measurements, negation) into their new positions within the localized span first, then fluidly wrap the varying syntax around them.
  - Execute editing with an intent on 'Minimal Diff.' Implement purely the smallest necessary textual patch to accomplish the user's deletion or insertion demand, completely resisting the urge to 'clean up' unrelated surrounding prose.
  - For insertion bridging, lock the 'Poles' immediately. Write the first sentence of the inserted span to act as a direct syntactic extension of the prefix, and write the final sentence to act as a direct causal trigger for the suffix.
  - Perform a final 'Diff and Invariance Audit' on the document. Run a stringent check verifying no unprotected regions suffered alterations, and confirm that all items tracked in the Invariant Ledger perfectly survived the finalized patch.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
