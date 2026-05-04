# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write prompts that make the cleaning rule operationally precise. Name the target column or structure, the method to use, and any threshold or postcondition needed for automatic evaluation. For example, an outlier question should specify Z-score and the threshold rather than saying “find abnormal points.”
  - Use realistic data imperfections that a disposable analysis script can handle. The task should be solvable with ordinary sandbox tools such as pandas, numpy, and simple statistical functions. Avoid requiring production-grade data engineering or cross-system ETL.
  - Keep the final output compact and deterministic. Counts, booleans, cleaned shapes, or short lists work well because they isolate whether preprocessing was correct. An edge case to avoid is a free-form narrative about data quality with no objective target.
  - Make the trajectory show diagnose-then-clean-then-answer. The JSON should reflect that the agent first inspected the problem, then applied the specified cleaning rule, and finally computed the requested result. That sequence is the reusable core of this capability.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
