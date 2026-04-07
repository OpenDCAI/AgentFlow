# Phase 3: Data Synthesis Instructions
* **Question Generation Rules:**
  * **Phrase the task as one coherent summary request over an oversized source.** The prompt should clearly require a single readable output over the whole document, not a collection of chunk summaries. This keeps the evaluation target aligned with real book- or report-length summarization. An edge case is allowing sectioned summaries; if so, the sections must still read as one coherent whole.
  * **Seed the source with long-distance coherence hazards.** Prefer documents containing recurring entities, time shifts, delayed causes, or later sections that reinterpret earlier ones. These are the structures that expose chunk-boundary failure. Without them, the summary will not meaningfully test long-form coherence.
  * **Bias question wording toward readability, continuity, and salience.** Do not ask only for “coverage” or “compression.” Ask for a summary that remains understandable to a reader who has not seen the source. This encourages the agent to preserve connective tissue, not merely facts.
  * **Require the answer to be one self-contained summary.** Even if the underlying trajectory used hierarchical merging or incremental updating, the final answer should be presented as one polished text. This mirrors the actual user-facing task. A list of intermediate summaries should never be the target answer.
  * **Write the trajectory to expose merge and compression decisions.** The real exploration path should show when chunks were summarized, when summaries were merged, when a running summary was updated, and when content was compressed. This is critical because the capability lives in those transitions. A trajectory that only logs document reading but not merge behavior is insufficient.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
