# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Draft technical prose utilizing 'Anchor-First' structuring. Place the immutable fact, citation key, or specific integer into the core of the clause, generating the transition framing explicitly around it to enforce 1:1 fidelity.
  - Implement 'Numerical-to-Qualitative Mapping' accurately. When translating table specs into text, ensure descriptive adjectives flawlessly reflect the supplied units (e.g., matching '5000mAh' to 'expansive battery') without unverified exaggeration.
  - Utilize rigorous 'Genre-Specific Diction' acknowledging attribution correctly. Treat structured metrics as objective measurements ('measured at'), while framing cited papers contextually ('postulates', 'evaluates').
  - Execute a final 'Grounding and Faithfulness Sweep.' Systematically count elements, verify citation names, ensure zero table facts drifted across semantic boundaries, and aggressively prune overlapping 'helpful assistant' hallucinated commentary.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}
