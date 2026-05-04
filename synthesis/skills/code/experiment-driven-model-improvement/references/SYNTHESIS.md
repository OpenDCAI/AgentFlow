# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Frame the prompt around improving an existing experimental setup or developing a specific algorithmic intervention rather than inventing a project from void. Provide a real starter codebase and define strong objective metric targets.
  - Embed explicit artifacts that support disciplined experimentation: starter code, data descriptions, evaluation details, and baseline execution commands. These empower the agent to diagnose true bottlenecks.
  - Include multi-objective resource traps or algorithmic misdirections. For example, explicitly penalize solutions that increase runtime beyond a specific limit, forcing agents to pick surgical, elegant interventions over brute-force scaling.
  - Require the final QA pair to capture the complete scientific cycle: observation of the baseline metric, hypothesis generation, specific architectural/algorithmic code changes, execution, and confirmation of objective metric improvement.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
