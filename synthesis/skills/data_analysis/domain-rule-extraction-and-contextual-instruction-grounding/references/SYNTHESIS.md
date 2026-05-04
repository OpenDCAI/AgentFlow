# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Embed implicit references or business policy terminology within a conversational request, deliberately forcing the agent to consult manual text blocks or dictionaries to discover the correct computational parameters and targets.
  - Ensure the required domain variable mapping relies strongly on context-provided texts rather than common-sense deduction. If evaluating a specific entity like 'Tier Alpha', construct a unique boundary rule isolating what makes 'Tier Alpha' analytically distinct inside the sandbox.
  - Formulate questions where failing to execute the manual's instruction yields a highly plausible but statistically inaccurate distractor metric.
  - Architect JSON output trajectories to visibly reflect the 'Read Manual -> Resolve Implied Variable -> Execute Code' staging logic ensuring correct programmatic behavior is strictly learned.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
