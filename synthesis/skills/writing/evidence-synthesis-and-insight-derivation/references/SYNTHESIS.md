# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Structure the output heavily around overarching 'Analytical Themes' rather than leaning upon the original 'Information Source' boundaries. Establish targeted headings and populate them comprehensively with overlapping insights from multiple diverse sources.
  - Implement rigorous 'Mechanism-to-Impact Verbalization' across every single technical or judicial finding within the synthesized response. Explicitly define what the factual mechanism involves, closely followed by clear phrasing declaring what it signifies for the broader objective.
  - Deploy robust 'Bridging Transitives' continuously to inextricably link raw evidence, contextual frameworks, and ultimate conclusions. Employ linguistic markers such as 'Consequently' or 'Pursuant to [Rule], given that [Fact]' to make the internal deductive reasoning entirely visible.
  - Deploy 'Tabular and Sectional Consolidation' when orchestrating extreme volumes of fragmented evidence. Generate precise Markdown tables or highly categorized bullet architectures to densely cluster parallel methods, milestones, or metrics cleanly without rhetorical bloat.
  - Conduct a stringent 'Logic-Gap Sweep' across the final synthesized draft to guarantee no analytical conclusions materialized randomly out of thin air. Check if any final verdict is reached lacking an explicit prerequisite fact-integration phrase beforehand.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
