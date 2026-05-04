# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write prompts that preserve the real visual complaint in plain language and pair it with the relevant visual artifact. The wording should sound like a normal issue report, such as 'the label is not rendered on message flows' or 'the highlighted bracket uses the wrong category', while still requiring image-grounded interpretation. Avoid revealing the exact component name unless the source issue already did so.
  - Make the execution context include visual reproduction assets. This can be an issue screenshot, a storybook case, a JSFiddle-style snippet, or a visual test target. The agent should need to combine repository reading with rendered-output reasoning rather than solving the issue from static text alone.
  - Introduce local visual distractors instead of unrelated code distractors. For example, include nearby rendering logic for a similar element type or a sibling token class that works correctly. This forces the agent to compare visually neighboring behaviors and identify the precise failed branch.
  - Ensure the answer format expects a concrete visual fix backed by executable verification. The desired output should mention the user-facing rendering correction and the trajectory should show how the agent confirmed it through snapshot, render test, or browser-grounded evidence. This keeps the skill aligned with multimodal front-end maintenance.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
