# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  * **Write questions that require looking, not guessing.** The prompt should be answerable only after the agent reveals a scene-specific state, count, location, or attribute. During synthesis, explicitly choose questions whose truth value changes across environments and therefore cannot be recovered from generic prior knowledge. Examples include faucet state, exact appliance count, or lamp location relative to visible room anchors.
  * **Tie the answer to observable evidence.** The expected answer should directly reflect something that became visible in the decisive observation. The generator should avoid speculative or inferential answers that extend far beyond what the trajectory actually revealed. A good answer is 'No, the faucet is turned off'; a weaker one is 'No, because you are careful with water usage.'
  * **Preserve open-ended but grounded wording.** Questions may be open-ended, but they should still have a constrained evidence basis and a single best answer. Use everyday phrasing such as 'Did I leave...' or 'Where is...' while ensuring that the scene evidence pins down the response. This keeps the data natural without sacrificing evaluation rigor.
  * **Encode the decisive step in the trajectory.** When constructing the JSON trajectory, explicitly include the step where task-relevant evidence was first observed. This lets downstream agents learn that not every movement matters equally and that one observation can flip uncertainty into grounded certainty. A faucet question should include the turn toward the sink as a trajectory step, not just the initial hallway walk.
  * **Avoid over-broad questions.** Keep the target narrow enough that a single rational exploration path can answer it convincingly. Questions like 'Describe the whole house' should be rejected or decomposed because they blur evidence requirements and make acceptance filtering unreliable. A focused query such as 'How many washing machines do I have?' is much better aligned with this capability.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
