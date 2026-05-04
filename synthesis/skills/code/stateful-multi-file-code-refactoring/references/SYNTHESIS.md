# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Construct multi-hop prompts that describe structural transformations rather than simple bug symptoms. Use language like 'Encapsulate these variables into a class', 'Refactor the data fetching logic to a separate service', or 'Rename this core function and its 15 internal usage sites'. This phrasing forces the agent into a stateful, architectural mindset. The question must be answerable through exploration but should not provide a 'list of files' to edit.
  - Design 'Compositional Traps' by choosing refactors that create temporary logical inconsistencies. For example, a task might require changing a function's return type in one file and its consumer's handling logic in another. The agent must successfully navigate the 'broken' midpoint where only one of these has been applied. Success is defined by the agent's persistent pursuit of the objective through this messy intermediate state.
  - Embed 'Namespace Friction' by choosing symbols with high collision rates or common names across the repository. A task might ask to refactor a function named 'validate' in a repo with 10 different 'validate' methods. This forces the agent to use 'Navigation' and 'Symbol Grounding' rather than blindly applying global search-and-replace. The reward and evaluation should focus on the agent's ability to distinguish relevant from irrelevant symbols.
  - Require the final synthetic JSON to reflect 'Action Tracking' in the trajectory steps. The trajectory should includes notes like 'I have now patched 3 of 5 locations' and use current observations to confirm the state change. This provenance is what makes the synthesized data valuable for training agents to survive long context windows and large codebases. A specific instruction might be: 'Your reasoning must explicitly record which cross-file dependencies are still pending implementation.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
