# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Design synthesis prompts that require 'Multidimensional Discovery' where the user's intent spans several related metrics (e.g., 'Emissions' and 'Inequality'). The prompt should be framed as a request for a 'Decision-Ready Report' or a 'Comprehensive Insights Deep-Dive' rather than a single calculation. This forces the agent to plan an outline and decide which charts are necessary to support a complex, tiered narrative. An edge case is asking for a 'Comparison of historical and current trends,' which mandates multiple visual hops.
  - Incorporate 'Interpretive Traps' where the raw chart image contains a subtle pattern (like a plateau or an anomaly) that the narrative must catch. For example, provide data where a trend reverses in the last year; the synthesis is only correct if the agent's textual summary explicitly notes this 'Recent Downturn' visible in the chart. This tests whether the agent is actually 'looking' at its evidence or just generating generic text based on the prompt's tone. This ensures high-fidelity text-chart grounding.
  - Mandate the use of 'Interleaved Visualization Request' tags (e.g., `<visualization>`) in the synthesized response format. The question should be written such that the answer is impossible to provide without creating a series of visual landmarks. This ensures that the generated training data reinforces the 'writing-time evidence construction' paradigm over obsolete text-first paradigms. A successful synthesized example will show the narrative pausing exactly when a quantitative claim needs proof. This structure is critical for training agentic reporting habits.
  - Create 'Platform-Specific Reporting Contracts' where the final output must be a suite of artifacts (e.g., a PDF report, a figure file, and a data summary file). The prompt should specify that 'insights must be saved to data.txt and charts to figure.pdf.' This forces the agent to manage its environment and ensures that the communication is grounded in saved objects that can be audited. An edge case is requiring a 'Summary Dashboard' as the final chapter, testing the agent's ability to aggregate previous findings into a single visual.
  - Include 'Constraint-Based Insight Synthesis' where the agent is forbidden from using specific pre-trained knowledge and must rely only on the generated chart. For example: 'Base your longevity analysis purely on the regional gap visible in your plot, ignoring typical biological assumptions.' This ensures the agent exercises 'Critical Grounding'—the ability to report what the *actual* data shows in the sandbox rather than what it *expects* it to show. This is essential for preventing model bias in scientific reporting.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
