# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer 'Complexity Traps' where a naive solution clearly passes sample inputs but fails on secret, maximum-scale test cases. The prompt should provide 2-3 small examples that admit a simple O(N^2) or O(N^3) logic, while the hidden constraints (e.g., N=200,000) strictly mandate an O(N log N) or O(N) approach. This forces the agent to perform deep complexity analysis during exploration. Success is awarded only when the agent identifies the failure on secret cases and refines its code accordingly.
  - Implement 'Language-Sensitive Hard Constraints' by setting time limits that are significantly harder to hit in Python than in C++. For instance, a 0.2s limit for a task with millions of operations creates a scenario where the agent must evaluate the trade-off and likely choose C++. The synthesis should producing two versions of the environment: one with a generous 5s limit (allowing Python) and one with a 0.2s limit (commanding C++ mastery). This ensures the data tests language-level architectural decision making.
  - Incorporate 'Feedback-Required Debugging' by providing an implementation that has a subtle logical error or a common competitive programming mistake (like integer overflow or missing modular arithmetic). The question rewards the agent for using 'WA' or 'RTE' feedback from the judge to identify the bug (e.g., 'Result exceeds 32-bit int limit') and fixing it. This replicates the real-world iterative workflow of contest participants. A concrete trap is an algorithm that works for all cases except when N is a power of two.
  - Require the final output JSON to include a 'Complexity and Insight Ledger' in the trajectory that mapping specific constraints to code choices. The reasoning steps should state: 'Constraint N=10^18 indicates O(log N); therefore, I am implementing Matrix Fast Exponentiation.' This documentation ensures the synthesized data is valuable for training models to explain their deductive process. A requirement is: 'Every major algorithmic choice must be justified by at least one numerical constraint found in the problem description.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
