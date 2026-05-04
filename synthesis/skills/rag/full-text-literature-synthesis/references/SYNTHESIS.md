# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - **Ask about concrete recent findings.** Generate questions about recent results, comparisons, or novel observations that a user could plausibly ask during literature review. Keep the wording natural and focused on an answerable claim. This makes the skill discoverable from layman requests like 'find what the papers say'.
  - **Require section-level evidence.** Design the sample so the answer depends on details commonly found in results, discussion, or body text rather than in the title or abstract. This forces true paper reading behavior. It also reduces contamination from latent model memory.
  - **Reward source-backed uncertainty.** When a question cannot be settled after reasonable retrieval, the expected output should prefer a calibrated 'cannot answer' over a guessed conclusion. This is especially important in scientific domains where plausible wrong answers are dangerous. Uncertainty is a first-class success mode here.
  - **Vary between yes/no, comparative, and option-selection forms.** Produce a balanced mix of answer formats while keeping the retrieval pattern grounded in full-text papers. This prevents the model from overfitting to one exam-style format. A strong literature skill should generalize across several scientific QA styles.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
