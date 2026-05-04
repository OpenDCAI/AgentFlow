# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - **Preserve the real user goal.** The synthesized question must always ask for translation as the primary task, even when the item contains locally acceptable synonyms that are globally inconsistent. First write the instruction exactly as a user would phrase it, then verify that the requested output remains source-aligned translation, and finally remove any wording that accidentally invites summarization, explanation, or problem solving. For example, a math-problem item is only valid if the outer instruction still clearly requests translation and the gold answer is the translated problem, not the solution.
  - **Make the target capability unavoidable.** The question should be constructed so that an agent cannot produce the best answer without demonstrating terminology consistency across documents. First identify the minimum cue that activates the capability, then ensure that cue materially changes the output, and finally keep the sample only if removing the cue would simplify the task. As an edge case, if a repeated term appears only once in the final text, it cannot test terminology consistency and should be rewritten.
  - **Keep the scoring rule explicit and external.** Write the item so that success or failure can be judged from the final output and the recorded trajectory, not from hidden author intent. First define what must remain unchanged, what must be transformed, and what must be inferred from context, then encode those requirements in the prompt or environment, and finally ensure that a reviewer could verify them line by line. A good example is a rule-constrained translation where date format, currency conversion, and URL preservation are all visible in the output.
  - **Serialize a faithful trajectory.** The JSON trajectory must reflect the actual exploration path that led to the sample, not a made-up reasoning story added later. First list the decisive observations in the order they were encountered, then pair each with the concrete action it triggered, and finally ensure that the last step directly supports the answer string. For instance, if the agent decided on an idiomatic proverb rendering because it recognized figurative intent, that recognition must appear as an observation before the action that selects the target idiom.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
