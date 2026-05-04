# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Write prompts that preserve the original bug semantics but hide easy memorization handles. The issue statement should still describe the real behavioral failure, while the repository context should present it through renamed identifiers, altered helper boundaries, or refactored control flow. This forces reasoning over behavior rather than over remembered surface form.
  - Tell the synthetic story from the transformed repository’s perspective. The question should never mention that the code was transformed for evaluation purposes. Instead, it should look like a normal issue report in a codebase whose current structure simply happens to differ from known historical versions.
  - Add one shallow similarity lure and one deep semantic clue. The shallow lure might be a similarly named helper or nearby conditional; the deep clue is the failing test or invariant that truly identifies the patch point. This pairing produces high-quality data for distinguishing memorization from semantic repair.
  - Require answers to preserve transformation while fixing behavior. The expected output should show that the agent repaired the transformed code as-is and validated it with transformed tests. This prevents synthetic tasks from rewarding trivial reverse-engineering of the canonical original.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
