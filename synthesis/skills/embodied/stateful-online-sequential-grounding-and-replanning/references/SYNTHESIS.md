# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Draft Hierarchical Sequential Prompts: Generate questions containing 3 to 5 sequential tasks connected by terms like 'First', 'Then', and 'Finally' to explicitly enforce temporal order requirements.
  - Construct Segmented Progress Queries: Formulate questions that explicitly present the full multi-step instruction and retrospectively ask: 'Based on the video history, which segment did the agent just finish?'.
  - Inject State-Dependent Pronominal Constraints: Utilize phrases like 'it' or 'the previous location' to force the output to actively reference the stored historical coordinate buffer to progress.
  - Document Sub-Goal Completion in JSON: The trajectory output must include a status field for each step (e.g., 'active_milestone', 'progress') to provide granular supervision for walking through the plan.
  - Incorporate 'Failure to Find' Scenarios: Produce tasks where a milestone target is obstructed, prompting the agent's output JSON to organically generate an alternative exploration sub-task.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
