# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Synthesize listwise tasks rather than pairwise clones: Write questions mandating the evaluator to order multiple realistic candidates under a shared user intent, making constraints important enough to resolve intricate tradeoffs.
  - Permutation-inclusive position control: Implement instructions directing the judge to produce consistent orderings irrespective of how the inputs are spatially arranged, explicitly mitigating position bias.
  - Require explicit rationale for adjacent boundaries: The final expected JSON must force the evaluator to execute a Chain-of-Thought listing the exact criteria bounding Candidate 1 to 2, and Candidate 2 to 3, reinforcing listwise consistency.
  - Prioritize user-centric tradeoffs: Synthesize scoring rationales wherein compliance, factual adequacy, and functional structure outrank surface polish, utilizing style only to break existing objective ties.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
