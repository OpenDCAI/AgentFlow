# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Draft the revision using a 'Staged Sub-Agent' logic: first, act as an 'Editor' to create a localized Edit Plan (Section, Anchor, Action); then, act as a 'Writer' to execute ONLY those actions. This prevents the creative drift that occurs when planning and writing are unified in a single loose pass. For example, if adding a 'staffing' detail, strictly insert it at the pre-determined Anchor sentence rather than re-organizing the whole 'Operations' chapter.
  - Implement 'In-Text Citation Restoration' as a mandatory final pass. After drafting the revision, scan the text for any 'Claims' that were preserved from Turn 1 and manually re-insert their original numeric markers. This prevents the 'Citation Drift' identified in benchmark failures like Case 2. A concrete rule: for every paragraph that was modified but not deleted, the density of [Bracketed Citations] must remain constant.
  - Apply 'Multi-Standard Presentation Auditing' to the final generation. Check the output against the 10-point presentation rubric (Table 5 of the research), ensuring that Turn t maintains the 'Legibility' (p3) and 'Parallelism' (p4) achieved in Turn t-1. If a reformatting pass turned a clean Markdown table into a messy list, you must revert and re-synthesize using the 'Tabular-First' strategy from the Synthesis skill.
  - Conduct a 'Cumulative Intent Check' before outputting the final report: read the draft alongside the full history of user feedback turns. Check for 'Supersession' (e.g., Turn 2 asked for a 'formal' tone, Turn 4 asked for 'casual'). If a conflict exists, prioritize the *most recent* turn, but for non-conflicting goals (e.g., Turn 2 wanted a table, Turn 4 wanted a summary), ensure BOTH are represented in the final synthesized artifact.
  - Perform an 'Oracle Coverage Verification' as the last step: count the satisfied checklist items. If the count has decreased relative to the previous turn (a Break Rate > 0), you must identify the 'lost' content and surgically restore it using the 'Contextual Text Restoration' skill. This ensures that the agent's performance follows an 'upward-only' coverage trajectory, effectively reaching toward the Oracle-level performance metrics.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
