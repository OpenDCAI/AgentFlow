# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Apply 'Imagery-First Anchoring' by opening every major description with a specific sensory detail before providing the abstract label. Write 'The sun ignited the dew on the meadows (Sensory Detail) before the beauty of the day took hold (Label).' This grounds the reader before dispensing judgment.
  - Synthesize the conclusion using 'Motif Reconstruction.' Reach back into the first paragraph, select the primary metaphor, and re-frame it to show progression. If the intro mentions a 'locked door,' the conclusion must mention the 'found key.'
  - Execute sweeping 'Diverse Token Injection' mid-generation: routinely check the text's cumulative vocabulary distribution. Radically replace duplicate mid-frequency verbs and adjectives with highly specific, domain-aware synonyms to enforce a steeply growing Type-Token distribution.
  - Perform a final 'Standardization Purge' prior to final output. Scan for vestigial 'polite AI' transition phrases (e.g., 'Moving on to...', 'It is crucial to consider') and forcefully substitute them with dense 'Logical Connectors' that natively utilize the content's momentum.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
