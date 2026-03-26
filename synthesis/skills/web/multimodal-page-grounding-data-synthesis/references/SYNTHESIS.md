# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write instructions that reference user-visible interface properties rather than only semantic content. Mention lists, buttons, ordering, fields, tabs, or revealed controls in a way that makes the screenshot necessary. A good pattern is a task where the same text label appears in multiple places but only one visible instance is correct.
  - Ensure the task requires at least one action after the page changes. The agent should need to re-ground after a click, open, or submit step instead of completing everything from the initial screen. This creates a realistic browser-control sequence instead of a one-shot click exercise.
  - Couple the question to the live page state rather than to a hidden annotation. The answer path should emerge from what the agent can currently see and inspect. As an edge case, if the HTML contains off-screen duplicates, the instruction should still be satisfiable using visible context.
  - Keep the endpoint concrete and easy to validate. The final state can be a forwarded message, a clicked result, a selected filter, or another visible interface outcome. This keeps grading crisp while still testing grounded multimodal control.

* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
