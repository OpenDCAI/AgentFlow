# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Hierarchical Goal Encoding: Design instructions that focus on the 'Leaf Function' (the final goal) while ignoring the 'Branch Hops' (the path to get there). Use phrases like 'find the setting to...', 'figure out where to...', or 'search the app until you find...'. For example, 'Find the version number of this app' forces the agent to navigate the 'About' section which is usually hidden three layers deep.
  - Semantic-Ambiguity Injection: Formulate the prompt using layman terms that could map to multiple different menu labels, forcing the agent to evaluate the hierarchy semantically. Use wording like 'the help area' which could be 'Customer Service', 'Support', or 'FAQ' in the app. This requires the agent to probe the different branches to find the one that truly contains the human-centered goal.
  - Backtracking-Incentive Seeding: Construct environments where the most obvious semantic path is a 'Trap' that leads to a similar but incorrect function. You should ensure the true target is in a more obscure but logically sound sub-menu, rewarding agents that backtrack and re-evaluate. For instance, place a 'Feedback' button on the homepage, but make the 'Contact Specialist' function reachable only through Settings -> Help.
  - Visual-Only Icon Constraints: Specify tasks that involve interacting with symbolic elements that lack a text label, such as a 'Gear' icon or a 'Three-Dash' hamburger menu. You must phrase the question so the agent must ground its search in visual symbols: 'Go to the gear icon and find the display settings'. This tests 'Icon Understanding' alongside hierarchical navigation.
  - State-Aware Discovery Verification: Design the final answer to include a specific detail that is only visible on the leaf-level page, such as a version number or a specific toggle status. This ensures the evaluation rigorously proves the agent navigated the entire hierarchy rather than just guessing completion. For example: 'Task Complete: Verified that auto-play is currently set to WiFi-only in the deep settings sub-menu'.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
