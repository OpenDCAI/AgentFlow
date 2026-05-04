# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Embed 'Update-Centric Conversational Baits' requiring the identification of the 'latest' or 'current' status of heavily repeated entities across long timescales. Construct interactions presenting at least three disparate historical values across conversational history. The generated QA pair must definitively showcase the agent extracting the most recently updated fact completely independently of its initial dialogue location.
  - Incorporate 'Absolute-to-Specific Contradiction Traps' in multi-turn JSON scripts. Design Turn 1 where the user makes an absolute claim ('I only use Mac computers') and Turn 10 where the user asks a question that implies the opposite. The synthesized response must identify the 'Only-Statement' collision and prompt for clarification rather than blindly providing the contradictory PC information.
  - Synthesize 'Maintenance-Trap Interjections' inserting casual pivot language halfway through established dialogues ('Actually, I don't feel like driving the usual route...'). The targeted JSON output must actively display the internal state operation flipping from the original constraint to the appended parameter cleanly, demonstrating definitive real-time context swapping.
  - Engineer Privacy-Opt-Out Variance inquiries heavily entangling highly private or medical data directly alongside standard actionable updates. Configure prompts like 'Take me to the new pharmacy location, my arthritis is agonizing.' Determine success specifically measured by the agent seamlessly executing the 'Update Location' variable while rigorously dropping the 'arthritis' variable from persistent storage.
  - Include 'Evaluation-Goal Anchors' in the JSON trajectory field that explicitly record the 'Provenance IDs' (Turn numbers) of any updated or clashing facts. This provides the instruction-tuning signal for models to learn that every update must be auditable and grounded in a verifiable chronological timeline event.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
