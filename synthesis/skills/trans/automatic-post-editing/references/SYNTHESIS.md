# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate prompts with discrete [Source Text] and [Machine Translation Draft] blocks. Synthesize the question so it is clear that the agent's task is comparative refinement rather than original generation. Research shows that explicitly grounding the task in a flawed hypothesis forces the model to perform 'error-awareness' logic. For example: 'Improve this draft using the provided source for accuracy.'
  - Intentionally inject 'High-Frequency Machine Errors' into the synthetic draft. When creating the data seed, modify a correct translation to include errors like word repetition, semantic drift (using a literal for a specialized term), or dropped adjectives. These errors must be specifically correctable by reading the provided source text. For instance, replace 'median age' with 'popular age' in the draft to test technical correction.
  - Embed 'Domain-Sensitive Traps' in the machine draft items. Design synthetic questions where a word in the draft is generally correct but professionally inaccurate (e.g., using 'the guy' for 'the defendant'). The gold answer must show the agent restoring the professional terminology from the source while cleaning up the draft's register. This evaluates the agent's ability to act as an expert post-editor in specific fields like Law or Medicine.
  - Simulate 'Low-Resource LLM Artifacts' in Indic language drafts. Create synthetic drafts for languages like Hindi or Bengali that contain syntax errors common in early-stage LLMs, such as incorrect query intent or awkward phrasing. The gold answer should reflect the human-level verification process seen in benchmarks like IndicMSMarco. This ensures the data reflects the real-world need to clean up Llama-style translation outputs.
  - Serialize the 'Error-Identification-Correction' steps in the JSON trajectory. Every synthetic sample must document the explicit detection of the error in step one, the reference to the source in step two, and the execution of the fix in step three. This provides a clear audit trail proving the agent isn't just generating a new sentence but specifically 'editing' the old one. Step 1: 'Observation: Draft uses general term "आम"; Step 2: Source intent is frequency; Step 3: Correcting to "अधिक बार".'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
