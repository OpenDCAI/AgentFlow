# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write questions as bundles of complementary constraints whose resolution naturally spans multiple sources. The wording should reward deliberate slot-filling and punish premature guessing. A good pattern is to combine one descriptive clue, one relational clue, and one comparison or ranking clue.
  - Ensure that no single source can satisfy all constraints without outside confirmation. This can be achieved by distributing publication metadata, biographical data, and ranking data across different pages. As an edge case, if a structured encyclopedia page accidentally contains every fact, add or replace one clue so the chain remains necessary.
  - Keep the chain semantically coherent. The required hops should feel like legitimate user reasoning rather than arbitrary scavenger-hunt jumps. For example, moving from an image archive to a roster to a duration table is coherent because each step advances the same entity-tracking objective.
  - Make the final answer concise even if the chain is long. The result can be a title, person name, or formatted pair, but the evidence should be distributed enough that the synthesis step matters. This preserves easy evaluation while still targeting multi-hop web reasoning.

* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
