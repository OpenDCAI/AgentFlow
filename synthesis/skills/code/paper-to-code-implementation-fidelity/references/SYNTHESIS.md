# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer 'Asymmetric Refinement Tasks' by providing an initial 'Incorrect' code block that contains a subtle semantic flaw (e.g., a missing term in a formula or a wrong sign in a gradient calculation) alongside a 'High-Level Failure Signal'. Success is awarded when the agent uses the 'Exploration' tools to compare the code against the paper LaTeX and implement the surgical correction based on hierarchical diagnostic feedback.
  - Incorporate 'Implicit Dependency stressors' by describing a methodological goal that relies on a specific hyperparameter or standard library naming convention found only in the repository's 'Settings' or 'Related Work' section. The question rewards the agent for identifying the 'Domain Secret' (T3) through repository search before committing to the implementation. This forces the agent to demonstrate contextual discovery over simple prompt-following.
  - Implement 'Multimodal Artifact Lures' where the correct logic requires combining information from a LaTeX equation, a block diagram in a PDF, and a provided code 'TODO' comment. The instructions should use divergent naming (e.g., math uses $P_{max}$ while code uses `top_prob`) to compel the agent to perform a 'Symbolic Alignment' pass. The synthetic task should explicitly penalize implementations that use the literal mathematical symbol if it conflicts with the repo's established camelCase or snake_case styles.
  - Require the final output JSON to include a 'Scientific Traceability Matrix' in the trajectory that tracks the implementation status of all key paper requirements (e.g., Eq 1: Implemented, Eq 2: Implemented). Each interactive turn should update this matrix to show the agent's awareness of the research context. A specific requirement is: 'Every code replacement block must be accompanied by a justification citing the specific paper section it aligns with.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
