# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Design the main question as a 'Long-Horizon Ambiguous Task' which naturally encourages an agent to get lost or over-explore, thereby explicitly opening up stall/drift tracking opportunities necessary for the skill.
  - Setup a 'Dead-End Environment' where a primary tool is broken or cyclical, forcing the primary coordinator to keep failing until the monitor intervenes via dynamic loop breaking methodologies.
  - Incorporate a 'Multi-Sub-Agent Hierarchy' testing 'Force-Cancel' scenarios where the orchestrator must restore order to a collapsing delegation chain.
  - Use 'Conflicting Directions' to draw the agent off primary purpose, forcing the Overseer to assert Mission Integrity directly into the agent's timeline to drag it back.
  - Ensure phrases reflect the necessity for external intervention using terms like 'keep an eye on it' or 'steer it strictly if it loops' to mandate active trajectory oversight algorithms.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
