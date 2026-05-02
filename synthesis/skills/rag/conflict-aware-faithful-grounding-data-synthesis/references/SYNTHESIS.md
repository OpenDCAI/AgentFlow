# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - **Ask for answers that can be over-stated.** Generate questions where a model is tempted to broaden, sharpen, or over-assert what the evidence really says. This is especially effective with numbers, ranges, named entities, and causal language. The goal is to make fidelity failures observable, not merely possible.
  - **Design one dominant corruption pattern.** For each sample, inject either a contradiction or a baseless extension pattern that is crisp enough to score. Examples include wrong host city, widened best-interval, or unsupported attribute insertion. Keeping one dominant corruption pattern prevents annotation ambiguity.
  - **Reward correction or narrowing.** Define the expected answer so that the best response either corrects the false claim, narrows the scope, or explicitly notes the conflict before answering. Do not reward stylish prose that still contains unsupported details. Faithfulness should dominate fluency.
  - **Diversify by conflict granularity.** Produce some samples with blatant errors and others with subtle semantic shifts. This prevents the downstream model from learning to catch only obvious mismatches such as misspelled names or swapped years. Subtle drift cases are essential for realistic deployment robustness.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
