# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write questions whose clues are individually meaningful but jointly awkward as a search query. The wording should force the agent to try several retrieval angles before the answer space collapses. A good example is a question anchored by role, time, and biographical constraints instead of a near-verbatim title.
  - Ensure the first obvious query fails in a controlled way. It may return too many candidates, the wrong candidate class, or pages that are relevant but incomplete. The edge case to avoid is a misleading question that is actually impossible; the goal is hard-but-solvable persistence, not hidden unanswerability.
  - Design the information path so that at least one reformulation is naturally triggered by retrieved evidence. The agent should learn a better keyword, a narrower entity name, or a more discriminative date range from the environment itself. For instance, an early page might reveal an author’s full name, which then enables a more precise follow-up search.
  - Keep the final answer short and verifiable, but make the route to it multi-turn. The answer should still be easy to grade once found, such as a title, date, or entity name. Avoid open-ended answers because they blur whether the agent failed at retrieval, reformulation, or generation.

* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
