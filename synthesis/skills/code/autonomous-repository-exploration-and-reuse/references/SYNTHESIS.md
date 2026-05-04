# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate prompts pairing a 'High-Level User Intent' with an 'Unfamiliar GitHub Repository', requesting an end-to-end deployment (Setup through Evaluation) or a functional wrapper. Withhold explicit file destinations or fix locations to force search, documentation digestion, and structural mapping flows natively.
  - Incorporate 'Implicit Dependency Traps' by stripping explicit instructions regarding a specific compiler, hardware flag, or pre-trained weight requirement from the documentation. Success implicitly rewards tracing call-stacks and executing compiler logs to reverse engineer the requirement.
  - Design 'Scale Stressors' involving dense 50+ file repositories where the target inference script is nested, enforcing Context Window Stewardship where the agent relies on AST parsing and dependency traces to locate logic instead of random file scanning.
  - Require the final output JSON deliverables to yield a meticulous 'Provenance Synthesis Chain' logging internal step-by-step decisions, such as 'Encountered KeyError -> Traced Module Dependency Graph to parse.py -> Adapted input mapping'. Detailing exactly HOW the agent unknots repository architectures trains dynamic codebase logic reasoning.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
