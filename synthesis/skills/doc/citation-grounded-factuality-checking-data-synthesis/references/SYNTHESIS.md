# Phase 3: Data Synthesis Instructions
* **Question Generation Rules:**
  * **Generate claims that look plausible before verification.** A good instance should be the kind of answer a user might trust on first read, because that is where grounded fact-checking matters most. This makes the benchmark realistic. A completely absurd hallucination is less valuable than a polished but misgrounded claim.
  * **Anchor the task in available evidence.** Every generated question should come with the grounding passage, cited authority, or retrieved snippet needed to judge support. This keeps the task self-contained and reusable. An edge case is a multi-sentence answer where each sentence should still trace back to a source.
  * **Vary the support relation intentionally.** Include supported, partially supported, unsupported, and contradictory cases so the final dataset does not collapse into a binary positive-only regime. This helps the agent learn fine-grained support reasoning. A particularly useful pattern is a real citation attached to an overstated conclusion.
  * **Keep the answer label normalized.** Use a small, explicit label inventory and make the generated answer or target explanation align to it consistently. This improves evaluation reliability. If free-form explanations are included, the first clause should still contain the normalized support judgment.
  * **Write the trajectory as a verification trace.** The path should show which claim was inspected, which source span was compared, and what support decision followed. This produces agent-like supervision instead of generic explanation text. A good trace often alternates between “inspect evidence” and “update support label.”
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
