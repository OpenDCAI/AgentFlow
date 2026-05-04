# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Deploy a 'Mandatory Import Masking' rule where the cursor is placed in a file that does not yet possess an import for the required internal API. This forces the agent to rely on its discovery and inference capabilities rather than looking at the file header for clues. For instance, ask to complete a call to `utils.log_event` in a new module where the `utils` import is entirely absent to test 'zero-declaration' retrieval.
  - Utilize 'Strategic Cursor Positioning' to place the completion target immediately after a cross-file token or keyword. The synthesis engine should identify lines where a developer has starting writing an identifier (e.g., `self.proc...`) and then requires the model to finish the rest of the line based on project-wide matches. This creates high-fidelity 'next-token' and 'single-line' triggers that mirror real IDE autocomplete usage behavior.
  - Incorporate 'First-use Logic Stressors' by selecting target lines that implement a functionality novel to the current file but common in the broader project. The question should reward the agent for identifying that while the current file hasn't used the `auth_gate` before, the global context requires it for the current `POST` handler implementation. Success is defined by the agent reconstructing the call pattern from distant repository knowledge seeds.
  - Engineer 'Representative Context Windows' by providing at least 150-200 files in the environment to ensure the search space is large enough to penalize random scanning. The target API should be nested at least two directories deep from the current file to force the agent to use its 'Repository Structure Audit' and 'Recursive Inventory' logic. This ensures the synthetic data captures the complexity of navigating diverse enterprise-level repository layouts.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
