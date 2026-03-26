# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write questions in natural task language and let the documentation carry the technical specificity. The prompt should ask for a real analytical quantity, while the codebook or manual contains the exact variable names and rules. For example, ask for median household income rather than naming the documented field directly.
  - Make the documentation necessary but not overwhelming. The answer should depend on one to three decisive definitions such as variable meaning, population scope, or weight usage, not on arbitrary scavenger hunts across the full manual. An edge case to avoid is requiring ten unrelated document lookups before any analysis can start.
  - Include enough room for plausible variable confusion. Good prompts should create realistic alternatives, such as household versus personal income, annual versus monthly measures, or raw versus adjusted values. This forces the agent to ground the question in the documentation rather than rely on prior assumptions.
  - Ensure the synthesized trajectory records both document access and final schema commitment. The JSON should show that the agent searched or read the right sections, extracted the needed rules, and then transitioned into code execution with the correct variables. That structure is the essence of documentation-grounded data analysis.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
