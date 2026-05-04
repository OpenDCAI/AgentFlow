# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate user questions in ordinary, fragmented language. Use informal openings like 'I found this trick math puzzle' or 'I just started my job' rather than providing sterile problem blocks.
  - Incorporate 'Cognitive Load and Social Tension Hooks' where the user expresses confusion ('run that step by me again') or idleness, forcing the model to generate pedagogical or proactive, rapport-building open-ended responses.
  - Embed 'Correction/Pivot Traps' where the user proposes a flawed logical shortcut or gives a low-entropy 'yeah' response. The gold response must respectfully correct the logic (face management) or proactively pivot the topic to maintain engagement.
  - Include explicit evaluation metadata in the JSON output tracking both the 'Reasoning Rationale' (is the logic sound?) and 'Rapport Strategy' (is the tone sufficiently engaging and respectful of the user's face?).
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
