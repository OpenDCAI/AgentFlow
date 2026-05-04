# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Generate Paired or Streamed Tasks: Formulate prompt structures establishing reusable experience through an initial episode acting as context for a subsequent execution challenge.
  - Write Memory-Relevant Later Tasks: Preserve strict procedural motifs linking the earlier and later constraints while diversifying environmental assets to absolutely force on-the-fly adaptation.
  - Encode Retrieved Lessons in Trajectories: In the JSON output, actively map the reuse breakpoint by generating rationale statements like: 'Observation: Closed container. Action: Retrieve prior logic stating container must be opened before manipulation.'
  - Demand Lifelong Learning Retention Checks: Produce queries forcing the agent to execute heavily practiced historical actions subsequent to absorbing unrelated skills to formally evaluate architectural behavioral stability.
  - Keep Answers Tied to Final Task Outcome: Guarantee the answer response logs the grounded physical success or failure result of the embodied transition, maintaining focus strictly on physical task consequences.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
