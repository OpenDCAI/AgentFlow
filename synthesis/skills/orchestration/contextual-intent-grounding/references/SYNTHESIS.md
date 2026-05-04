# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate the main question using 'Action-Only' phrasing that describes a goal (e.g., 'Add my latest paper to the site') while intentionally omitting all formatting, structural, or metadata requirements. The objective is to lure the model into a 'Generic Execution' trap where it assumes standard formats, only to fail if it doesn't audit the existing environment first. An example is asking to 'register these new students in the database' where the database has a non-standard naming convention discovered only through inspection. This forces the model to engage the contextual grounding skill to survive.
  - Incorporate a 'Template Contrast' where the user request is framed in one style (e.g., informal prose) but the environment state strictly uses another style (e.g., technical JSON snippets). This tests the orchestrator's ability to 'translate' messy human intent into the established 'Administrative Reality' of the workspace. A concrete trap is asking to 'give Alice a 10 for the quiz' in a Canvas-like environment where the scores are actually tracked as decimals or percentages in the existing sheet history. This pushes the agent toward domain-specific mapping over literal translation.
  - Set up a 'Structure Prerequisite' trap by nesting the target items deep within an environment where the 'where' is as important as the 'what.' Use an instruction like 'Post the news to my blog' when the blog has multiple categories and years, forcing the orchestrator to navigate the folder hierarchy to find the current active path. An important edge case is placing 'fake' or 'stale' folders in the root to see if the agent can identify the 'current' one by checking modification dates or sibling file counts. This mandate tests hierarchical state awareness.
  - Design the prompt as a 'Continuation Task' (e.g., 'Finish filling out the audit for me') where 90% of the constraints are hidden in the first 10% of the work already done by a 'human.' This essentially turns the environment itself into the primary 'Instruction Manual' for the task. For example, a partial CSV with 5 custom-formatted rows is provided, and the agent must add 5 more. This mechanism guarantees that 'Internal Memory' is useless and only 'Environment Observation' can lead to success.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
