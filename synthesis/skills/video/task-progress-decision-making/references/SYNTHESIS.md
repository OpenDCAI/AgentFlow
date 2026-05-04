# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Construct 'Comparative Rubric-Based Queries' that ask the agent to justify a specific score across multiple professional dimensions. Use templates like: 'Please provide scores (1,2,3,4,5) for each metric: Flow of operation, Tool handling, and Overall performance, citing specific timestamps for each.' This forces the agent to (1) parse the video, (2) apply the rubric, and (3) verify with evidence.
  - Generate 'Safety-Critical State Verification Tasks' that require assessing if a procedural constraint was achieved before a transition. Formulate questions like: 'Using Strasberg’s guidelines for the Critical View of Safety, has the agent achieved a score of 2 for structure identification before the clip ends?'. These questions mandate that the agent performs a 'Protocol Audit' against the visual state.
  - Implement 'Forward-Reasoning Procedure Forecasting' where distractors represent plausible but incorrect next steps based on protocol violations. First, make wrong options compatible with common sense but logically incorrect based on professional safety rules (e.g., 'prepare to cut' before 'confirm two structures'). This tests if the agent possesses 'Technical Discipline' rather than just superficial habit prediction.
  - Design 'Next-Action Optimization Challenges' tasking the agent to identify an inefficiency in the current workflow and propose a corrective step. Formulate prompts like: 'Identify one movement at T=50s that increased technical risk and suggest the correct next step to remediate it.' This secures the link between procedural observation and actionable engineering/clinical feedback.
  - Apply 'Format-Strict Chronological Mapping' in the ground truth answer where the procedural summary is coupled with explicit phase timestamps. You must ensure the response is concise and mathematically grounded: 'Phase 1: [T1-T2], Action [X]; Phase 2: [T2-T3], Action [Y].' This establishes a standardized metric for evaluating sequential planning and progress tracking accuracy.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
