# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write the question so that Fuzzy Tool Retrieval is required but not named. The wording should sound like an ordinary person describing a multidimensional goal (e.g., 'find a cheap way to do X' or 'look up Y securely'), leaving the hidden structure to force the orchestrator to map to the exact tools.
  - Build one sharp trap that punishes a shallow keyword-matching strategy. Formulate 'Lexically Ambiguous' prompts using tiered adjectives, forcing the model to engage the translation skillset to filter distractor nodes.
  - Keep the answer derivable from the approved trajectory and only from the approved trajectory. Do not compress away the decisive capability comparison chain when synthesizing the final QA pair.
  - When writing the trajectory field, preserve the causal logic of the real exploration. Include the moment where the crucial decision to ignore a distractor tool or evaluate a worker's policy metadata became visible.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
