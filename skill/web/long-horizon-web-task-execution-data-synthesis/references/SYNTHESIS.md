# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write instructions that contain multiple conjunctive requirements or ordered subgoals. This creates pressure on working memory and execution discipline. A useful pattern is combining sorting, filtering, navigation, and final confirmation in one compact user request.
  - Design the path so that partial success is common but insufficient. The agent should often find near misses that satisfy some constraints but not all. This makes the benchmark sensitive to dropped requirements and premature stopping.
  - Include at least one workflow phase shift. Examples include moving from list view to detail view, from inbox to compose panel, or from search to checkout-like confirmation. The shift forces the agent to maintain intent across changing page states.
  - Keep the final answer or outcome easy to check even if the path is long. A selected item, a sent/forwarded action, or a fully validated product choice works well. This preserves robust evaluation while still targeting long-horizon execution.

* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
