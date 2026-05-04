# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Bulk-Intent Layman Phrasing: Use everyday language that implies a high-volume, repetitive task without providing a step-by-step loop instruction. Start with phrases like 'get me every...' or 'update all the...' followed by a target noun and a location. For example, 'I need you to go through the whole Salesforce lead list and change everyone's status to Contacted' forces the agent to figure out the iteration logic on its own.
  - Paginated/Scrolling Complexity Injection: Ensure the target data set is spread across multiple pages or requiring significant scrolling to reveal all items. You should design the environment so that the first screen only shows a small fraction of the total set. A concrete question would be: 'There are over 200 items in this table; find every one that has an 'Active' status and copy their emails into this list.'
  - Set-Integrity Constraints: Formulate the prompt to include a specific requirement for 'Completeness' or 'Deduplication' to emphasize reliable coordination. Use words like 'all of them,' 'every single one,' and 'don't miss any.' For instance, 'Take every PDF file from this project folder tree, making sure you don't skip any sub-folders or double-count files that appear in multiple views.'
  - Iterative Logic Distractors: Include 'Planted Distractors' such as items that look similar but should be skipped based on a subtle rule, forcing the agent to maintain focus during the loop. Create scenarios where the agent must 'Skip all entries from 2023' while processing a long list of 2024 entries. This tests if the agent stays vigilant during repetitive actions rather than clicking on autopilot.
  - Success-Verification Anchoring: Design the final answer to require a character-perfect summary or a specific count that can only be obtained through a complete iteration. The 'Answer' should not be a guess; it must be the sum total of the work performed. For example, 'Task Complete: 47 unique invoices processed' ensures that the evaluation captures whether the agent actually finished the whole set.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
