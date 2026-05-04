# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Phrase the task as an evidence-based validation problem, not merely an execution problem. The agent should be asked to determine whether a result was actually reproduced and to justify that determination from logs and outputs. This invites careful checking instead of superficial script running.
  - Provide the environment with explicit entrypoints and requirement structure. A reproduce.sh script, rubric, or checklist of expected outcomes makes the task concretely benchmarkable. The agent should need to connect runtime artifacts back to that structure.
  - Include at least one possible false-positive path, such as stale outputs or partial completion. This creates realistic pressure to verify provenance and completeness. The best synthetic tasks reward skepticism and structured evidence gathering.
  - Require the final JSON to include trajectory steps showing execution, artifact inspection, and requirement-level judgment. The value of this skill lies in the bridge from empirical observation to replication assessment. That bridge should be visible in the generated data.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
