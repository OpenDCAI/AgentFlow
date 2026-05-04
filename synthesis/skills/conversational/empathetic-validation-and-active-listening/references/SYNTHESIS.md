# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate initial user prompts using 'Ambiguous Distress Seeds' expressing strong emotion while only hinting at the cause. Start the script with 'I can't believe this is happening again' or 'I feel not myself lately', forcing the agent to initiate the 'Fostering' and 'Gathering' phases rather than guessing the problem correctly in one turn.
  - Incorporate 'Implicit-to-Explicit Need Transitions' across a 5-turn script. Design turn 1 where the seeker wants 'Validation', and turn 4 where they pivot to needing 'Expert Guidance' or a 'Solution'. Test if the synthesizing agent updates its internal 'Needs' tracking.
  - Design 'Intentional Misalignment Traps' providing a prompt with a clear emotional need overshadowed by a minor technical detail. The synthesized gold response must prioritize the emotional intention over the technical instruction, proving empathy takes precedence.
  - Construct 'ICECoT Full-Trace Outputs' encompassing internal reasoning fields within the final JSON assistant turn. Output pairs must include {State_Analysis: {...}, Inferred_Intention: "...", Strategy_Selected: "...", Response: "..."} to enforce explicit supervised step-by-step psychological tracing.
  - Embed 'Evaluation Hooks' where the user directly asks 'Why me?' or 'Why do I feel this way?' mid-conversation. The synthesized gold response must prioritize clear, compassionate 'Sensemaking' that bridges the empirical facts of their situation with deep emotional validation.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
