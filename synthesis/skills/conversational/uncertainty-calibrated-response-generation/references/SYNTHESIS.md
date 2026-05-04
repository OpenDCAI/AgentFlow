# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'Hinter-Guesser' multi-turn scripts where the User acts as the 'Hinter' providing incremental, truthful clues. The synthesizer must generate a target 'Secret Entity' (e.g., a city/object) and a 5-step hint sequence where early hints are high-entropy (many matches) and late hints are low-entropy (unique match). This forces the synthesized response to demonstrate 'Monotonic Growth' in confidence. Edge case: Clues must be 'Plurality-Safe,' meaning they don't accidentally reveal the answer too early through a unique name.
  - Embed 'Logit-Based Choice Probes' in the instruction set, specifically commanding the agent to calculate P(SUFFICIENT). The prompt should ask: 'Based only on the clues, is this answer the ONLY possible correct choice? A. Yes, B. No.' Outputting the softmax probability for 'A' provides the supervised signal for calibrated confidence. This is more robust than P(TRUE) because it requires the agent to model the 'Hypothesis Space' rather than just its own correctness.
  - Incorporate 'Placebo Audit turns' into the dialogue JSON by injecting uninformative questions. Each synthesized interaction should feature at least one turn where the user asks a 'neutral' question (e.g., 'Do you have all the clues so far?'). The synthesized gold answer must show 'Flat Confidence'—refusing to increase its certainty despite the turn-counter incrementing. This enforces 'Evidence-Groundedness' over 'Sequence-Bias'.
  - Construct 'Uncertainty Calibration Headers' in the assistant's verbal output, where the agent leads with a linguistic hedge matched to its internal P(SUFFICIENT) score. If the logit probability is < 0.3, use 'I'm making a highly uncertain guess'; if > 0.8, use 'I am very confident'. This provides a direct alignment between the model's 'Internal Math' and its 'External Communication.' Edge case: Avoid 'Over-calibration' where the model sounds too confident for an ambiguous set.
  - Design 'Summary-Contrastive Sub-tasks' where the final turn asks the agent to provide both a multi-turn guess and a confidence score for a single-turn concatenation of the same hints. This contrastive data helps the model learn to 'Ignore the Format' and focus on the 'Information Content' when estimating its doubt. The synthesized trajectory must explicitly state: 'History contains info X; Summary contains info X; Confidence should be equal.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
