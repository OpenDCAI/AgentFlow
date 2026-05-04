# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  * Draft the summary from an ordered element skeleton. A reliable order is entity, date if available, event, then result, with light rearrangement only when needed for fluency. This keeps compression anchored to the source’s indispensable information.
  * Use abstraction selectively and only where it preserves fidelity. Paraphrase surrounding phrasing, but keep critical factual relations stable. An important edge case is not softening a death into a generic “incident” because the result is the core fact.
  * Compress supporting detail by asking whether it sharpens the event or clarifies the result. If it does neither, remove or subordinate it. For example, road location may stay if it grounds the incident, while tangential reaction quotes can often be dropped.
  * Perform a final four-element audit on the drafted summary. Check whether each source-supported core element is still present and whether none was hallucinated during paraphrase. If one mandatory element has vanished, revise by restoring it directly rather than broadening the whole summary.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
