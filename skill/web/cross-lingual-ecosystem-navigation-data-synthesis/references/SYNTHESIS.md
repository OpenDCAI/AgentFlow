# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write the question in the user-facing language you want to test, but place decisive evidence in another language ecosystem. This forces the agent to bridge retrieval and reasoning rather than solve the task inside one language silo. A strong pattern is an English prompt whose answer requires Chinese or other non-English evidence.
  - Exploit name variance, platform fragmentation, and local indexing habits. Cultural artifacts, public figures, and regional institutions are especially useful because they often have mismatched English and native-language footprints. The edge case to avoid is relying on exotic vocabulary alone; the hard part should be navigation and alignment, not obscure translation trivia.
  - Distribute the clue chain across at least two native-language sources or one native-language source plus one bridging source. This encourages the agent to validate rather than trust the first translated hit. For example, a heritage list can verify official status while a biography or entertainment page resolves the other constraint.
  - Keep the answer objectively gradable after normalization. The final output can be an accepted English rendering, a native-script title, or a normalized bilingual form, but the benchmark should define that choice consistently. This keeps evaluation clean while preserving the intended cross-lingual challenge.

* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
