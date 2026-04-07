# Phase 3: Data Synthesis Instructions
* **Question Generation Rules:**
  * **Force the answer to depend on multiple documents.** Write the question so that no single document can satisfy it on its own. This is the first and most important design constraint for the skill. A practical check is whether each document contributes a different slot in the reasoning chain.
  * **Choose a clear integration operator.** Decide whether the task should require comparison, ranking, grouping, temporal trend analysis, or citation-chain construction, and write the question to foreground that operator. This makes scoring easier and prevents accidental drift into vague open-ended QA. An edge case is a question that secretly requires two operators; if so, state both explicitly.
  * **Make distractors structural, not random.** Use semantically similar documents that share domain vocabulary and nearby fields so that the challenge comes from real corpus structure. This better simulates deep document work than inserting unrelated noise. A good example is multiple annual reports that all contain the same metric names for different companies or years.
  * **Require a normalized answer format.** Ask for a ranked list, grouped JSON object, trend statement, or citation list rather than a vague free-form paragraph whenever possible. This keeps evaluation deterministic and encourages the agent to perform explicit integration. If a narrative answer is allowed, require the key conclusion in the first sentence.
  * **Derive the trajectory from the genuine multi-document path.** Log each evidence collection step, each normalization step, and the final integration step in the order they actually occurred. This yields training data that teaches the agent how to think over multiple files rather than merely what the final answer should be. A concrete example is showing that the agent first built a three-row year-value table and only then inferred the trend.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
