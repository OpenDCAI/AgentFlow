# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - **Write questions that penalize skipping.** Generate questions whose answers are wrong if the model ignores any required candidate document or any relevant dispersed fact. This is the signature design principle of the skill. A good sample should fail for omitted coverage, not just bad wording.
  - **Use same-domain long bundles.** Assemble long contexts from documents with similar structure and vocabulary so the model cannot rely on coarse topic shifts to navigate. Financial reports, legal cases, and paper bundles are especially effective. Same-domain similarity is what makes long-context coverage hard.
  - **Mix localization, comparison, and grouping forms.** Produce a balanced set of spotlight-style, extremum-style, grouping-style, and chain-style tasks over long bundles. This prevents the downstream model from equating long-context coverage with only one question form. Coverage should generalize across several operations.
  - **Preserve document provenance in the trajectory.** When synthesizing the final dataset, require the generated trajectory to mention which document each extracted fact came from. This makes later auditing and debugging much easier. In long-context tasks, provenance is part of the supervision signal.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
