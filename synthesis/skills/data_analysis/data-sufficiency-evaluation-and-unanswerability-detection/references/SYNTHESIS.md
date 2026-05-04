# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write questions that sound entirely plausible and typical for the dataset's domain. The prompt should not give away that it is an unanswerable question; it should look like a standard, high-quality analytical request.
  - Ensure the requested variables are completely absent or structurally deficient. Either remove the target column from the dataset or ask for a subset of data (e.g., a specific year or product category) that was filtered out.
  - Make the trap subtle by providing near-miss columns. For example, include a 'price' column but omit 'quantity', so the agent is tempted to guess. This makes the verifiability check meaningful and challenging.
  - Structure the trajectory to show diligent search followed by principled refusal. The synthesized JSON should depict the agent loading the data, searching for the columns, realizing the gap, checking for proxies, and finally outputting the unanswerable rationale.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
