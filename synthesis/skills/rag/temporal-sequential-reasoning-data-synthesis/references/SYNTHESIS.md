# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - **Use natural timeline language.** Generate questions with wording such as 'before or after', 'what happened earlier', 'over the years', or 'how did it change'. This makes the skill match ordinary user requests. Avoid formal benchmark jargon inside the question.
  - **Distribute timepoints across documents.** Place the relevant dates, quarters, or release events in different documents so retrieval alone is insufficient. Then require an answer that depends on putting them in order or reading them as a sequence. This is the simplest way to synthesize temporal reasoning data.
  - **Include one plausible chronological trap.** Use nearby years, reversed order temptations, or middle-turning-point patterns to make chronology matter. The trap should be realistic rather than arbitrary. For example, a model may confuse publication year with event year unless the sample is designed carefully.
  - **Vary between order, gap, and trend tasks.** Produce a balanced set of samples spanning before/after, temporal offset, and multi-point trend summaries. This prevents the downstream model from equating temporal reasoning with only one surface pattern. A healthy synthetic mix should include both entity answers and concise temporal narratives.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
