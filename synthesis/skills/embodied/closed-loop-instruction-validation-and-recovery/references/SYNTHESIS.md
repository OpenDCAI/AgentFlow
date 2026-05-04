# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Generate Repetitive Loop Distractor Contexts: Feed previous memory strings showing triple-failures and prompt finding the escape vector.
  - Develop History-Aware Recovery Injections: Force generation tokens specifying exactly which physical parameter (offset distance, grip strength) adapts based on immediate simulated feedback strings.
  - Construct Execution Trace Audits: Present parsed data files containing spatial coordinates + time steps, interrogating the model to evaluate process fidelity.
  - Synthesize Mission Delivery Verifications: Formulate asynchronous wait challenges querying, 'Is the task ready for closure?' demanding logical confirmation relying exclusively on post-action status checks.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
