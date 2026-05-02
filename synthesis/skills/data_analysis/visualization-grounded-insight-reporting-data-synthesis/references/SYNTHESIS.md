# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write prompts that require both analysis and presentation. The user should ask for a chart, saved artifact, report, or concise insight summary in ordinary language. This creates realistic tasks where communication quality is part of the analytical deliverable.
  - Tie the reporting output to explicit artifacts or computed values. Good prompts mention files like figure.pdf or data.txt, or ask for a PDF report with named sections. This makes the communication step objectively inspectable.
  - Encourage concise, evidence-linked statements rather than generic narration. Bullet points, short report sections, or structured summaries work well because each claim can be grounded in a specific computed pattern. An edge case to avoid is asking for a long open-ended essay about the dataset.
  - Represent the trajectory as compute-visualize-summarize. The JSON should show the analysis step, the artifact-saving step, and the final grounded explanation step in that order. That pattern is the reusable core of visualization-grounded insight reporting.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
