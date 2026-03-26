# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - **Write answerable-looking questions.** Generate questions that look completely ordinary and are phrased as if a competent retriever should be able to solve them. Avoid wording that hints the task is unanswerable. The strength of the sample comes from hidden insufficiency, not overt cues.
  - **Use evidence gaps that are semantically meaningful.** Create absence by removing the exact supporting slot while preserving surrounding context that looks promising. Examples include missing year values, missing entity occurrences, or missing relation edges. This yields realistic abstention tasks rather than arbitrary blank contexts.
  - **Reward clean refusal, not apologetic essays.** The expected answer should be short, direct, and standardized so downstream evaluation is robust. Do not ask for speculative fallback advice when the evidence is missing. The training target is evidence-bounded refusal.
  - **Vary the insufficiency pattern.** Produce samples where evidence is absent because of non-existence, incompleteness, or broken bridging across documents. Keeping these variants together prevents the model from equating rejection with only one surface form. An important edge case is a multi-hop question whose individual facts exist but whose required bridge does not.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
