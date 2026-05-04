# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer 'Open-Ended Score Optimization' prompts where the user asks for the 'highest possible score' rather than a binary pass. The wording should emphasize that the true optimum is unreachable and that 'any improvement is a win.' This forces the agent into a long-horizon mindset where it must constantly seek the next 1% gain. For example, 'Improve the current logistics plan to reduce total distance as much as possible within the 4-hour window.'
  - Implement 'Asymmetric Input Scaling' in the synthesis environment where small cases are trivial but full cases require O(N log N) or better heuristics. The prompt should provide small samples that work with simple loops, while the hidden evaluation set contains 100,000+ entities. Success is only awarded if the agent identifies this scale during exploration and implements a hardware-efficient approach. This creates realistic difficulty for testing the agent's architectural foresight.
  - Include 'Multi-Objective Friction' by providing scores that weighted competing factors, such as 'rectangle area' vs 'rectangle count penalty'. The question rewards the agent for correctly balancing these objectives in its evaluation function. This forces the agent to move beyond single-metric optimization into the 'Engineering' space where trade-offs must be managed. A concrete synthesis task is one where focus on Objective A too much leads to a catastrophic penalty in Objective B.
  - Require the final output to include a 'Score Trajectory Log' in the trajectory that documents every public test score achieved. The JSON should record: 'Run 1 Score: 1200, Run 2 (with SA) Score: 4500, Run 3 (with tuned Temp) Score: 5100.' This provides high-density signal for reward models to distinguish between 'thinking about optimization' and 'actually achieving it.' A specific requirement is: 'Every major algorithmic pivot must be justified by the preceding numerical result.'
  - Design 'Neighborhood Operator Traps' where standard moves fail to cover the entire search space. For instance, a problem where simply swapping two nodes leaves the agent stuck in a local minimum unless it implements a 'node-ejection' move. The question rewards the agent for identifying search stagnation and proposing a more diverse neighbor strategy. This tests the agent's 'deductive ideation' ability, forcing it to analyze the 'topology' of the problem mathematically.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
