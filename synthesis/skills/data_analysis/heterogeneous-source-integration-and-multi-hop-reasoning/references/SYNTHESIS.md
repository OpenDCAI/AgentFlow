# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write prompts so that no single file contains the answer directly. The question should require at least one bridge step, such as combining a metric table with a rule document or comparing outputs from several analytical files. This creates the “connect the dots” behavior the user wants.
  - Keep the final answer format compact and objective. Good outputs are numbers, names, ranked items, or short structured strings because the complexity already lives in the intermediate chain. An edge case to avoid is forcing long free-form justifications that blur whether the multi-hop reasoning was actually correct.
  - Use heterogeneous evidence types deliberately. At least one source should be structured and at least one source should add contextual meaning through text, reference codes, or alternative structure. This encourages robust agents that can move between tabular computation and contextual grounding.
  - Make the trajectory expose the hops explicitly. The synthesized JSON should show where the agent extracted the first clue, how it converted that clue into an intermediate artifact, and how it used that artifact in the next source or computation. Clear hops make this capability learnable rather than opaque.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
