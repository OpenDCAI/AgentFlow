# Phase 3: Data Synthesis Instructions
* **Question Generation Rules:**
  * **Write the control lens into the prompt itself.** State the required frame explicitly, whether it is a 5W1H-style checklist, a meeting query, or an aspect focus. This prevents the task from being interpreted as generic summarization. A good prompt should make it obvious what content belongs and what content does not.
  * **Prefer frames that are easy to audit.** Element lists, named topics, review aspects, and direct user questions are stronger than abstract notions like “relevance.” This makes the final answer easier to score and easier to connect to source evidence. An edge case is allowing a two-part frame, such as “focus on cost and timeline only,” which is acceptable if both parts are concrete.
  * **Seed the source with plausible off-frame detail.** Include enough attractive background material that a weak summarizer will be tempted to mention it. This produces a more realistic control challenge. A practical example is a meeting transcript with both strategic discussion and casual logistics when the query only asks about staffing decisions.
  * **Constrain answer organization.** Instruct the output to either follow the requested slots explicitly or keep each sentence aligned to one frame item. This sharply improves controllability. If the final answer is free-form, the first sentence should still clearly signal the requested focus.
  * **Build the trajectory around slot filling and pruning.** The real trajectory should show where the agent found evidence for each frame item and which off-frame facts were intentionally excluded. This is more informative than a simple “read then summarize” path. A good example logs “found date,” “found event,” “found result,” then “omit unrelated injury backstory.”
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
