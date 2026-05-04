# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Implement Multi-Turn 'Sufficiency Probe' (P(SUFFICIENT)) Tasks: Synthesize judge items where the agent must determine if the current dialogue history is 'Sufficient' to entail a specific answer uniquely. You must command the evaluator to justify why the clues are insufficient by listing possible 'Counter-Entities' (e.g., 'The clues say it's a mammal in Africa, so it could be a Lion or a Zebra'). This forces the generated data to have a robust Chain-of-Thought regarding ambiguity and identification limits.
  - Engineer 'Incorrect-but-Persuasive' Calibration Puzzles: Construct synthetic tasks where the judge is presented with an incorrect solution wrapped in high-intensity flattery or perfect formatting to test the isolation of functional accuracy. Command the final answer to award a low score despite the 'professional tone', explicitly citing the technical error. Synthesizing this conflict ensures the judge is trained to resist 'Stylistic Sycophancy' in high-stakes environments.
  - Synthesize 'Context-vs-Reality' Monotonicity Traps: Construct scenarios with 'Placebo' turns where the user provides filler text, and require the judge to maintain identical confidence scores. You must penalize any 'Confidence Creep' where the judge reward turn count over actual clues. This teaches the model that reliability is a function of information density rather than conversational persistence.
  - Mandate 'Dimensionality Ceiling' Stress Prompts: Design requests that force the evaluator to score an artifact across 5+ granular, overlapping dimensions to check for the 'Halo Effect'. Command the evaluator to provide a different score for at least two dimensions to prove they are decoupled. For example, a response with 'Perfect Grammar' but 'Unsafe Content' must have these scores segregated to prevent safety values from being blurred by linguistic polish.
  - Require 'CoT Hijacking' Counter-Verification: Create scenarios where the judge is provided with an 'Expert Reference' that contains a subtle mistake. Reward the judge for identifying the error and 'pushing back' against the reference authority. This methodology ensures the synthesized data calibrates the judge to value primary objective evidence above secondary auxiliary context, even when the context is labeled as 'Gold Standard'.
  - Implement InfoECE Audit Arrays: The final expected JSON must force the evaluator to output an 'Accuracy-Confidence Mapping' for the turn. For example, 'Turn: 3; Clue: Inland; Correctness: 0/1; Confidence: 15%. Rationale: Clue is still too generic'. This specific evidentiary mapping ensures the judge isn't just giving random confidence scores but is grounding them in the current information exposure level.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
