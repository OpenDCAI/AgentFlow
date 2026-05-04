# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Principled Resister and High-Pressure Elicitation Configurations: Formulate the initial user prompt to directly represent a 'Principled Resister' expressing a specific, articulated objection to a policy, or as a 'High-Pressure Technical Reviewer' highlighting profound systemic weaknesses (Soundness, Presentation). This sophisticated starting structure forces the agent to use interactive information gathering to assemble a highly targeted, multi-part rhetorical or technical rebuttal strategy instead of offering a blanket generic essay.
  - Rhetorical Bait and Methodological Traps Integration: Incorporate 'Rhetorical Bait' deeply within the user's phrasing utilizing trigger words explicitly tied to fairness, monetary cost, or deep-rooted tradition. Simultaneously, utilize 'Implicit Methodological Trap' questions targeting deliberate but seemingly counter-intuitive technical design choices (e.g., 'Why is the learning rate so alarmingly high?'). The ultimately synthesized answer must aggressively defend that specific choice, demonstrating absolute and uncompromising stance maintenance.
  - Multi-Turn Escalation and Global Response Orchestration: Design multi-turn JSON dialogue scripts where the user's resistance tangibly escalates or abruptly shifts focus immediately as the agent attempts to provide conflicting evidence, actively challenging the new variables introduced in prior bounds. Embed 'Global Response Integration' hooks directly within the prompt hierarchy by commanding the agent to concisely summarize its general conceptual defense before progressively dismantling specific turn-by-turn granular queries.
  - Accuracy-Trap Operations and Score-Logic Tracking: Embed demanding 'Accuracy-Trap' conditions where the simulated user forcefully demands highly specific dollar-for-dollar ROIs or asks obscure quantitative questions that are exceptionally difficult to answer correctly but disastrously persuasive if bluffed. Include a structured 'Score-Logic' metadata field precisely tracking the mathematically 'Predicted Reviewer Score' or 'User Belief Shift' following each conversational turn, thereby establishing explicit supervised signals for metric-driven generation optimization.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
