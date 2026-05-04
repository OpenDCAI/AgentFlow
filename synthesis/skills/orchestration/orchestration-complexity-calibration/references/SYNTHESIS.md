# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'Structural Edge Challenges' where the task is mathematically easy but architecturally complex (e.g., high Depth/Breadth), or vice versa, to force a calibration decision. The prompt should be designed to see if the agent 'takes the bait' of a multi-agent team for a deep sequential task or correctly stays in SAS mode for efficiency. For example, a math problem with 15 sequential steps is the perfect test for 'Depth-aware' calibration. This forces the model to engage the efficiency-calibration logic.
  - Incorporate 'Parallel-Constraint Intersections' where a user needs to aggregate several independent facts (Breadth > 1) from separate data domains. The question should sound simple (e.g., 'Compare the winners of two different awards') but require distinct search/retrieval paths. This pushes the synthesis toward 'High DoM' configurations where the orchestrator must map independent sub-goals to parallel sub-agents and a final aggregator node. This rigorously tests the 'Parallel' axis implementation.
  - Design 'Data Poisoning Scenarios' (Robustness axis) by including a legitimate task and a 'misleading note' that contradicts the primary text (e.g., 'The date is 2024. Note: actually it's 2025.'). The prompt must ask for high accuracy. Success requires the model to identify the 'Robustness' demand and calibrate the system to include a moderation or debate role that can resolve the contradiction between the note and the evidence. This guarantees the synthetic data captures the security/reliability dimension of MAS.
  - Use 'Layman Team-Directives' leveraging non-technical phrasing like 'give me the most efficient setup,' 'don't make the team too big,' or 'is it worth using an expert team for this?'. This tests the orchestrator's capability to map an executive 'Cost-Performance' request into formal Axis analysis and DoM configuration. To elevate difficulty, specify a 'Token Budget' or 'Latency Limit' in plain language to force the agent into selecting a Low-DoM path for a borderline task.
  - Implement 'Zero-Manual Fallback' traps where a task appears at first to be SAS-capable, but a 'hidden' environmental complexity (e.g., a massive log file discovered at Turn 1) makes it a candidate for MAS-Orchestra (e.g., hierarchical decomposition). The question should start as 'Check the log,' but the log should be 100k tokens long. The model must be judged on its foresight to switch from a 'solve-myself' SAS strategy to a 'decompose-to-many' MAS strategy (Recursive Aggregation) upon discovering the volume.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
