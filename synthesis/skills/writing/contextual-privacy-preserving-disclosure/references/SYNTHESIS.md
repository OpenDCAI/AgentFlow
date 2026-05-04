# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  * Draft the message from a safe-content whitelist rather than from all observed facts. Only facts that have been cleared as appropriate for this recipient and channel should be eligible for inclusion. This sharply reduces accidental leakage during fluent generation.
  * Prefer minimal adequate disclosure. State only what the recipient needs to know to accomplish the communication objective, and generalize or omit anything more specific than necessary. A concrete edge case is reporting “professional development activities” without detailing recruiter names or companies.
  * Use substitution and abstraction where they preserve task value. If a sensitive detail explains context but is inappropriate to share, replace it with a safer professional framing or use a different supporting fact altogether. This is often better than either blunt leakage or total refusal.
  * Run a final privacy scan on the completed message before returning it. Check for direct secrets, paraphrased secrets, and implication chains that a recipient could reasonably interpret. If a risk remains, revise the unsafe phrase locally and keep the rest of the helpful message intact.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
