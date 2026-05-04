# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write prompts that naturally require several analytical stages. A good task should need discovery, preparation, computation, and validation in sequence, even if each step is individually simple. This creates realistic opportunities for planning and repair.
  - Design the environment so that an initial imperfect plan is plausible. There should be enough ambiguity that a careful agent might need one revision, but not so much chaos that convergence becomes unlikely. For example, near-duplicate files or partially informative previews create healthy pressure for adaptation.
  - Keep the final answer objective. The complexity should live in the workflow, not in an open-ended reporting rubric. Numbers, short strings, or structured outputs are ideal because they make it easier to tell whether repair actually improved the pipeline.
  - Represent the trajectory as plan-execute-observe-revise-complete. The JSON should explicitly show the first plan, the execution evidence, the repair step, and the final completion. That ordered pattern is the essence of this capability.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
