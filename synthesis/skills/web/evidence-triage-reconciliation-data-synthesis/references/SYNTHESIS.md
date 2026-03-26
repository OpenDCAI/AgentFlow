# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write questions that naturally attract multiple high-surface-relevance answers. The best prompts make search engines return snippets that look right while hiding an important qualifier such as time, first occurrence, scope, or entity identity. This creates a controlled environment where triage matters.
  - Embed a decisive but easily overlooked comparison condition in the question. Words like “most recent,” “first time,” “as of,” “excluding,” or “officially” are useful because they create room for near-miss evidence. The edge case to avoid is a condition so subtle that the task becomes a wording trick instead of an evidence-reasoning challenge.
  - Ensure there exists at least one page that supports the wrong candidate in a plausible way. The wrong page should not be fabricated; it should be a naturally occurring result that is relevant but ultimately insufficient. This makes the synthesized data reflect the real failure mode of trusting the first convincing result.
  - Keep the answer format simple while making the validation path demanding. A single company name, date, or ranked choice is ideal because grading stays easy. The complexity should come from evidence comparison, not from generating a long explanation.

* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
