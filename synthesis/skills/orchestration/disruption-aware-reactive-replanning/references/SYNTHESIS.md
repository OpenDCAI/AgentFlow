# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Develop 'Nominal-to-Disruption' prompts that establish an ongoing objective but inherently trigger a live push event or constraint mid-way (e.g., 'Monitor the deployment roll-out, ensure strict thresholds'). This forces discovery and adaptation logic instead of one-shot passes.
  - Incorporate a 'Cascading Dependency' trap where the disruption of an early resource delays several downstream downstream tasks. The orchestrator must be judged on its ability to propagate this event accurately to recalculate final delivery constraints.
  - Design 'Ambiguous Recovery' puzzles where a dashboard shows a 'Green' status but the live telemetry event shows 'Red/Failed'. The orchestrator must prioritize the fresh disruption evidence over static historical benchmarks.
  - Use 'Proactive Adaptation' cues by providing early warning events (e.g., 'Power outage in 10 mins') forcing the agent to structurally replan immediate nodes before the absolute resource failure completely breaks the active session.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
