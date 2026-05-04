# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  * Write the question so that **Schema Compliance** is required but not named. The user-facing wording should sound like an ordinary person describing a goal, while the hidden structure should force the orchestrator to demonstrate the target coordination skill to succeed. For example, avoid API-like phrasing unless the entire purpose is to test whether the agent can translate messy human intent into the exact orchestration pattern.
  * Build one sharp trap that punishes a shallow strategy specific to **Schema Compliance**. The trap should be logically fair: a strong agent can avoid it by paying attention to the trajectory evidence, while a weak agent will predictably stumble into it. A good edge case is a near-correct path that fails because one dependency, parameter, citation, scheduling decision, or trust judgment was mishandled.
  * Keep the answer derivable from the approved trajectory and only from the approved trajectory. Do not introduce answer content that was never observed during exploration, and do not compress away the decisive evidence chain when synthesizing the final QA pair. If a concise answer would hide the capability under test, prefer a slightly longer answer that preserves the critical grounding signal.
  * When writing the trajectory field, preserve the causal logic of the real exploration rather than rewriting it into a perfectly linear textbook solution. The synthetic example should still feel executable, auditable, and faithful to the accepted trace, including the moment where the crucial decision for **Schema Compliance** became visible. An important edge case is a trajectory with a failed attempt or rejected branch; include it if it clarifies the capability boundary and does not create noise.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
