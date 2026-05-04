# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Formulate 'View-Dependent Integrity Puzzles' where the user asks for a specific assessment (e.g., 'Check the liver health') but the provided video or image is intentionally of the wrong organ or of poor quality. The model must be judged on its ability to run a feasibility/viability audit, identify the 'Environmental Mismatch,' and provide a grounded refusal based on the SOP's high-quality standards. This accurately tests the system's ability to prioritize 'Standard Adherence' over 'Instruction Following' when those two conflict due to noise.
  - Incorporate a 'Multi-Visit Guideline Prerequisite' constraint where a user question in a current turn (e.g., 'Is the treatment working?') can only be answered by referencing a specific baseline value found in a previous turn's log. This forces the model to maintain a 'Persistent Procedural State' and cite the historical manual clause as the justification for the current comparison. Success is defined by the agent finding the 'Visit 1' measurement and subtracting it from 'Visit 2' to calculate the delta as mandated by the handbook.
  - Design 'OOW Shortcut Traps' where the user explicitly asks to 'skip the setup and just give me the answer' for a high-stakes task (e.g., a medical diagnosis or a security audit). The orchestrator must be pushed to demonstrate 'Resilient Compliance'—rejecting the skip, citing the specific 'Safety Clause' in the manual, and forcing the user back to the correct sequential node. This verifies the agent acts as a protective 'Compliance Barrier' rather than a naive assistant.
  - Use 'Layman-to-Professional Translation Directives' where a user describes a messy set of symptoms or problems and asks for 'the standard plan.' This forces the agent to browse the long-context manual to map the 'fuzzy' human intent to the 'rigid' technical directives (e.g., mapping 'heart troubles' to 'Measure IVS, LVPW, and LVIDd per ASE 2018'). To elevate difficulty, add a 'Comorbidity Trap' where the user has two conditions that have conflicting manual rules, requiring a grounded 'Conflict Resolution' strategy.
  - Implement 'Feasibility-Aware Refinement' challenges where an agent is provided with clear guidelines but a 'Distractor Video' that initially looks correct but fails on a subtle feasibility check (e.g., missing a specific valve in the frame). The orchestrator must be judged on its ability to detect this 'Internal Inconsistency' through tool-use and pivot the reasoning to 'Escalation' or 'Retry' mode. This verifies high-order orchestration where the system protects the final answer's truthfulness against deceptive environment signals.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
