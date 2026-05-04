# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write long-form content section by section using the hierarchical plan as the control structure. Before each section, recall its unique role, local budget, and dependency on earlier material. This prevents the draft from devolving into a single undifferentiated stream of prose.
  - Carry forward previous sections during generation to preserve continuity. Use the accumulated draft to shape references, transitions, and terminology choices in later sections. A practical edge case is keeping the same framing of central concepts across all sections instead of reintroducing them inconsistently.
  - Expand through new substance, not recycled summary. When additional length is needed, add evidence, examples, mechanisms, comparisons, or implications that were pre-planned for that section. Do not lengthen by reiterating earlier claims in broader wording.
  - Perform a document-level reconciliation pass at the end. Check for repetition, missing transitions, uneven section depth, and unresolved references across the full draft. If repair is needed, adjust local sections while preserving the global length target and overall structure.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
