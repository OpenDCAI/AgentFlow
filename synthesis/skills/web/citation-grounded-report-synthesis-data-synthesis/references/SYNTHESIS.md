# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write prompts that naturally demand a compact research-style answer instead of a single fact. Good prompts ask for a framework, comparison, synthesis, or evidence-backed recommendation. The challenge should be collecting and organizing web evidence into an answerable structure.
  - Ensure the user request implies multiple evidence categories. For example, a good research synthesis task might require background, methods, trade-offs, and recommendation criteria. This creates a legitimate need for citation-backed composition.
  - Phrase the task so unsupported fluency would be attractive but insufficient. The benchmark should reward grounded, specific synthesis rather than polished but generic prose. As an edge case, avoid prompts so broad that any answer becomes unverifiable.
  - Constrain the expected output to a scoped, checkable report. A short report, memo, or structured answer works better than an unconstrained essay because it keeps grounding auditable. This makes the final synthetic data more useful for training and evaluation.

* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
