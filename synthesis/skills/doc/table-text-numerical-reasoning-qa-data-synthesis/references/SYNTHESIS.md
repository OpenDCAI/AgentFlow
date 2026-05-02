# Phase 3: Data Synthesis Instructions
* **Question Generation Rules:**
  * **Require at least one numeric reasoning operator.** Write questions that force subtraction, addition, ratio estimation, thresholding, trend analysis, extremum selection, or grouped comparison over grounded values. This is what makes the task about quantitative reasoning rather than direct lookup. A simple way to test this is to ask whether a single copied cell could answer the question; if yes, redesign it.
  * **Bind the question to metric, unit, and period explicitly.** Mention the reporting period, entity, and measurement name in the question so the answer can be scored deterministically. This sharply reduces ambiguity in financial and scientific documents. An edge case is a metric that appears both quarterly and annually; the wording must force one interpretation.
  * **Use both text and structure when possible.** Prefer examples where prose, tables, footnotes, or chart layout each contribute something necessary, because those cases better reflect realistic document work. This also makes the data more robust to superficial retrieval baselines. A practical example is needing the table for values and the note text for units.
  * **Normalize the answer format.** Ask for a scalar with unit, a trend sentence, or a ranked result with explicit ordering, and keep that format consistent across generated items. This improves automatic evaluation and makes the synthetic corpus easier to reuse. If the output is a sentence, require the normalized numeric result near the beginning.
  * **Write the trajectory as a computation ledger.** The real trajectory should show where each operand came from, how it was normalized, and how the final operation was performed. This is more valuable than a polished narrative because it mirrors what a document agent must actually do. A good example is logging “read chart legend,” then “capture top and bottom values,” then “subtract.”
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
