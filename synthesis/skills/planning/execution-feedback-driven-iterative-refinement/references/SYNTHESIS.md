# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - RefineToolBench Scenario Synthesis: Design user requests that involve 'Implicitly Imperfect' tools, such as an API with an outdated parameter name (`is_id` vs `order_id`) or a script that requires a hidden initialization step not shown in the primary prompt. This structure forces the agent to enter a 'Feedback -> Reflection' loop to discover the real environment constraints. For example, 'Fetch my orders using the onboarding tool' where the tool requires a `user_id` that must be inferred from the user's name.
  - Boolean Syntax and Formatting Traps: Create technical tasks where a common parameter (like a date) must follow a strictly non-standard pattern (e.g., 'YYYY/MM/DD' vs 'YYYY-MM-DD'). The prompt should use the standard format, forcing the agent to fail the first attempt and use the 'Execution Feedback' to learn the local rule. This tests the agent's Error Recognition Rate (ERR) by rewarding those that correctly parse the server's formatting hint.
  - Heuristic Optimization Mazes: Synthesize problems where a single 'greedy' solution performs poorly and a numeric 'Scorer' is provided to guide the agent. The question must ask the agent to 'maximize the score' through trial and error, forcing it to try multiple algorithmic variants (e.g., Greedy vs. Simulated Annealing). Success is defined as a trajectory where the agent achieves a higher score in Step 5 than in Step 1 based on its own refinement.
  - Iterative Parameter Discovery Hooks: Formulate requests where the agent must 'Probe the tool to see what it needs'. Instead of providing all details, say 'Use the car_data tool to find my vehicle; I'm not sure what the ID is'. This necessitates an initial search -> observe IDs -> fetch details sequence, testing the agent's ability to chain tool outputs into subsequent parameters dynamically.
  - Self-Reflection Structured Output: Mandate that the synthetic QA pair includes a dedicated `<reflection>` or `<thought>` block that specifically analyzes the *difference* between the previous failed observation and the current corrected plan. Use natural language commands like 'Analyze why your last attempt didn't work and then fix it' to ensure the output captures the System 2 internal monologue. This provides clear training signals for the 'Reflection' phase.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
