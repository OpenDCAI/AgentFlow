# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write prompts that specify a concrete statistical ask. Mention the variables, the relationship or summary of interest, and the required procedure or output type when possible. For example, asking for an R-squared-based fit judgment is far better than saying “analyze whether they are related.”
  - Keep the answer space narrow and objective. Percentages, coefficients, fit labels, and direct comparisons work well because they permit precise evaluation. An edge case to avoid is asking for a broad interpretation essay after a simple computation.
  - Ensure the dataset contains enough signal and support for the procedure. The variables should have sufficient non-null overlap and sensible types so the agent’s task is to analyze, not to rescue a broken dataset. This makes the synthetic data cleaner and more reusable.
  - Represent the trajectory as prepare-then-compute-then-interpret. The JSON should show minimal variable preparation, the exact statistical computation, and the final answer mapping. That concise structure is ideal for training data in this capability.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
