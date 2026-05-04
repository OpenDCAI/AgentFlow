# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write prompts that sound like realistic analytics requests while preserving answer unambiguity. The wording may be natural and business-like, but the required output should still be determinable through the provided schema, docs, and dialect references. Avoid bluntly restating the full SQL structure in the question.
  - Ensure the environment exposes large-schema friction. Include enough tables, columns, or nested structures that the agent must perform real linkage and not simply pattern-match a toy database. This is crucial for preserving the difficulty profile of the source benchmark.
  - Include at least one dialect-sensitive operation that punishes generic SQL completion. Date truncation, safe division, array access, geospatial functions, or warehouse-specific syntax all work well. The trap should be realistic rather than adversarially obscure.
  - Require the answer to reflect both correct SQL generation and grounded reasoning steps in the trajectory. The synthetic JSON should show schema inspection, doc consultation, and execution-led refinement. That makes the final data useful for training code agents rather than plain text-to-SQL parsers.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
