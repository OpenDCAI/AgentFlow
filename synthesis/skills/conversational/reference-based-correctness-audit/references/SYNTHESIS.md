# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Structure the user prompt as an 'Official Audit Request' supplying both a 'Reference Solution/Rubric' and an 'Assistant Candidate'. Clearly delineate the two texts so the synthesized logic distinctly recognizes the ground truth standard vs the target evaluation subject.
  - Embed 'Plausible Error Traps' within the candidate's response. For factual/math inputs, interweave a highly common human mistake (e.g., using Gross instead of Net). For behavioral inputs, interweave a subtle passive-aggressive slight hidden in formal vocabulary.
  - Incorporate 'Axis-Specific Constraint Nudges' in the audit prompt when synthesizing fuzzy logic cases (e.g., 'Pay special attention to whether the doctor was distracting'). This instructs the model to prioritize a specified facet in its internal multi-dimensional classification trace.
  - Include a 'Chain-of-Thought (CoT) Requirement' mapped into the output answer key. The synthesized JSON must contain an 'audit_rationale' field where the agent explicitly breaks down the comparison line-by-line before yielding the aggregate [[Correct]] / [[Borderline]] / [[Incorrect]] output.
  - Design the final evaluation to strictly necessitate the reference. Synthesize obscure constraints or hyper-modern organizational policies (e.g., a specific 2024 compliance mandate) ensuring the agent absolutely cannot rely on training-data priors to grade the interaction successfully.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
