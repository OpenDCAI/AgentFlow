# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Implement 'Seed-Based Continuity' by starting the generation with an author-specific identifier tag, implicit genre structural beat, or anchor phrase that conditions all subsequent predictions.
  - Apply 'Syntactic-Lexical Reconstructioning' by weaving the target's specific 'high-attribution tokens' and punctuation habits into the prose.
  - Apply 'Reflexative Re-verbalization' for neutral personas: identify the subjective 'emotional anchor' of a clause and replace it with a 'descriptive anchor' derived from the context, utilizing 'Attribution-as-a-Wrapper' for contested claims.
  - Execute 'Rhythm and Complexity Mirroring' to ensure the final document matches the target's parse-tree and sentence-length histograms, intentionally combining or pruning complex dependency chains to map the persona.
  - Perform a final 'Persona-Consistency Polishing Pass' to surgically remove any vestigial 'social desirability' markers or assistant-voice transitions that survived drafting. Ensure the final answer ends with an in-character narrative beat or professional closure.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
