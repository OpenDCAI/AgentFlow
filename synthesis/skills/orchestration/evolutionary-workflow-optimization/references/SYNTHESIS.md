# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'Outcome-to-Policy' challenges where the user provides a set of failed historical trajectories (e.g., 'Reports of previous mission failures') and asks the agent to 'Audit the workflow and update the decision policy to prevent these outcomes.' This forces the model into a meta-analysis state where it must translate raw performance signs into structural or linguistic mutations of its own supervisor prompt. Do not provide the fix; provide the failure logs.
  - Design 'Adaptive Recalibration' prompts where a human-in-the-loop dashboard is presented with a high-uncertainty state (e.g., 'Low-confidence radar data') and the user asks the agent to 'Optimize the triage threshold for this specific scenario.' This tests if the agent can perform dynamic, context-specific parameter tuning. To elevate difficulty, specify a multi-objective constraint like 'Maximise population reach while keeping false alarms below 5%,' pushing the model toward Pareto-frontier reasoning.
  - Incorporate a 'Performance Gap' trap where an initial analytical model (e.g., a simple Forecaster) is insufficient to provoke action, requiring the addition of an 'Operational Response' layer. The instructions should be abstract (e.g., 'Close the gap between prediction and response'), mandating that the agent discover the need for a 'Coordination Agent' or 'Routing Agent' to translate forecasts into actionable alerts. This successfully audits the 'Decision Intelligence' vs 'Analytical Intelligence' transition.
  - Draft requests using 'Layman Strategic Cues' such as 'tune the agent so it doesn't get tricked again,' 'improve our lead time by learning from last year's storm,' or 'figure out which model is messing up the plan.' This aggressively tests the agent’s translation layer, proving it can map a casual executive request for 'preparedness' to formal Reinforcement Learning, Bayesian Calibration, or Coalitional Attribution algorithms.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
